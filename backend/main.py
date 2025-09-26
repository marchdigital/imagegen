from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import base64
import httpx
from typing import Dict, Any
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Image Generator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the CLASSES, not instances
from backend.gallery_manager import GalleryManager
from backend.project_manager import ProjectManager

# Create instances
gallery_manager = GalleryManager()
project_manager = ProjectManager()

# Import the Fal.ai provider
try:
    from backend.providers.fal_ai import fal_provider
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False
    print("Warning: Fal.ai provider not available")

# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
storage_path = Path(__file__).parent.parent / "storage"

# Mount static files
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

@app.get("/")
async def root():
    html_file = frontend_path / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "API"}

@app.get("/api/providers")
async def get_providers():
    return [
        {
            "id": 1,
            "name": "Fal.ai",
            "type": "fal_ai",
            "models": [
                {
                    "id": 1,
                    "name": "flux-dev",
                    "display_name": "Flux Dev",
                    "model_id": "fal-ai/flux/dev",
                    "type": "image",
                    "max_width": 1920,
                    "max_height": 1920,
                    "supports_img2img": True,
                    "supports_inpainting": False
                },
                {
                    "id": 2,
                    "name": "flux-schnell",
                    "display_name": "Flux Schnell (Fast)",
                    "model_id": "fal-ai/flux/schnell",
                    "type": "image",
                    "max_width": 1920,
                    "max_height": 1920,
                    "supports_img2img": False,
                    "supports_inpainting": False
                },
                {
                    "id": 3,
                    "name": "sdxl",
                    "display_name": "Stable Diffusion XL",
                    "model_id": "fal-ai/fast-sdxl",
                    "type": "image",
                    "max_width": 1536,
                    "max_height": 1536,
                    "supports_img2img": True,
                    "supports_inpainting": True
                }
            ]
        }
    ]

@app.post("/api/generation/generate")
async def generate_image(params: dict):
    """Generate an image using the selected provider"""
    
    if not PROVIDER_AVAILABLE:
        return JSONResponse(
            status_code=500,
            content={"error": "Provider not configured. Please check your setup."}
        )
    
    # Get the selected model
    model_id = params.get("model_id")
    model_map = {
        1: "fal-ai/flux/dev",
        2: "fal-ai/flux/schnell", 
        3: "fal-ai/fast-sdxl"
    }
    
    model = model_map.get(model_id, "fal-ai/flux/dev")
    
    # Check if API key is set
    if not os.getenv("FAL_API_KEY"):
        return JSONResponse(
            status_code=500,
            content={"error": "FAL_API_KEY not set. Please add it to your .env file"}
        )
    
    try:
        # Call the Fal.ai provider
        result = await fal_provider.generate_image(
            prompt=params.get("prompt", ""),
            model=model,
            negative_prompt=params.get("negative_prompt", ""),
            width=params.get("width", 1024),
            height=params.get("height", 1024),
            steps=params.get("steps", 20),
            cfg_scale=params.get("cfg_scale", 7.5),
            seed=params.get("seed", -1)
        )
        
        if "error" in result:
            return JSONResponse(
                status_code=500,
                content={"error": result["error"]}
            )
        
        # Save to gallery if successful
        if result.get("success") and result.get("image_url"):
            try:
                gallery_image = await gallery_manager.save_image(
                    image_url=result["image_url"],
                    prompt=params.get("prompt", ""),
                    model=model,
                    params=params
                )
                result["gallery_id"] = gallery_image["id"]
            except Exception as e:
                print(f"Failed to save to gallery: {e}")
        
        return {
            "success": True,
            "image_url": result.get("image_url"),
            "seed": result.get("seed"),
            "model": result.get("model"),
            "message": "Image generated successfully!"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Generation failed: {str(e)}"}
        )

# Gallery endpoints
@app.post("/api/gallery/save")
async def save_to_gallery(data: dict):
    """Save generated image to local gallery"""
    result = await gallery_manager.save_image(
        image_url=data["image_url"],
        prompt=data["prompt"],
        model=data["model"],
        params=data["params"]
    )
    return {"success": True, "image": result}

@app.get("/api/gallery/list")
async def get_gallery_images(limit: int = 50, filter: str = None):
    """Get gallery images"""
    images = gallery_manager.get_gallery(limit, filter)
    return {"images": images, "total": len(images)}

@app.post("/api/gallery/{image_id}/favorite")
async def toggle_favorite(image_id: int):
    """Toggle favorite status"""
    new_status = gallery_manager.toggle_favorite(image_id)
    return {"success": True, "is_favorite": new_status}

# Project endpoints
@app.get("/api/projects")
async def get_projects(active_only: bool = False):
    return {"projects": project_manager.get_projects(active_only)}

@app.post("/api/projects")
async def create_project(data: dict):
    project = project_manager.create_project(data["name"], data.get("description", ""))
    return {"success": True, "project": project}

@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, data: dict):
    project = project_manager.update_project(project_id, data)
    if project:
        return {"success": True, "project": project}
    return {"success": False, "error": "Project not found"}

@app.get("/api/settings")
async def get_settings():
    return {"theme": "dark", "autoSave": True}

@app.get("/api/gallery")
async def get_gallery(limit: int = 10):
    """Backward compatibility endpoint"""
    return await get_gallery_images(limit)

@app.get("/api/dashboard/stats")
async def get_stats():
    return {
        "total_generations": len(gallery_manager.metadata.get("images", [])),
        "storage_usage_gb": 0,
        "last_generation": None
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
