# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path

from backend.database import engine, SessionLocal
from backend.models import Base
from backend.config import settings
from backend.api import generation, gallery, projects, settings as settings_api, dashboard
from backend.providers import initialize_providers
from backend.utils.file_manager import FileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting AI Image Generator...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    
    # Initialize storage directories
    file_manager = FileManager()
    file_manager.setup_directories()
    logger.info("Storage directories initialized")
    
    # Initialize providers
    initialize_providers()
    logger.info("Providers initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Image Generator...")


# Create FastAPI app
app = FastAPI(
    title="AI Image Generator API",
    description="Generate images using multiple AI providers",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "frontend"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Mount storage for serving generated images
storage_path = Path(__file__).parent.parent / "storage"
if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# Include API routers
app.include_router(generation.router, prefix="/api/generation", tags=["Generation"])
app.include_router(gallery.router, prefix="/api/gallery", tags=["Gallery"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Serve the frontend application"""
    html_file = static_path / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "AI Image Generator API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/api/providers")
async def get_providers():
    """Get list of available providers and their models"""
    db = SessionLocal()
    try:
        from backend.models import Provider, Model
        providers = db.query(Provider).filter(Provider.is_active == True).all()
        
        result = []
        for provider in providers:
            models = db.query(Model).filter(
                Model.provider_id == provider.id,
                Model.is_active == True
            ).all()
            
            result.append({
                "id": provider.id,
                "name": provider.name,
                "type": provider.type.value,
                "models": [
                    {
                        "id": model.id,
                        "name": model.name,
                        "display_name": model.display_name or model.name,
                        "model_id": model.model_id,
                        "type": model.type.value,
                        "max_width": model.max_width,
                        "max_height": model.max_height,
                        "supports_img2img": model.supports_img2img,
                        "supports_inpainting": model.supports_inpainting
                    }
                    for model in models
                ]
            })
        
        return result
    finally:
        db.close()


# backend/database.py
from sqlalchemy import create_engine
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


# backend/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os
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
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Storage
    STORAGE_PATH: Path = Path("./storage")
    IMAGES_DIR: str = "images"
    THUMBNAILS_DIR: str = "thumbnails"
    TEMP_DIR: str = "temp"
    MAX_IMAGE_SIZE: int = 10485760  # 10MB
    THUMBNAIL_SIZE: tuple = (256, 256)
    
    # Generation
    MAX_CONCURRENT_GENERATIONS: int = 3
    GENERATION_TIMEOUT: int = 120  # seconds
    DEFAULT_STEPS: int = 20
    DEFAULT_CFG_SCALE: float = 7.5
    
    # API Keys (from environment)
    FAL_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# backend/security.py
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os
import base64

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption key management
def get_or_create_key():
    """Get or create encryption key for API keys"""
    key_file = "encryption.key"
    
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    
    return key


class APIKeyEncryption:
    def __init__(self):
        self.cipher = Fernet(get_or_create_key())
    
    def encrypt(self, api_key: str) -> str:
        """Encrypt an API key"""
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        encrypted = base64.b64decode(encrypted_key.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()


# Singleton instance
encryption = APIKeyEncryption()


# backend/utils/file_manager.py
import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
from datetime import datetime
from backend.config import settings


class FileManager:
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.images_dir = self.storage_path / settings.IMAGES_DIR
        self.thumbnails_dir = self.storage_path / settings.THUMBNAILS_DIR
        self.temp_dir = self.storage_path / settings.TEMP_DIR
    
    def setup_directories(self):
        """Create necessary storage directories"""
        for directory in [self.images_dir, self.thumbnails_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_image(self, image_data: bytes, filename: str = None) -> Tuple[str, str]:
        """Save image and create thumbnail"""
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(image_data).hexdigest()[:8]
            filename = f"img_{timestamp}_{file_hash}.png"
        
        # Save full image
        image_path = self.images_dir / filename
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        # Create thumbnail
        thumbnail_path = self.create_thumbnail(image_path, filename)
        
        return str(image_path), str(thumbnail_path)
    
    def create_thumbnail(self, image_path: Path, filename: str) -> str:
        """Create thumbnail for an image"""
        thumbnail_path = self.thumbnails_dir / f"thumb_{filename}"
        
        with Image.open(image_path) as img:
            img.thumbnail(settings.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "PNG")
        
        return str(thumbnail_path)
    
    def delete_image(self, image_path: str, thumbnail_path: str = None):
        """Delete image and its thumbnail"""
        if os.path.exists(image_path):
            os.remove(image_path)
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_storage_info(self) -> dict:
        """Get storage usage information"""
        total_size = 0
        image_count = 0
        
        for file_path in self.images_dir.glob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                image_count += 1
        
        return {
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "image_count": image_count,
            "storage_path": str(self.storage_path)
        }