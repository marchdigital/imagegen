#!/usr/bin/env python3
"""
Complete setup script for AI Image Generator
This script creates the entire project structure and all necessary files
"""

import os
import sys
from pathlib import Path
import secrets
import base64

def create_project_structure():
    """Create the complete project structure with all files"""
    
    print("🚀 Setting up AI Image Generator...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create Python backend files
    create_backend_files()
    
    # Create frontend files
    create_frontend_files()
    
    # Create root files
    create_root_files()
    
    # Generate secret key
    generate_secret_key()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Copy .env.example to .env and add your API keys:")
    print("   copy .env.example .env  (Windows)")
    print("   cp .env.example .env    (Linux/Mac)")
    print("\n4. Run the application:")
    print("   python desktop.py")

def create_directories():
    """Create all necessary directories"""
    directories = [
        "database",
        "storage/images",
        "storage/thumbnails", 
        "storage/temp",
        "frontend/css",
        "frontend/js",
        "frontend/assets/icons",
        "backend/api",
        "backend/providers",
        "backend/utils",
    ]
    
    print("\n📁 Creating directories...")
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

def create_backend_files():
    """Create backend Python files with minimal working code"""
    
    print("\n🐍 Creating backend files...")
    
    # backend/__init__.py
    create_file("backend/__init__.py", "")
    
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

SQLALCHEMY_DATABASE_URL = "sqlite:///./database/app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
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
    
    # backend/main.py - Simplified version
    create_file("backend/main.py", '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="AI Image Generator API", version="1.0.0")

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
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Mount storage
storage_path = Path(__file__).parent.parent / "storage"
if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

@app.get("/")
async def root():
    """Serve the frontend application"""
    html_file = frontend_path / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "AI Image Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/providers")
async def get_providers():
    """Get list of available providers - dummy data for now"""
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
                    "name": "sdxl",
                    "display_name": "SDXL",
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

@app.get("/api/settings")
async def get_settings():
    """Get application settings"""
    return {
        "theme": "dark",
        "autoSave": True,
        "confirmDelete": True,
        "keyboardShortcuts": True
    }

@app.get("/api/gallery")
async def get_gallery(limit: int = 10):
    """Get recent generations - returns empty for now"""
    return []

@app.get("/api/dashboard/stats")
async def get_stats():
    """Get dashboard statistics"""
    return {
        "total_generations": 0,
        "storage_usage_gb": 0,
        "last_generation": None
    }

@app.post("/api/generation/generate")
async def generate_image(params: dict):
    """Generate an image - placeholder for now"""
    return {
        "id": 1,
        "status": "pending",
        "message": "Generation endpoint not yet implemented"
    }
''')
    
    # Create empty API files
    create_file("backend/api/__init__.py", "")
    create_file("backend/api/generation.py", "# Generation API endpoints")
    create_file("backend/api/gallery.py", "# Gallery API endpoints")
    create_file("backend/api/projects.py", "# Projects API endpoints")
    create_file("backend/api/settings.py", "# Settings API endpoints")
    create_file("backend/api/dashboard.py", "# Dashboard API endpoints")
    
    # Create empty provider files
    create_file("backend/providers/__init__.py", "def initialize_providers(): pass")
    create_file("backend/providers/base.py", "# Base provider class")
    
    # Create empty utils files
    create_file("backend/utils/__init__.py", "")
    create_file("backend/utils/file_manager.py", '''from pathlib import Path

class FileManager:
    def __init__(self):
        self.storage_path = Path("./storage")
        
    def setup_directories(self):
        """Ensure storage directories exist"""
        for dir_name in ["images", "thumbnails", "temp"]:
            (self.storage_path / dir_name).mkdir(parents=True, exist_ok=True)
''')

def create_frontend_files():
    """Create frontend files"""
    
    print("\n🎨 Creating frontend files...")
    
    # Create empty CSS files
    create_file("frontend/css/main.css", "/* Main styles */")
    create_file("frontend/css/components.css", "/* Component styles */")
    create_file("frontend/css/themes.css", "/* Theme styles */")
    
    # Create empty JS files
    create_file("frontend/js/api.js", "// API client")
    create_file("frontend/js/generation.js", "// Generation logic")
    create_file("frontend/js/gallery.js", "// Gallery management")
    create_file("frontend/js/projects.js", "// Project management")
    create_file("frontend/js/settings.js", "// Settings management")
    create_file("frontend/js/ui.js", "// UI utilities")
    create_file("frontend/js/components.js", "// Reusable components")

def create_root_files():
    """Create root project files"""
    
    print("\n📄 Creating root files...")
    
    # .env.example
    create_file(".env.example", """# Example environment variables
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./database/app.db

# API Keys
FAL_API_KEY=your-fal-api-key
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key
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
encryption.key

# Database
*.db
*.sqlite
*.sqlite3

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

# OS
.DS_Store
Thumbs.db
""")
    
    # Create .gitkeep files to preserve empty directories
    create_file("storage/images/.gitkeep", "")
    create_file("storage/thumbnails/.gitkeep", "")
    create_file("storage/temp/.gitkeep", "")

def create_file(path: str, content: str):
    """Create a file with content"""
    file_path = Path(path)
    try:
        # Don't overwrite existing files
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            print(f"  ✓ {path}")
        else:
            print(f"  ⚠ {path} (exists)")
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