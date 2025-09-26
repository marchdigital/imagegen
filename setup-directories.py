#!/usr/bin/env python3
"""
Setup script to create the directory structure for AI Image Generator
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create all necessary directories for the application"""
    
    # Define directory structure
    directories = [
        # Database
        "database",
        
        # Storage
        "storage",
        "storage/images",
        "storage/thumbnails", 
        "storage/temp",
        
        # Frontend
        "frontend",
        "frontend/css",
        "frontend/js",
        "frontend/assets",
        "frontend/assets/icons",
        
        # Backend
        "backend",
        "backend/api",
        "backend/providers",
        "backend/utils",
    ]
    
    # Create each directory
    for dir_path in directories:
        # Convert forward slashes to correct path separator for the OS
        dir_path = Path(dir_path)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {dir_path}")
        except Exception as e:
            print(f"✗ Failed to create {dir_path}: {e}")
    
    print("\n✅ Directory structure created successfully!")
    
    # Create empty __init__.py files for Python packages
    python_packages = [
        "backend",
        "backend/api",
        "backend/providers", 
        "backend/utils",
    ]
    
    print("\nCreating Python package files...")
    for package in python_packages:
        init_file = Path(package) / "__init__.py"
        try:
            init_file.touch(exist_ok=True)
            print(f"✓ Created: {init_file}")
        except Exception as e:
            print(f"✗ Failed to create {init_file}: {e}")
    
    # Create initial files
    create_initial_files()
    
    print("\n🎉 Setup complete! Next steps:")
    print("1. Create a .env file with your API keys")
    print("2. Install Python dependencies: pip install -r requirements.txt")
    print("3. Run the application: python desktop.py")

def create_initial_files():
    """Create initial empty files"""
    
    files_to_create = [
        # Root files
        (".env.example", """# Example environment variables
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./database/app.db

# API Keys
FAL_API_KEY=your-fal-api-key
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key
"""),
        
        ("requirements.txt", """# Core
fastapi==0.104.1
uvicorn==0.24.0
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
bcrypt==4.1.1

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
PyYAML==6.0.1
aiofiles==23.2.1
"""),
        
        ("README.md", """# AI Image Generator

A powerful desktop application for generating images using multiple AI providers.

## Features
- Multiple AI provider support (Fal.ai, Replicate, OpenAI, OpenRouter)
- Advanced generation controls
- Project management
- Gallery and history
- Local storage with SQLite

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your API keys
3. Run: `python desktop.py`

## Development
Run in development mode: `python desktop.py --dev`
"""),
    ]
    
    print("\nCreating initial files...")
    for filename, content in files_to_create:
        file_path = Path(filename)
        try:
            # Don't overwrite existing files
            if not file_path.exists():
                file_path.write_text(content)
                print(f"✓ Created: {filename}")
            else:
                print(f"⚠ Skipped (exists): {filename}")
        except Exception as e:
            print(f"✗ Failed to create {filename}: {e}")

if __name__ == "__main__":
    print("🚀 Setting up AI Image Generator directory structure...")
    print("=" * 50)
    create_directory_structure()