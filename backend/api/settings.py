from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

@router.get("/settings")
async def get_settings():
    """Get application settings"""
    from backend.config import settings as app_settings
    return {
        "app_name": app_settings.APP_NAME,
        "version": app_settings.VERSION,
        "providers": {
            "fal_ai": {"configured": bool(app_settings.FAL_API_KEY)}
        }
    }