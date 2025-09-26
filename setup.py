import os
from pathlib import Path

print("Creating project structure...")

# Create directories
dirs = [
    "backend", "backend/api", "backend/providers", "backend/utils",
    "frontend", "frontend/css", "frontend/js",
    "database", "storage/images", "storage/thumbnails", "storage/temp"
]

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {d}")

# Create files
files = {
    "backend/__init__.py": "",
    "backend/models.py": "from sqlalchemy.ext.declarative import declarative_base\nBase = declarative_base()",
    "backend/database.py": "from sqlalchemy import create_engine\nengine = None",
    "backend/main.py": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'API'}",
    "backend/config.py": "class Settings:\n    pass\n\nsettings = Settings()",
    "backend/api/__init__.py": "",
    "backend/providers/__init__.py": "def initialize_providers(): pass",
    "backend/utils/__init__.py": "",
    "backend/utils/file_manager.py": "class FileManager:\n    def setup_directories(self): pass",
    "desktop.py": "print('Desktop app')",
    "frontend/index.html": "<html><body><h1>AI Image Generator</h1></body></html>"
}

for filepath, content in files.items():
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"Created: {filepath}")

print("\nSetup complete!")