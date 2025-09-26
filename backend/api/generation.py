from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from typing import Optional
import uuid
import json

router = APIRouter()

@router.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(None),
    model: str = Form("flux-schnell"),
    width: int = Form(1024),
    height: int = Form(1024),
    steps: int = Form(4),
    cfg_scale: float = Form(7.5),
    seed: Optional[int] = Form(None),
    provider: str = Form("fal_ai")
):
    """Generate an image using the specified provider and model"""
    
    generation_id = str(uuid.uuid4())
    
    # Get the provider
    from backend.providers.fal_ai import FalAIProvider
    from backend.config import settings
    
    if not settings.FAL_API_KEY:
        raise HTTPException(status_code=400, detail="Fal.ai API key not configured")
    
    provider_instance = FalAIProvider(api_key=settings.FAL_API_KEY)
    
    try:
        result = await provider_instance.generate(
            model=model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generation/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get the status of a generation"""
    return {
        "generation_id": generation_id,
        "status": "completed",
        "progress": 100
    }