from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add backend to path if not already there
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

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
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    
    # Setup storage directories
    try:
        from backend.utils.file_manager import FileManager
        file_manager = FileManager()
        file_manager.setup_directories()
        logger.info("Storage directories initialized")
    except Exception as e:
        logger.warning(f"Storage setup warning: {e}")
    
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

# Try to import and include routers
try:
    from backend.api import generation
    app.include_router(generation.router, prefix="/api", tags=["generation"])
    logger.info("Generation router included")
except Exception as e:
    logger.warning(f"Could not include generation router: {e}")

try:
    from backend.api import gallery
    app.include_router(gallery.router, prefix="/api", tags=["gallery"])
    logger.info("Gallery router included")
except Exception as e:
    logger.warning(f"Could not include gallery router: {e}")

try:
    from backend.api import projects
    app.include_router(projects.router, prefix="/api", tags=["projects"])
    logger.info("Projects router included")
except Exception as e:
    logger.warning(f"Could not include projects router: {e}")

try:
    from backend.api import settings as settings_api
    app.include_router(settings_api.router, prefix="/api", tags=["settings"])
    logger.info("Settings router included")
except Exception as e:
    logger.warning(f"Could not include settings router: {e}")

# Import and include the extended generation router
try:
    from backend.api import generation_extended
    app.include_router(generation_extended.router, prefix="/api/extended", tags=["extended"])
    logger.info("Extended generation router included successfully!")
except ImportError as e:
    logger.error(f"Could not import generation_extended: {e}")
except Exception as e:
    logger.error(f"Could not include extended generation router: {e}")

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

# Debug endpoint to check loaded routes
@app.get("/api/routes")
async def get_routes():
    """Get all registered routes for debugging"""
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": route.methods if hasattr(route, "methods") else None
            })
    return routes