from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/projects")
async def get_projects():
    """Get all projects"""
    return []

@router.post("/projects")
async def create_project(project: ProjectCreate):
    """Create a new project"""
    return {"id": 1, "name": project.name, "description": project.description}