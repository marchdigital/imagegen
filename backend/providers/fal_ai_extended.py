# backend/providers/fal_ai_extended.py

import os
import json
import base64
import httpx
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

class FalModel(Enum):
    """Supported Fal.ai models with their endpoints"""
    # Existing models
    SDXL = "110602490-sdxl-turbo"
    STABLE_DIFFUSION = "110602490-stable-diffusion"
    FLUX = "fal-ai/flux/dev"
    
    # New models
    WAN_25_PREVIEW = "fal-ai/wan-25-preview/image-to-image"
    QWEN_IMAGE_EDIT = "fal-ai/qwen-image-edit-plus"
    PRODUCT_PHOTOSHOOT = "easel-ai/product-photoshoot"

@dataclass
class ImageInput:
    """Represents an image input for models"""
    data: Union[str, bytes]  # Base64 or bytes
    url: Optional[str] = None
    path: Optional[str] = None
    
    def to_fal_format(self) -> Dict[str, Any]:
        """Convert to Fal.ai API format"""
        if self.url:
            return {"url": self.url}
        elif self.path:
            with open(self.path, "rb") as f:
                data = base64.b64encode(f.read()).decode('utf-8')
                return {"data": f"data:image/png;base64,{data}"}
        elif isinstance(self.data, bytes):
            data = base64.b64encode(self.data).decode('utf-8')
            return {"data": f"data:image/png;base64,{data}"}
        else:
            return {"data": self.data}

class FalAIProvider:
    """Extended Fal.ai provider with support for new models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://queue.fal.run"
        self.headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger("fal_ai_provider")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[FAL] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def generate_wan25_preview(
        self,
        prompt: str,
        image: ImageInput,
        reference_images: Optional[List[ImageInput]] = None,
        image_influence: float = 0.75,
        style_strength: float = 0.5,
        aspect_ratio: str = "original",
        output_size: str = "1024x1024",
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        hd_output: bool = False,
        auto_enhance: bool = False
    ) -> Dict[str, Any]:
        """
        Generate with WAN-25 Preview model for advanced image-to-image
        """
        # Parse output size
        width, height = map(int, output_size.split('x'))
        
        # Prepare request payload
        payload = {
            "prompt": prompt,
            # add alternate prompt fields for compatibility
            "text_prompt": prompt,
            "caption": prompt,
            "image": image.to_fal_format(),
            "image_influence": image_influence,
            "style_strength": style_strength,
            "width": width,
            "height": height,
            "guidance_scale": guidance_scale,
            "num_inference_steps": 20,
            "enable_hd": hd_output,
            "enable_enhancement": auto_enhance
        }
        
        # Add reference images if provided
        if reference_images:
            payload["reference_images"] = [
                img.to_fal_format() for img in reference_images
            ]
        
        # Add seed if specified
        if seed and seed != -1:
            payload["seed"] = seed
        
        # Handle aspect ratio
        if aspect_ratio != "original":
            aspect_ratios = {
                "1:1": (1024, 1024),
                "16:9": (1920, 1080),
                "9:16": (1080, 1920),
                "4:3": (1024, 768),
                "3:2": (1152, 768)
            }
            if aspect_ratio in aspect_ratios:
                payload["width"], payload["height"] = aspect_ratios[aspect_ratio]
        
        # lightweight debug (avoid logging images)
        try:
            self.logger.info(f"WAN-25 payload keys: {sorted([k for k in payload.keys() if k not in ['image','reference_images']])}; prompt_len={len(prompt or '')}")
        except Exception:
            pass
        return await self._submit_request(FalModel.WAN_25_PREVIEW.value, payload, wrap_input=True)
    
    async def edit_with_qwen(
        self,
        image: ImageInput,
        instruction: str,
        edit_type: str = "auto",
        mask: Optional[ImageInput] = None,
        edit_strength: float = 0.8,
        coherence: float = 0.9,
        auto_mask: bool = True,
        preserve_style: bool = False
    ) -> Dict[str, Any]:
        """
        Edit images with Qwen Image Edit Plus model
        """
        payload = {
            "image": image.to_fal_format(),
            "prompt": instruction,
            "text_prompt": instruction,
            "instruction": instruction,
            "edit_mode": edit_type,
            "strength": edit_strength,
            "coherence_factor": coherence,
            "auto_detect_region": auto_mask,
            "preserve_original_style": preserve_style
        }
        
        # Add mask if provided
        if mask:
            payload["mask"] = mask.to_fal_format()
        
        # Edit type specific parameters
        edit_params = {
            "object_removal": {
                "inpaint_mode": "remove",
                "edge_blend": 0.2
            },
            "object_replacement": {
                "inpaint_mode": "replace",
                "context_aware": True
            },
            "background_change": {
                "segment_mode": "background",
                "blend_edges": True
            },
            "style_transfer": {
                "style_preservation": 0.3,
                "content_preservation": 0.7
            },
            "color_adjustment": {
                "color_mode": "adaptive",
                "preserve_luminance": True
            }
        }
        
        if edit_type in edit_params:
            payload.update(edit_params[edit_type])
        
        return await self._submit_request(FalModel.QWEN_IMAGE_EDIT.value, payload)
    
    async def generate_product_shots(
        self,
        product_images: List[ImageInput],
        product_category: str,
        product_description: str,
        scene_type: str = "studio",
        background_style: str = "clean_white",
        lighting_setup: str = "soft_box",
        props: Optional[str] = None,
        remove_background: bool = True,
        preserve_shadows: bool = False,
        color_palette: Optional[List[str]] = None,
        reflection_intensity: float = 0.3,
        output_format: str = "square",
        resolution: str = "1024",
        batch_size: int = 4,
        add_watermark: bool = False,
        generate_variations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate product photography with the Product Photoshoot model
        """
        # Format mapping
        format_dimensions = {
            "square": (1024, 1024),
            "portrait": (768, 1024),
            "landscape": (1024, 768),
            "banner": (1920, 1080),
            "story": (1080, 1920)
        }
        
        width, height = format_dimensions.get(output_format, (1024, 1024))
        
        # Scale based on resolution
        if resolution == "1920":
            scale = 1.875
        elif resolution == "3840":
            scale = 3.75
        else:
            scale = 1.0
        
        width = int(width * scale)
        height = int(height * scale)
        
        # Prepare payload
        payload = {
            "product_images": [img.to_fal_format() for img in product_images],
            "category": product_category,
            "description": product_description,
            "scene_type": scene_type,
            "background": {
                "style": background_style,
                "remove_original": remove_background,
                "preserve_shadows": preserve_shadows
            },
            "lighting": {
                "setup": lighting_setup,
                "intensity": 1.0,
                "color_temperature": "neutral"
            },
            "output": {
                "width": width,
                "height": height,
                "format": "png",
                "quality": 95
            },
            "batch_size": batch_size,
            "variations": generate_variations,
            "effects": {
                "reflection_intensity": reflection_intensity,
                "add_watermark": add_watermark
            }
        }
        
        # Add optional parameters
        if props:
            payload["props"] = props.split(",")
        
        if color_palette:
            payload["color_palette"] = color_palette
        
        # Scene-specific settings
        scene_settings = {
            "studio": {
                "background_blur": 0,
                "shadow_intensity": 0.5
            },
            "lifestyle": {
                "context_blend": 0.7,
                "natural_lighting": True
            },
            "outdoor": {
                "environment": "natural",
                "time_of_day": "golden_hour"
            },
            "minimalist": {
                "simplicity": 1.0,
                "negative_space": 0.6
            },
            "luxury": {
                "premium_finish": True,
                "glamour_lighting": True
            }
        }
        
        if scene_type in scene_settings:
            payload["scene_settings"] = scene_settings[scene_type]
        
        return await self._submit_request(FalModel.PRODUCT_PHOTOSHOOT.value, payload)
    
    async def _submit_request(self, model: str, payload: Dict[str, Any], wrap_input: bool = False) -> Dict[str, Any]:
        """Submit request to Fal.ai API and handle response.
        Some models expect the body under an `input` key (client libraries do this). Use wrap_input=True to send {"input": payload}.
        """
        self.logger.info(f"Submitting to {model}")
        async with httpx.AsyncClient() as client:
            # Submit to queue
            try:
                body = {"input": payload} if wrap_input else payload
                # send both top-level and input envelope for compatibility
                if wrap_input:
                    body = {**payload, "input": payload}
                submit_response = await client.post(
                    f"{self.base_url}/{model}",
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )
                submit_response.raise_for_status()
            except Exception as e:
                self.logger.error(f"Submit failed: {e}")
                try:
                    self.logger.error(f"Response: {submit_response.text[:500]}")
                except Exception:
                    pass
                raise
            
            # Get request ID
            submit_data = submit_response.json()
            try:
                self.logger.info(f"Submit response keys: {list(submit_data.keys())}")
            except Exception:
                pass
            request_id = submit_data.get("request_id")
            
            if not request_id:
                return submit_data  # Synchronous response
            
            # Poll for results
            status_url = f"{self.base_url}/{model}/requests/{request_id}/status"
            result_url = f"{self.base_url}/{model}/requests/{request_id}"
            
            max_attempts = 60  # 2 minutes with 2-second intervals
            for attempt in range(max_attempts):
                await asyncio.sleep(2)
                
                status_response = await client.get(
                    status_url,
                    headers=self.headers,
                    timeout=10.0
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if status_data.get("status") == "COMPLETED":
                        # Get the actual result
                        result_response = await client.get(
                            result_url,
                            headers=self.headers,
                            timeout=10.0
                        )
                        return result_response.json()
                    
                    elif status_data.get("status") == "FAILED":
                        err = status_data.get('error')
                        self.logger.error(f"Job failed: {err}")
                        raise Exception(f"Generation failed: {err}")
            
            raise TimeoutError("Request timed out after 2 minutes")
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://queue.fal.run/health",
                    headers={"Authorization": f"Key {self.api_key}"},
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

# Helper functions for the FastAPI endpoints

async def process_wan25_request(
    provider: FalAIProvider,
    prompt: str,
    main_image: bytes,
    reference_images: Optional[List[bytes]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Process WAN-25 Preview generation request"""
    
    # Convert main image
    main_img = ImageInput(data=main_image)
    
    # Convert reference images if provided
    ref_imgs = None
    if reference_images:
        ref_imgs = [ImageInput(data=img) for img in reference_images]
    
    # Generate
    result = await provider.generate_wan25_preview(
        prompt=prompt,
        image=main_img,
        reference_images=ref_imgs,
        **kwargs
    )
    
    return result

async def process_qwen_edit_request(
    provider: FalAIProvider,
    image: bytes,
    instruction: str,
    mask: Optional[bytes] = None,
    **kwargs
) -> Dict[str, Any]:
    """Process Qwen Image Edit request"""
    
    # Convert images
    img = ImageInput(data=image)
    mask_img = ImageInput(data=mask) if mask else None
    
    # Edit
    result = await provider.edit_with_qwen(
        image=img,
        instruction=instruction,
        mask=mask_img,
        **kwargs
    )
    
    return result

async def process_product_shoot_request(
    provider: FalAIProvider,
    product_images: List[bytes],
    category: str,
    description: str,
    **kwargs
) -> Dict[str, Any]:
    """Process Product Photoshoot request"""
    
    # Convert images
    imgs = [ImageInput(data=img) for img in product_images]
    
    # Generate product shots
    result = await provider.generate_product_shots(
        product_images=imgs,
        product_category=category,
        product_description=description,
        **kwargs
    )
    
    return result

import asyncio  # Add this import at the top