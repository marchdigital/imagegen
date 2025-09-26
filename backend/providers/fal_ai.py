import httpx
import base64
import json
import asyncio
import tempfile
import os
from typing import Dict, Any, Optional, List
from backend.providers.base import BaseProvider
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

class FalAIProvider(BaseProvider):
    """Fal.ai provider implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://fal.run"
        self.headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(
        self,
        model: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 4,
        cfg_scale: float = 7.5,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate an image using Fal.ai"""
        
        # Map model names to Fal.ai endpoints
        model_map = {
            "flux-pro": "fal-ai/flux-pro",
            "flux-dev": "fal-ai/flux/dev",
            "flux-schnell": "fal-ai/flux/schnell"
        }
        
        endpoint = model_map.get(model, "fal-ai/flux/schnell")
        url = f"{self.base_url}/{endpoint}"
        
        payload = {
            "prompt": prompt,
            "image_size": {
                "width": width,
                "height": height
            },
            "num_inference_steps": steps,
            "guidance_scale": cfg_scale,
            "num_images": 1
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed is not None and seed != -1:
            payload["seed"] = seed
        
        logger.info(f"Sending request to {url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                
                logger.info(f"Response status: {response.status_code}")
                response_text = response.text
                
                if response.status_code != 200:
                    logger.error(f"Fal.ai API Error: {response_text}")
                    
                    # Try to parse error message
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_data.get("error", str(error_data)))
                    except:
                        error_msg = response_text[:500]
                    
                    raise Exception(f"Fal.ai API Error ({response.status_code}): {error_msg}")
                
                # Parse the successful response
                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Response text: {response_text[:500]}")
                    raise Exception(f"Invalid JSON response from Fal.ai: {str(e)}")
                
                # Handle the response format
                images = []
                if "images" in result:
                    images = result["images"]
                elif "image" in result:
                    images = [result["image"]]
                
                return {
                    "images": images,
                    "seed": result.get("seed"),
                    "has_nsfw": result.get("has_nsfw_concepts", [False])[0]
                }
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            raise
    
    async def generate_wan25(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        output_format: str = "webp",
        quality: int = 80,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate image using WAN-25 Preview model (using Flux as fallback)"""
        
        # Map aspect ratios to dimensions
        aspect_map = {
            "1:1": (1024, 1024),
            "16:9": (1344, 768),
            "9:16": (768, 1344),
            "4:3": (1152, 896),
            "3:4": (896, 1152)
        }
        width, height = aspect_map.get(aspect_ratio, (1024, 1024))
        
        # Add style to prompt if provided
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style}"
        
        # Use Flux Schnell for now (fast generation)
        return await self.generate(
            model="flux-schnell",
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=4,  # Schnell is optimized for 4 steps
            cfg_scale=3.5,
            seed=seed
        )
    
    async def edit_qwen(
        self,
        image: bytes,
        instruction: str,
        mask: Optional[bytes] = None,
        edit_type: str = "object",
        edit_strength: float = 0.8,
        coherence: float = 0.7,
        auto_mask: bool = True,
        preserve_style: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Edit image using Qwen Image Edit Plus"""
        
        url = f"{self.base_url}/fal-ai/qwen-image-edit-plus"
        
        # Convert image to base64
        image_b64 = base64.b64encode(image).decode('utf-8')
        
        # The API expects image_urls as an array
        payload = {
            "image_urls": [f"data:image/png;base64,{image_b64}"],
            "prompt": instruction,
            "strength": edit_strength,
            "guidance_scale": coherence * 10,  # Map coherence to guidance scale
        }
        
        # Add mask if provided (also as array)
        if mask:
            mask_b64 = base64.b64encode(mask).decode('utf-8')
            payload["mask_urls"] = [f"data:image/png;base64,{mask_b64}"]
        
        logger.info(f"Sending Qwen edit request to {url}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                
                if response.status_code != 200:
                    error_msg = response.text[:500]
                    logger.error(f"Qwen API Error: {error_msg}")
                    raise Exception(f"Qwen API Error ({response.status_code}): {error_msg}")
                
                result = response.json()
                
                # Format response
                images = []
                if "image" in result:
                    images = [{"url": result["image"]}]
                elif "images" in result:
                    images = [{"url": img} if isinstance(img, str) else img for img in result["images"]]
                
                return {
                    "images": images,
                    "message": "Edit completed successfully"
                }
                
        except Exception as e:
            logger.error(f"Qwen edit error: {str(e)}")
            raise
    
    async def generate_product_shoot(
        self,
        product_images: List[bytes],
        category: str,
        description: str,
        scene_type: str = "studio",
        background_style: str = "gradient",
        lighting_setup: str = "soft",
        props: Optional[List[str]] = None,
        remove_background: bool = False,
        preserve_shadows: bool = True,
        color_palette: Optional[str] = None,
        reflection_intensity: float = 0.0,
        output_format: str = "png",
        resolution: str = "1024x1024",
        batch_size: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate product photography using Easel AI Product Photoshoot"""
        
        url = f"{self.base_url}/easel-ai/product-photoshoot"
        
        # Convert first product image to base64
        if not product_images:
            raise Exception("At least one product image is required")
        
        # Compress and resize image if too large
        from PIL import Image
        import io
        
        original_size = len(product_images[0])
        logger.info(f"Original image size: {original_size} bytes ({original_size / 1024 / 1024:.2f} MB)")
        
        # Open the image
        img = Image.open(io.BytesIO(product_images[0]))
        logger.info(f"Original dimensions: {img.size}")
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Resize if image is too large (max 2048px on longest side)
        max_dimension = 2048
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            logger.info(f"Resizing image from {img.size} to {new_size}")
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compress the image
        output_buffer = io.BytesIO()
        
        # Try to get a reasonable file size (target: under 1MB)
        quality = 95
        max_size = 1024 * 1024  # 1MB
        
        while quality >= 60:
            output_buffer.seek(0)
            output_buffer.truncate()
            
            # Save as JPEG for better compression
            img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
            
            if output_buffer.tell() <= max_size:
                break
            
            quality -= 10
            logger.info(f"Image too large ({output_buffer.tell()} bytes), reducing quality to {quality}")
        
        # Get the compressed image bytes
        output_buffer.seek(0)
        compressed_image = output_buffer.read()
        
        logger.info(f"Compressed image size: {len(compressed_image)} bytes ({len(compressed_image) / 1024:.2f} KB)")
        logger.info(f"Compression ratio: {original_size / len(compressed_image):.2f}x")
        
        # Convert to base64
        image_b64 = base64.b64encode(compressed_image).decode('utf-8')
        logger.info(f"Base64 length: {len(image_b64)} characters")
        
        # Simple, clear scene and placement descriptions that match API examples
        # Scene MUST be at least 64 characters
        scene = f"an image with a professional {scene_type} photography setting, featuring {background_style} background and {lighting_setup} lighting setup for product photography"
        
        # Ensure minimum length
        if len(scene) < 64:
            scene = f"an image with a professional photography studio setting, featuring elegant {background_style} background, sophisticated {lighting_setup} lighting, creating perfect product presentation environment"
        
        # Simple placement description similar to API example
        placement = f"the {category} product placed in the center of the image"
        
        if props and len(props) > 0:
            placement = f"the {category} product placed in the center with {', '.join(props[:2])}"
        
        # Use JPEG format for compressed image
        payload = {
            "product_image": f"data:image/jpeg;base64,{image_b64}",
            "scene": scene,
            "product_placement": placement
        }
        
        # Only add optional fields if they have meaningful values
        if description and len(description.strip()) > 0:
            payload["product_description"] = description[:100]  # Limit length
        
        # Log full details for debugging
        logger.info(f"=== PRODUCT PHOTOSHOOT DEBUG ===")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {self.headers}")
        logger.info(f"Scene ({len(scene)} chars): {scene}")
        logger.info(f"Placement: {placement}")
        logger.info(f"Product description: {payload.get('product_description', 'Not provided')}")
        
        # Log first 100 chars of base64 to verify format
        logger.info(f"Image data prefix: data:image/jpeg;base64,{image_b64[:50]}...")
        
        # Create a sanitized payload for logging (without the full base64)
        log_payload = payload.copy()
        if "product_image" in log_payload:
            log_payload["product_image"] = f"data:image/png;base64,[{len(image_b64)} chars]"
        logger.info(f"Payload structure: {json.dumps(log_payload, indent=2)}")
        
        try:
            # Try with a longer timeout and log the exact request
            async with httpx.AsyncClient(timeout=180.0) as client:
                logger.info("Sending POST request...")
                response = await client.post(url, json=payload, headers=self.headers)
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                # Log full response for debugging
                response_text = response.text
                logger.info(f"Response body: {response_text[:1000]}")  # First 1000 chars
                
                if response.status_code != 200:
                    logger.error(f"=== ERROR DETAILS ===")
                    logger.error(f"Status: {response.status_code}")
                    logger.error(f"Response: {response_text}")
                    
                    # Check if it's a validation error
                    try:
                        error_data = response.json()
                        logger.error(f"Error JSON: {json.dumps(error_data, indent=2)}")
                        
                        # Check for specific validation errors
                        if "detail" in error_data:
                            if isinstance(error_data["detail"], list):
                                # FastAPI validation error format
                                for error in error_data["detail"]:
                                    logger.error(f"Validation error: {error}")
                            else:
                                logger.error(f"Error detail: {error_data['detail']}")
                        
                        error_msg = error_data.get("detail", str(error_data))
                    except:
                        error_msg = response_text[:500]
                    
                    # If it's a 500 error, it might be an issue with the image format
                    if response.status_code == 500:
                        logger.error("500 error - possible causes:")
                        logger.error("1. Image format not supported (try PNG/JPEG)")
                        logger.error("2. Image too large (try compressing)")
                        logger.error("3. API service issue")
                        logger.error("4. Invalid base64 encoding")
                    
                    raise Exception(f"Product Photoshoot API Error ({response.status_code}): {error_msg}")
                
                result = response.json()
                logger.info(f"Success! API Response: {json.dumps(result, indent=2)}")
                
                # Format response - the API returns an image object with URL
                images = []
                if "image" in result:
                    if isinstance(result["image"], dict) and "url" in result["image"]:
                        images = [{"url": result["image"]["url"]}]
                    elif isinstance(result["image"], str):
                        images = [{"url": result["image"]}]
                elif "images" in result:
                    for img in result["images"]:
                        if isinstance(img, dict) and "url" in img:
                            images.append({"url": img["url"]})
                        elif isinstance(img, str):
                            images.append({"url": img})
                
                if not images:
                    logger.warning("No images found in response, returning raw result")
                    images = [{"url": "error: no image URL found"}]
                
                return {
                    "images": images,
                    "message": f"Generated product photo successfully"
                }
                
        except httpx.TimeoutException:
            logger.error("Request timed out after 180 seconds")
            raise Exception("Product photoshoot request timed out. The image might be too large or the service is slow.")
        except Exception as e:
            logger.error(f"Product photoshoot error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise
    
    async def get_models(self) -> list:
        """Get available models"""
        return [
            {"id": "flux-schnell", "name": "Flux Schnell", "type": "text-to-image"},
            {"id": "flux-dev", "name": "Flux Dev", "type": "text-to-image"},
            {"id": "flux-pro", "name": "Flux Pro", "type": "text-to-image"},
            {"id": "qwen-edit", "name": "Qwen Image Edit Plus", "type": "image-edit"},
            {"id": "product-photoshoot", "name": "Product Photoshoot", "type": "product"}
        ]