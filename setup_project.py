#!/usr/bin/env python3
"""
Complete setup script for AI Image Generator with Enhanced Models
This script creates the entire project structure with all necessary files
"""

import os
import sys
from pathlib import Path
import secrets
import base64

def create_project_structure():
    """Create the complete project structure with all files"""
    
    print("🚀 Setting up AI Image Generator with Enhanced Models...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create Python backend files
    create_backend_files()
    
    # Create root files
    create_root_files()
    
    # Generate secret key
    generate_secret_key()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Create virtual environment:")
    print("   python -m venv venv")
    print("\n2. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print("\n3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n4. Copy .env.example to .env and add your API keys:")
    print("   copy .env.example .env  (Windows)")
    print("   cp .env.example .env    (Linux/Mac)")
    print("\n5. Run the application:")
    print("   python desktop.py")

def create_directories():
    """Create all necessary directories"""
    directories = [
        "backend",
        "backend/api",
        "backend/providers",
        "backend/utils",
        "backend/models",
        "frontend",
        "frontend/css",
        "frontend/js",
        "frontend/js/models",
        "frontend/assets",
        "frontend/assets/icons",
        "database",
        "storage/images",
        "storage/thumbnails",
        "storage/temp",
    ]
    
    print("\n📁 Creating directories...")
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

def create_backend_files():
    """Create backend Python files with working code"""
    
    print("\n🐍 Creating backend files...")
    
    # backend/__init__.py
    create_file("backend/__init__.py", '"""AI Image Generator Backend"""')
    
    # backend/config.py
    create_file("backend/config.py", '''from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Image Generator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./database/app.db"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"
    
    # Storage
    STORAGE_PATH: Path = Path("./storage")
    
    # API Keys (from environment)
    FAL_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
''')
    
    # backend/database.py
    create_file("backend/database.py", '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')
    
    # backend/models.py
    create_file("backend/models.py", '''from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from backend.database import Base

class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(String, primary_key=True)
    provider = Column(String(50))
    model = Column(String(100))
    prompt = Column(Text)
    negative_prompt = Column(Text)
    image_path = Column(String(255))
    thumbnail_path = Column(String(255))
    
    # Parameters
    width = Column(Integer)
    height = Column(Integer)
    steps = Column(Integer)
    cfg_scale = Column(Float)
    seed = Column(Integer)
    
    # Metadata
    status = Column(String(20), default="pending")
    error_message = Column(Text)
    generation_time = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Additional data
    parameters = Column(JSON)
    metadata = Column(JSON)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    thumbnail_path = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Metadata
    settings = Column(JSON)
    tags = Column(JSON)

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    provider = Column(String(50), unique=True, nullable=False)
    encrypted_key = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
''')
    
    # backend/main.py
    create_file("backend/main.py", '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from contextlib import asynccontextmanager
import logging

from backend.database import engine, Base
from backend.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting AI Image Generator...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    
    # Setup storage directories
    from backend.utils.file_manager import FileManager
    file_manager = FileManager()
    file_manager.setup_directories()
    logger.info("Storage directories initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AI Image Generator API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
storage_path = Path(__file__).parent.parent / "storage"

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# Import routers
from backend.api import generation, gallery, projects, settings as settings_api
from backend.api.generation_extended import router as extended_router

# Include routers
app.include_router(generation.router, prefix="/api", tags=["generation"])
app.include_router(gallery.router, prefix="/api", tags=["gallery"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(settings_api.router, prefix="/api", tags=["settings"])
app.include_router(extended_router, prefix="/api/extended", tags=["extended"])

@app.get("/")
async def root():
    """Serve the frontend application"""
    html_file = frontend_path / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "AI Image Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Enhanced model pages
@app.get("/models/wan25")
async def wan25_page():
    wan25_file = frontend_path / "enhanced-wan25.html"
    if wan25_file.exists():
        return FileResponse(wan25_file)
    return JSONResponse(status_code=404, content={"error": "WAN-25 page not found"})

@app.get("/models/qwen-edit")
async def qwen_page():
    qwen_file = frontend_path / "enhanced-qwen.html"
    if qwen_file.exists():
        return FileResponse(qwen_file)
    return JSONResponse(status_code=404, content={"error": "Qwen page not found"})

@app.get("/models/product-photoshoot")
async def product_page():
    product_file = frontend_path / "enhanced-product.html"
    if product_file.exists():
        return FileResponse(product_file)
    return JSONResponse(status_code=404, content={"error": "Product page not found"})

@app.get("/api/providers")
async def get_providers():
    """Get list of available providers"""
    return [
        {
            "id": "fal_ai",
            "name": "Fal.ai",
            "status": "active" if settings.FAL_API_KEY else "not_configured",
            "models": [
                {"id": "flux-pro", "name": "Flux Pro"},
                {"id": "flux-dev", "name": "Flux Dev"},
                {"id": "flux-schnell", "name": "Flux Schnell"},
                {"id": "wan-25-preview", "name": "WAN-25 Preview"},
                {"id": "qwen-edit", "name": "Qwen Image Edit Plus"},
                {"id": "product-photoshoot", "name": "Product Photoshoot"}
            ]
        },
        {
            "id": "replicate",
            "name": "Replicate",
            "status": "active" if settings.REPLICATE_API_TOKEN else "not_configured",
            "models": []
        },
        {
            "id": "openai",
            "name": "OpenAI",
            "status": "active" if settings.OPENAI_API_KEY else "not_configured",
            "models": []
        }
    ]
''')
    
    # backend/api/__init__.py
    create_file("backend/api/__init__.py", "")
    
    # backend/api/generation.py
    create_file("backend/api/generation.py", '''from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
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
''')
    
    # backend/api/gallery.py
    create_file("backend/api/gallery.py", '''from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend.database import get_db
from backend.models import Generation
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/gallery")
async def get_gallery(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get gallery images"""
    generations = db.query(Generation).offset(skip).limit(limit).all()
    return {
        "items": generations,
        "total": db.query(Generation).count()
    }

@router.delete("/gallery/{generation_id}")
async def delete_generation(
    generation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a generation"""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    db.delete(generation)
    db.commit()
    return {"message": "Generation deleted"}
''')
    
    # backend/api/projects.py
    create_file("backend/api/projects.py", '''from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend.database import get_db
from backend.models import Project
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/projects")
async def get_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).all()
    return projects

@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project"""
    db_project = Project(
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}
''')
    
    # backend/api/settings.py
    create_file("backend/api/settings.py", '''from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from backend.config import settings as app_settings
from backend.database import get_db
from backend.models import ApiKey
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class ApiKeyUpdate(BaseModel):
    provider: str
    api_key: str

@router.get("/settings")
async def get_settings():
    """Get application settings"""
    return {
        "app_name": app_settings.APP_NAME,
        "version": app_settings.VERSION,
        "providers": {
            "fal_ai": {"configured": bool(app_settings.FAL_API_KEY)},
            "replicate": {"configured": bool(app_settings.REPLICATE_API_TOKEN)},
            "openai": {"configured": bool(app_settings.OPENAI_API_KEY)},
        }
    }

@router.post("/settings/api-keys")
async def update_api_key(
    key_data: ApiKeyUpdate,
    db: Session = Depends(get_db)
):
    """Update API key for a provider"""
    # In production, encrypt the API key before storing
    api_key = db.query(ApiKey).filter(ApiKey.provider == key_data.provider).first()
    
    if api_key:
        api_key.encrypted_key = key_data.api_key
    else:
        api_key = ApiKey(
            provider=key_data.provider,
            encrypted_key=key_data.api_key
        )
        db.add(api_key)
    
    db.commit()
    return {"message": "API key updated"}

@router.get("/settings/test-connection")
async def test_connection(provider: str):
    """Test API connection for a provider"""
    if provider == "fal_ai":
        return {"status": "connected" if app_settings.FAL_API_KEY else "not_configured"}
    return {"status": "not_implemented"}
''')
    
    # backend/api/generation_extended.py
    create_file("backend/api/generation_extended.py", '''from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, List
import json
import uuid
from pydantic import BaseModel

router = APIRouter()

class WAN25Request(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    output_format: str = "webp"
    quality: int = 80
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

class QwenEditRequest(BaseModel):
    instruction: str
    edit_type: str = "object"
    edit_strength: float = 0.8
    coherence: float = 0.7
    auto_mask: bool = True
    preserve_style: bool = True

class ProductShootRequest(BaseModel):
    product_category: str
    product_description: str
    scene_type: str = "studio"
    background_style: str = "gradient"
    lighting_setup: str = "soft"
    props: Optional[List[str]] = None
    remove_background: bool = False
    preserve_shadows: bool = True
    color_palette: Optional[str] = None
    reflection_intensity: float = 0.0
    output_format: str = "png"
    resolution: str = "1024x1024"
    batch_size: int = 1
    add_watermark: bool = False
    generate_variations: bool = False

@router.post("/wan25")
async def generate_wan25(settings: str = Form(...)):
    """Generate image using WAN-25 Preview model"""
    request_data = WAN25Request(**json.loads(settings))
    generation_id = str(uuid.uuid4())
    
    from backend.providers.fal_ai import FalAIProvider
    from backend.config import settings as app_settings
    
    if not app_settings.FAL_API_KEY:
        raise HTTPException(status_code=400, detail="Fal.ai API key not configured")
    
    provider = FalAIProvider(api_key=app_settings.FAL_API_KEY)
    
    try:
        result = await provider.generate_wan25(
            prompt=request_data.prompt,
            aspect_ratio=request_data.aspect_ratio,
            output_format=request_data.output_format,
            quality=request_data.quality,
            style=request_data.style,
            negative_prompt=request_data.negative_prompt,
            seed=request_data.seed
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/qwen-edit")
async def edit_with_qwen(
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    settings: str = Form(...)
):
    """Edit image using Qwen Image Edit Plus model"""
    request_data = QwenEditRequest(**json.loads(settings))
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/product-photoshoot")
async def generate_product_shots(
    product_images: List[UploadFile] = File(...),
    settings: str = Form(...)
):
    """Generate product photography using Product Photoshoot model"""
    request_data = ProductShootRequest(**json.loads(settings))
    generation_id = str(uuid.uuid4())
    
    from backend.providers.fal_ai import FalAIProvider
    from backend.config import settings as app_settings
    
    if not app_settings.FAL_API_KEY:
        raise HTTPException(status_code=400, detail="Fal.ai API key not configured")
    
    provider = FalAIProvider(api_key=app_settings.FAL_API_KEY)
    
    try:
        images_data = [await img.read() for img in product_images]
        
        result = await provider.generate_product_shoot(
            product_images=images_data,
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
            batch_size=request_data.batch_size
        )
        
        return {
            "generation_id": generation_id,
            "status": "completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models():
    """Get list of available enhanced models"""
    return {
        "models": [
            {
                "id": "wan-25-preview",
                "name": "WAN-25 Preview",
                "description": "Advanced text-to-image generation",
                "provider": "fal_ai"
            },
            {
                "id": "qwen-edit",
                "name": "Qwen Image Edit Plus",
                "description": "Advanced image editing",
                "provider": "fal_ai"
            },
            {
                "id": "product-photoshoot",
                "name": "Product Photoshoot",
                "description": "Professional product photography",
                "provider": "fal_ai"
            }
        ]
    }
''')
    
    # backend/providers/__init__.py
    create_file("backend/providers/__init__.py", '''def initialize_providers():
    """Initialize all providers"""
    pass
''')
    
    # backend/providers/base.py
    create_file("backend/providers/base.py", '''from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def generate(self, **kwargs) -> Dict[str, Any]:
        """Generate an image"""
        pass
    
    @abstractmethod
    async def get_models(self) -> list:
        """Get available models"""
        pass
''')
    
    # backend/providers/fal_ai.py
    create_file("backend/providers/fal_ai.py", '''import httpx
import base64
from typing import Dict, Any, Optional, List
from backend.providers.base import BaseProvider

class FalAIProvider(BaseProvider):
    """Fal.ai provider implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://fal.run/fal-ai"
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
            "flux-pro": "flux-pro",
            "flux-dev": "flux/dev",
            "flux-schnell": "flux/schnell"
        }
        
        endpoint = model_map.get(model, "flux/schnell")
        url = f"{self.base_url}/{endpoint}"
        
        payload = {
            "prompt": prompt,
            "image_size": {"width": width, "height": height},
            "num_inference_steps": steps,
            "guidance_scale": cfg_scale,
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed:
            payload["seed"] = seed
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            return {
                "images": result.get("images", []),
                "seed": result.get("seed"),
                "has_nsfw": result.get("has_nsfw_concepts", [False])[0]
            }
    
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
        """Generate image using WAN-25 Preview model"""
        
        url = f"{self.base_url}/wan-25-preview"
        
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "quality": quality
        }
        
        if style:
            payload["style"] = style
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed:
            payload["seed"] = seed
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def edit_qwen(
        self,
        image: bytes,
        instruction: str,
        mask: Optional[bytes] = None,
        edit_type: str = "object",
        edit_strength: float = 0.8,
        coherence: float = 0.7,
        auto_mask: bool = True,
        preserve_style: bool = True
    ) -> Dict[str, Any]:
        """Edit image using Qwen Image Edit Plus"""
        
        url = f"{self.base_url}/qwen-image-edit-plus"
        
        payload = {
            "image": base64.b64encode(image).decode("utf-8"),
            "instruction": instruction,
            "edit_type": edit_type,
            "edit_strength": edit_strength,
            "coherence": coherence,
            "auto_mask": auto_mask,
            "preserve_style": preserve_style
        }
        
        if mask:
            payload["mask"] = base64.b64encode(mask).decode("utf-8")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
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
        batch_size: int = 1
    ) -> Dict[str, Any]:
        """Generate product photography"""
        
        url = f"{self.base_url}/product-photoshoot"
        
        payload = {
            "product_images": [base64.b64encode(img).decode("utf-8") for img in product_images],
            "product_category": category,
            "product_description": description,
            "scene_type": scene_type,
            "background_style": background_style,
            "lighting_setup": lighting_setup,
            "remove_background": remove_background,
            "preserve_shadows": preserve_shadows,
            "reflection_intensity": reflection_intensity,
            "output_format": output_format,
            "resolution": resolution,
            "batch_size": batch_size
        }
        
        if props:
            payload["props"] = props
        if color_palette:
            payload["color_palette"] = color_palette
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_models(self) -> list:
        """Get available models"""
        return [
            {"id": "flux-pro", "name": "Flux Pro", "type": "text-to-image"},
            {"id": "flux-dev", "name": "Flux Dev", "type": "text-to-image"},
            {"id": "flux-schnell", "name": "Flux Schnell", "type": "text-to-image"},
            {"id": "wan-25-preview", "name": "WAN-25 Preview", "type": "text-to-image"},
            {"id": "qwen-edit", "name": "Qwen Image Edit Plus", "type": "image-edit"},
            {"id": "product-photoshoot", "name": "Product Photoshoot", "type": "product"}
        ]
''')
    
    # backend/utils/__init__.py
    create_file("backend/utils/__init__.py", "")
    
    # backend/utils/file_manager.py
    create_file("backend/utils/file_manager.py", '''from pathlib import Path
import shutil
import uuid
from typing import Optional
from PIL import Image
import io

class FileManager:
    """Manage file storage for the application"""
    
    def __init__(self):
        self.storage_path = Path("./storage")
        self.images_path = self.storage_path / "images"
        self.thumbnails_path = self.storage_path / "thumbnails"
        self.temp_path = self.storage_path / "temp"
    
    def setup_directories(self):
        """Ensure all storage directories exist"""
        for path in [self.images_path, self.thumbnails_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_image(self, image_data: bytes, filename: Optional[str] = None) -> str:
        """Save an image to storage"""
        if not filename:
            filename = f"{uuid.uuid4()}.png"
        
        filepath = self.images_path / filename
        filepath.write_bytes(image_data)
        
        # Create thumbnail
        self.create_thumbnail(image_data, filename)
        
        return filename
    
    def create_thumbnail(self, image_data: bytes, filename: str):
        """Create a thumbnail for an image"""
        try:
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail((256, 256), Image.Resampling.LANCZOS)
            
            thumb_path = self.thumbnails_path / f"thumb_{filename}"
            img.save(thumb_path, "PNG")
        except Exception as e:
            print(f"Failed to create thumbnail: {e}")
    
    def delete_image(self, filename: str):
        """Delete an image and its thumbnail"""
        image_path = self.images_path / filename
        thumb_path = self.thumbnails_path / f"thumb_{filename}"
        
        if image_path.exists():
            image_path.unlink()
        if thumb_path.exists():
            thumb_path.unlink()
    
    def cleanup_temp(self):
        """Clean up temporary files"""
        for file in self.temp_path.iterdir():
            if file.is_file():
                file.unlink()
''')
    
    # backend/gallery_manager.py (if referenced)
    create_file("backend/gallery_manager.py", '''from pathlib import Path
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

class GalleryManager:
    """Manage gallery operations"""
    
    def __init__(self):
        self.storage_path = Path("./storage")
        self.gallery_file = self.storage_path / "gallery.json"
        self.ensure_gallery_file()
    
    def ensure_gallery_file(self):
        """Ensure gallery file exists"""
        if not self.gallery_file.exists():
            self.gallery_file.write_text("[]")
    
    def add_image(self, image_data: Dict[str, Any]) -> str:
        """Add an image to the gallery"""
        gallery = self.get_gallery()
        
        image_id = str(uuid.uuid4())
        image_data["id"] = image_id
        image_data["created_at"] = datetime.now().isoformat()
        
        gallery.append(image_data)
        self.save_gallery(gallery)
        
        return image_id
    
    def get_gallery(self) -> List[Dict[str, Any]]:
        """Get all gallery items"""
        return json.loads(self.gallery_file.read_text())
    
    def save_gallery(self, gallery: List[Dict[str, Any]]):
        """Save gallery data"""
        self.gallery_file.write_text(json.dumps(gallery, indent=2))
    
    def delete_image(self, image_id: str):
        """Delete an image from the gallery"""
        gallery = self.get_gallery()
        gallery = [img for img in gallery if img.get("id") != image_id]
        self.save_gallery(gallery)
''')
    
    # backend/project_manager.py (if referenced)
    create_file("backend/project_manager.py", '''from pathlib import Path
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

class ProjectManager:
    """Manage project operations"""
    
    def __init__(self):
        self.storage_path = Path("./storage")
        self.projects_file = self.storage_path / "projects.json"
        self.ensure_projects_file()
    
    def ensure_projects_file(self):
        """Ensure projects file exists"""
        if not self.projects_file.exists():
            self.projects_file.write_text("[]")
    
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new project"""
        projects = self.get_projects()
        
        project_id = str(uuid.uuid4())
        project_data["id"] = project_id
        project_data["created_at"] = datetime.now().isoformat()
        
        projects.append(project_data)
        self.save_projects(projects)
        
        return project_id
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        return json.loads(self.projects_file.read_text())
    
    def save_projects(self, projects: List[Dict[str, Any]]):
        """Save projects data"""
        self.projects_file.write_text(json.dumps(projects, indent=2))
    
    def delete_project(self, project_id: str):
        """Delete a project"""
        projects = self.get_projects()
        projects = [p for p in projects if p.get("id") != project_id]
        self.save_projects(projects)
''')

def create_root_files():
    """Create root project files"""
    
    print("\n📄 Creating root files...")
    
    # desktop.py - Main entry point
    create_file("desktop.py", '''#!/usr/bin/env python3
"""
AI Image Generator Desktop Application
"""

import webview
import threading
import uvicorn
import sys
import time
import requests
import argparse
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DesktopApp:
    def __init__(self, dev_mode=False):
        self.dev_mode = dev_mode
        self.host = "127.0.0.1"
        self.port = 8000
        self.server_thread = None
        self.window = None
        
    def start_server(self):
        """Start the FastAPI server in a separate thread"""
        def run():
            logger.info(f"Starting FastAPI server on {self.host}:{self.port}")
            uvicorn.run(
                "backend.main:app",
                host=self.host,
                port=self.port,
                reload=self.dev_mode,
                log_level="info" if self.dev_mode else "warning"
            )
        
        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        self.wait_for_server()
    
    def wait_for_server(self, timeout=30):
        """Wait for the server to be ready"""
        logger.info("Waiting for server to start...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://{self.host}:{self.port}/health")
                if response.status_code == 200:
                    logger.info("Server is ready!")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.5)
        
        logger.error("Server failed to start within timeout")
        return False
    
    def create_window(self):
        """Create the desktop window"""
        window_config = {
            "title": "AI Image Generator - Enhanced Suite",
            "url": f"http://{self.host}:{self.port}",
            "width": 1400,
            "height": 900,
            "min_size": (1200, 700),
            "resizable": True,
            "fullscreen": False,
            "confirm_close": True,
            "background_color": "#1a1a1a"
        }
        
        if self.dev_mode:
            window_config["debug"] = True
        
        self.window = webview.create_window(**window_config)
        
        # Window event handlers
        self.window.events.loaded += self.on_loaded
        self.window.events.closed += self.on_closed
    
    def on_loaded(self):
        """Called when the window is loaded"""
        logger.info("Window loaded successfully")
    
    def on_closed(self):
        """Called when the window is closed"""
        logger.info("Window closed, shutting down...")
        sys.exit(0)
    
    def run(self):
        """Run the desktop application"""
        try:
            # Start the server
            self.start_server()
            
            # Create and configure window
            self.create_window()
            
            # Start the GUI
            logger.info("Starting desktop application...")
            webview.start(debug=self.dev_mode)
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            logger.info("Application shutdown complete")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Image Generator Desktop App")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode with debug tools"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on"
    )
    
    args = parser.parse_args()
    
    # Change to application directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    # Create and run app
    app = DesktopApp(dev_mode=args.dev)
    if args.port:
        app.port = args.port
    
    app.run()

if __name__ == "__main__":
    main()
''')
    
    # requirements.txt
    create_file("requirements.txt", """# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Desktop
pywebview==4.4.1

# API Clients
httpx==0.25.1
aiohttp==3.9.0
requests==2.31.0

# Image Processing
Pillow==10.1.0

# Security
cryptography==41.0.7
passlib==1.7.4

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
PyYAML==6.0.1
aiofiles==23.2.1
""")
    
    # .env.example
    create_file(".env.example", """# AI Provider API Keys
FAL_API_KEY=your-fal-api-key-here
REPLICATE_API_TOKEN=your-replicate-token-here
OPENAI_API_KEY=your-openai-key-here
OPENROUTER_API_KEY=your-openrouter-key-here

# Application Settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./database/app.db
DEBUG=False

# Server Settings
HOST=127.0.0.1
PORT=8000
""")
    
    # .gitignore
    create_file(".gitignore", """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment
.env
.env.local
encryption.key

# Database
*.db
*.sqlite
*.sqlite3
database/

# Storage
storage/images/*
storage/thumbnails/*
storage/temp/*
!storage/images/.gitkeep
!storage/thumbnails/.gitkeep
!storage/temp/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Logs
*.log
logs/
""")
    
    # Create .gitkeep files
    create_file("storage/images/.gitkeep", "")
    create_file("storage/thumbnails/.gitkeep", "")
    create_file("storage/temp/.gitkeep", "")
    
    # README.md
    create_file("README.md", """# AI Image Generator - Enhanced Suite

A powerful desktop application for generating and editing images using multiple AI providers.

## Features

### Core Generation
- **Multiple AI Providers**: Fal.ai, Replicate, OpenAI, OpenRouter
- **Advanced Models**: Flux Pro/Dev/Schnell, DALL-E, and more
- **Project Management**: Organize your generations
- **Gallery**: Browse and manage generated images

### Enhanced Models
- **WAN-25 Preview**: Advanced text-to-image generation
- **Qwen Image Edit Plus**: Intelligent image editing
- **Product Photoshoot**: Professional product photography

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-image-generator
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run the application**:
   ```bash
   python desktop.py
   ```

## Development Mode

Run with debug tools enabled:
```bash
python desktop.py --dev
```

## API Endpoints

### Standard Generation
- `POST /api/generate` - Generate images
- `GET /api/gallery` - Browse gallery
- `GET /api/projects` - Manage projects

### Enhanced Models
- `POST /api/extended/wan25` - WAN-25 generation
- `POST /api/extended/qwen-edit` - Qwen editing
- `POST /api/extended/product-photoshoot` - Product photography

## Requirements

- Python 3.8+
- Windows/macOS/Linux
- At least one API key (Fal.ai recommended)

## Support

For issues or questions, please open an issue on GitHub.
""")

def create_file(path: str, content: str):
    """Create a file with content"""
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        print(f"  ✓ {path}")
    except Exception as e:
        print(f"  ✗ {path}: {e}")

def generate_secret_key():
    """Generate a random secret key"""
    print("\n🔐 Generating secret key...")
    secret_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    print(f"  Generated secret key: {secret_key}")
    print("  Add this to your .env file as SECRET_KEY")

if __name__ == "__main__":
    create_project_structure()
