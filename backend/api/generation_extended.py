# backend/api/generation_extended.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
import json
from ..providers.fal_ai_extended import (
    FalAIProvider,
    process_wan25_request,
    process_qwen_edit_request,
    process_product_shoot_request
)
import uuid
from datetime import datetime
import traceback

router = APIRouter(prefix="/api/generate", tags=["generation"])

# Request models
class WAN25Request(BaseModel):
    prompt: str
    image_influence: float = Field(default=0.75, ge=0, le=1)
    style_strength: float = Field(default=0.5, ge=0, le=1)
    aspect_ratio: str = "original"
    output_size: str = "1024x1024"
    guidance_scale: float = Field(default=7.5, ge=1, le=20)
    seed: Optional[int] = None
    hd_output: bool = False
    auto_enhance: bool = False
    project_id: Optional[int] = None

class QwenEditRequest(BaseModel):
    instruction: str
    edit_type: str = "auto"
    edit_strength: float = Field(default=0.8, ge=0, le=1)
    coherence: float = Field(default=0.9, ge=0, le=1)
    auto_mask: bool = True
    preserve_style: bool = False
    project_id: Optional[int] = None

class ProductShootRequest(BaseModel):
    product_category: str
    product_description: str
    scene_type: str = "studio"
    background_style: str = "clean_white"
    lighting_setup: str = "soft_box"
    props: Optional[str] = None
    remove_background: bool = True
    preserve_shadows: bool = False
    color_palette: Optional[List[str]] = None
    reflection_intensity: float = Field(default=0.3, ge=0, le=1)
    output_format: str = "square"
    resolution: str = "1024"
    batch_size: int = Field(default=4, ge=1, le=10)
    add_watermark: bool = False
    generate_variations: bool = True
    project_id: Optional[int] = None

# Get provider instance (you'd normally inject this via dependency)
def get_fal_provider():
    # Load from config/env
    import os
    api_key = os.getenv("FAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Fal.ai API key not configured")
    return FalAIProvider(api_key)

@router.post("/wan25-preview")
async def generate_wan25(
    main_image: UploadFile = File(...),
    reference_images: Optional[List[UploadFile]] = File(None),
    settings: str = Form(...),  # JSON string of WAN25Request
    provider: FalAIProvider = Depends(get_fal_provider),
):
    """Generate image using WAN-25 Preview model with multiple reference images"""
    
    try:
        # Parse settings
        request_data = WAN25Request(**json.loads(settings))
        
        # Read images
        main_img_data = await main_image.read()
        ref_imgs_data = None
        if reference_images:
            ref_imgs_data = [await img.read() for img in reference_images]
        
        generation_id = str(uuid.uuid4())
        
        # Process request
        result = await process_wan25_request(
            provider=provider,
            prompt=request_data.prompt,
            main_image=main_img_data,
            reference_images=ref_imgs_data,
            image_influence=request_data.image_influence,
            style_strength=request_data.style_strength,
            aspect_ratio=request_data.aspect_ratio,
            output_size=request_data.output_size,
            guidance_scale=request_data.guidance_scale,
            seed=request_data.seed,
            hd_output=request_data.hd_output,
            auto_enhance=request_data.auto_enhance
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        print("[WAN25] Error:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/qwen-edit")
async def edit_with_qwen(
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    settings: str = Form(...),  # JSON string of QwenEditRequest
    provider: FalAIProvider = Depends(get_fal_provider),
):
    """Edit image using Qwen Image Edit Plus model"""
    
    try:
        # Parse settings
        request_data = QwenEditRequest(**json.loads(settings))
        
        # Read images
        img_data = await image.read()
        mask_data = await mask.read() if mask else None
        
        generation_id = str(uuid.uuid4())
        
        # Process request
        result = await process_qwen_edit_request(
            provider=provider,
            image=img_data,
            instruction=request_data.instruction,
            mask=mask_data,
            edit_type=request_data.edit_type,
            edit_strength=request_data.edit_strength,
            coherence=request_data.coherence,
            auto_mask=request_data.auto_mask,
            preserve_style=request_data.preserve_style
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        print("[QWEN] Error:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/product-photoshoot")
async def generate_product_shots(
    product_images: List[UploadFile] = File(...),
    settings: str = Form(...),  # JSON string of ProductShootRequest
    provider: FalAIProvider = Depends(get_fal_provider),
):
    """Generate product photography using Product Photoshoot model"""
    
    try:
        # Parse settings
        request_data = ProductShootRequest(**json.loads(settings))
        
        # Read images
        imgs_data = [await img.read() for img in product_images]
        
        generation_id = str(uuid.uuid4())
        
        # Process request
        result = await process_product_shoot_request(
            provider=provider,
            product_images=imgs_data,
            category=request_data.product_category,
            description=request_data.product_description,
            scene_type=request_data.scene_type,
            background_style=request_data.background_style,
            lighting_setup=request_data.lighting_setup,
            props=request_data.props,
            remove_background=request_data.remove_background,
            preserve_shadows=request_data.preserve_shadows,
            color_palette=request_data.color_palette,
            reflection_intensity=request_data.reflection_intensity,
            output_format=request_data.output_format,
            resolution=request_data.resolution,
            batch_size=request_data.batch_size,
            add_watermark=request_data.add_watermark,
            generate_variations=request_data.generate_variations
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result,
            "batch_size": len(result.get("images", []))
        }
        
    except Exception as e:
        print("[PRODUCT] Error:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models():
    """Get list of available Fal.ai models and their capabilities"""
    return {
        "models": [
            {
                "id": "wan-25-preview",
                "name": "WAN-25 Preview",
                "description": "Advanced image-to-image with multiple reference support",
                "category": "image-to-image",
                "features": [
                    "Multiple reference images",
                    "Style transfer",
                    "High quality output",
                    "HD mode available"
                ],
                "input_types": ["image", "text", "reference_images"],
                "max_references": 4
            },
            {
                "id": "qwen-image-edit-plus",
                "name": "Qwen Image Edit Plus",
                "description": "Smart AI-powered image editing and manipulation",
                "category": "image-editing",
                "features": [
                    "Object removal",
                    "Object replacement",
                    "Background editing",
                    "Smart inpainting",
                    "Style preservation"
                ],
                "input_types": ["image", "text", "mask"],
                "edit_modes": [
                    "auto",
                    "object_removal",
                    "object_replacement",
                    "background_change",
                    "style_transfer",
                    "color_adjustment"
                ]
            },
            {
                "id": "product-photoshoot",
                "name": "Product Photoshoot",
                "description": "Professional product photography generation",
                "category": "product-photography",
                "features": [
                    "Multi-angle inputs",
                    "Background generation",
                    "Variations",
                    "High-resolution output"
                ],
                "input_types": ["image", "text"],
                "max_images": 8
            }
        ]
    }