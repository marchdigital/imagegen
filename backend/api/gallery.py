from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/gallery")
async def get_gallery(skip: int = 0, limit: int = 20):
    """Get gallery images"""
    return {"items": [], "total": 0}

@router.delete("/gallery/{generation_id}")
async def delete_generation(generation_id: str):
    """Delete a generation"""
    return {"message": "Generation deleted"}