from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, List
import json
import uuid
from pydantic import BaseModel

router = APIRouter()

@router.post("/wan25")
async def generate_wan25(
    prompt: str = Form(...),
    aspect_ratio: str = Form("1:1"),
    output_format: str = Form("webp"),
    quality: int = Form(80),
    style: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None)
):
    """Generate image using WAN-25 Preview model"""
    generation_id = str(uuid.uuid4())
    
    from backend.providers.fal_ai import FalAIProvider
    from backend.config import settings as app_settings
    
    if not app_settings.FAL_API_KEY:
        raise HTTPException(status_code=400, detail="Fal.ai API key not configured")
    
    provider = FalAIProvider(api_key=app_settings.FAL_API_KEY)
    
    try:
        # Call the provider with the correct parameters
        result = await provider.generate_wan25(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            output_format=output_format,
            quality=quality,
            style=style,
            negative_prompt=negative_prompt,
            seed=seed
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
    except Exception as e:
        print(f"WAN-25 Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/qwen-edit")
async def edit_with_qwen(
    image: UploadFile = File(...),
    instruction: str = Form(...),
    mask: Optional[UploadFile] = File(None),
    edit_type: str = Form("object"),
    edit_strength: float = Form(0.8),
    coherence: float = Form(0.7),
    auto_mask: bool = Form(True),
    preserve_style: bool = Form(True)
):
    """Edit image using Qwen Image Edit Plus model"""
    generation_id = str(uuid.uuid4())
    
    from backend.providers.fal_ai import FalAIProvider
    from backend.config import settings as app_settings
    
    if not app_settings.FAL_API_KEY:
        raise HTTPException(status_code=400, detail="Fal.ai API key not configured")
    
    provider = FalAIProvider(api_key=app_settings.FAL_API_KEY)
    
    try:
        image_data = await image.read()
        mask_data = await mask.read() if mask else None
        
        result = await provider.edit_qwen(
            image=image_data,
            instruction=instruction,
            mask=mask_data,
            edit_type=edit_type,
            edit_strength=edit_strength,
            coherence=coherence,
            auto_mask=auto_mask,
            preserve_style=preserve_style
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
    except Exception as e:
        print(f"Qwen Edit Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/product-photoshoot")
async def generate_product_shots(
    product_images: List[UploadFile] = File(...),
    product_category: str = Form(...),
    product_description: str = Form(...),
    scene_type: str = Form("studio"),
    background_style: str = Form("gradient"),
    lighting_setup: str = Form("soft"),
    props: Optional[str] = Form(None),  # Comma-separated string
    remove_background: bool = Form(False),
    preserve_shadows: bool = Form(True),
    color_palette: Optional[str] = Form(None),
    reflection_intensity: float = Form(0.0),
    output_format: str = Form("png"),
    resolution: str = Form("1024x1024"),
    batch_size: int = Form(1),
    add_watermark: bool = Form(False),
    generate_variations: bool = Form(False)
):
    """Generate product photography using Product Photoshoot model"""
    generation_id = str(uuid.uuid4())
    
    from backend.providers.fal_ai import FalAIProvider
    from backend.config import settings as app_settings
    
    if not app_settings.FAL_API_KEY:
        raise HTTPException(status_code=400, detail="Fal.ai API key not configured")
    
    provider = FalAIProvider(api_key=app_settings.FAL_API_KEY)
    
    try:
        images_data = [await img.read() for img in product_images]
        
        # Parse props if provided
        props_list = [p.strip() for p in props.split(',')] if props else None
        
        result = await provider.generate_product_shoot(
            product_images=images_data,
            category=product_category,
            description=product_description,
            scene_type=scene_type,
            background_style=background_style,
            lighting_setup=lighting_setup,
            props=props_list,
            remove_background=remove_background,
            preserve_shadows=preserve_shadows,
            color_palette=color_palette,
            reflection_intensity=reflection_intensity,
            output_format=output_format,
            resolution=resolution,
            batch_size=batch_size
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
    except Exception as e:
        print(f"Product Photoshoot Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models():
    """Get list of available enhanced models"""
    return {
        "models": [
            {
                "id": "wan-25-preview",
                "name": "WAN-25 Preview",
                "description": "Advanced text-to-image generation with superior quality",
                "provider": "fal_ai",
                "features": [
                    "High-quality image generation",
                    "Multiple aspect ratios",
                    "Style presets",
                    "Advanced parameters"
                ]
            },
            {
                "id": "qwen-edit",
                "name": "Qwen Image Edit Plus",
                "description": "Advanced image editing with AI",
                "provider": "fal_ai",
                "features": [
                    "Intelligent object editing",
                    "Style preservation",
                    "Mask support",
                    "Multiple edit types"
                ]
            },
            {
                "id": "product-photoshoot",
                "name": "Product Photoshoot",
                "description": "Professional product photography generation",
                "provider": "fal_ai",
                "features": [
                    "Multiple scene types",
                    "Background removal",
                    "Lighting control",
                    "Batch processing"
                ]
            }
        ]
    }

@router.get("/health")
async def health_check():
    """Check if enhanced models are available"""
    from backend.config import settings
    
    return {
        "status": "healthy",
        "fal_ai_configured": bool(settings.FAL_API_KEY),
        "models_available": 3
    }

@router.get("/test")
async def test_api():
    """Test if the API and Fal.ai key are working"""
    from backend.config import settings
    
    result = {
        "status": "ok",
        "fal_api_key_configured": bool(settings.FAL_API_KEY),
        "fal_api_key_length": len(settings.FAL_API_KEY) if settings.FAL_API_KEY else 0
    }
    
    if settings.FAL_API_KEY:
        # Test the API key with a simple request
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Key {settings.FAL_API_KEY}",
                    "Content-Type": "application/json"
                }
                # Try to get user info or make a simple test request
                response = await client.get(
                    "https://queue.fal.run/fal-ai/flux/schnell",
                    headers=headers
                )
                result["fal_api_test"] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 405, 422]  # These are "valid" responses
                }
        except Exception as e:
            result["fal_api_test"] = {
                "error": str(e)
            }
    
    return result