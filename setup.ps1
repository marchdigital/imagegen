# AI Image Generator - Setup Script (Fixed Version)
# Save this as setup.ps1 and run it

Write-Host "Setting up AI Image Generator Project..." -ForegroundColor Cyan

# Create main project directory
$projectPath = "ai-image-generator"
if (!(Test-Path $projectPath)) {
    New-Item -ItemType Directory -Path $projectPath | Out-Null
    Write-Host "Created project directory: $projectPath" -ForegroundColor Green
}
Set-Location $projectPath

# Create directory structure
Write-Host "Creating directory structure..." -ForegroundColor Yellow
$dirs = @(
    "backend",
    "backend\api",
    "backend\providers",
    "backend\utils",
    "frontend",
    "frontend\css",
    "frontend\js",
    "frontend\js\models",
    "frontend\assets",
    "frontend\assets\icons",
    "storage",
    "storage\images",
    "storage\thumbnails",
    "storage\temp",
    "database"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host "Creating Python files..." -ForegroundColor Yellow

# Create requirements.txt
@"
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.12.1
pywebview==4.4.1
openai==1.3.5
replicate==0.20.0
httpx==0.25.1
aiohttp==3.9.0
Pillow==10.1.0
cryptography==41.0.7
python-jose[cryptography]==3.3.0
passlib==1.7.4
bcrypt==4.1.1
pydantic==2.5.0
pydantic-settings==2.1.0
PyYAML==6.0.1
aiofiles==23.2.1
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Create .env template
@"
FAL_API_KEY=your-fal-api-key-here
REPLICATE_API_TOKEN=your-replicate-token-here
OPENAI_API_KEY=your-openai-key-here
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./database/app.db
APP_HOST=127.0.0.1
APP_PORT=8000
DEBUG=False
"@ | Out-File -FilePath ".env" -Encoding UTF8

# Create backend/__init__.py
'"""AI Image Generator Backend"""' | Out-File -FilePath "backend\__init__.py" -Encoding UTF8

# Create backend/config.py
@"
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    fal_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    secret_key: str = "change-this-secret-key"
    database_url: str = "sqlite:///./database/app.db"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
"@ | Out-File -FilePath "backend\config.py" -Encoding UTF8

# Create backend/database.py
@"
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(
    settings.database_url,
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
"@ | Out-File -FilePath "backend\database.py" -Encoding UTF8

# Create backend/models.py
@"
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    generations = relationship('Generation', back_populates='project')

class Generation(Base):
    __tablename__ = 'generations'
    id = Column(String, primary_key=True)
    model = Column(String)
    prompt = Column(Text)
    parameters = Column(JSON)
    status = Column(String, default='pending')
    result_url = Column(String)
    result_urls = Column(JSON)
    project_id = Column(Integer, ForeignKey('projects.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship('Project', back_populates='generations')
"@ | Out-File -FilePath "backend\models.py" -Encoding UTF8

# Create backend/main.py
@"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title='AI Image Generator API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def root():
    return {'message': 'AI Image Generator API', 'version': '1.0.0'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}
"@ | Out-File -FilePath "backend\main.py" -Encoding UTF8

# Create empty API files
New-Item -ItemType File -Path "backend\api\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "backend\providers\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "backend\utils\__init__.py" -Force | Out-Null

# Create frontend/index.html
@"
<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <title>AI Image Generator</title>
    <link rel='stylesheet' href='css/main.css'>
</head>
<body>
    <div id='app'>
        <nav class='navbar'>
            <h1>AI Image Generator</h1>
            <div class='nav-menu'>
                <button class='nav-item active'>Generate</button>
                <button class='nav-item'>Gallery</button>
                <button class='nav-item'>Projects</button>
                <button class='nav-item'>Settings</button>
            </div>
        </nav>
        <main class='main-content'>
            <div id='model-selector'></div>
            <div id='model-interfaces'></div>
            <div id='results-container'></div>
        </main>
    </div>
    <script src='js/app.js'></script>
</body>
</html>
"@ | Out-File -FilePath "frontend\index.html" -Encoding UTF8

# Create frontend/css/main.css
@"
* { margin: 0; padding: 0; box-sizing: border-box; }
body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0a;
    color: #e0e0e0;
}
.navbar {
    background: #1a1a1a;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #333;
}
.nav-menu { display: flex; gap: 1rem; }
.nav-item {
    padding: 0.5rem 1rem;
    background: transparent;
    color: #888;
    border: 1px solid #333;
    border-radius: 6px;
    cursor: pointer;
}
.nav-item.active {
    background: #667eea;
    color: white;
    border-color: transparent;
}
.main-content { padding: 2rem; }
"@ | Out-File -FilePath "frontend\css\main.css" -Encoding UTF8

# Create frontend/js/app.js
@"
console.log('AI Image Generator initialized');
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        e.target.classList.add('active');
    });
});
"@ | Out-File -FilePath "frontend\js\app.js" -Encoding UTF8

# Create desktop.py
@"
import webview
import uvicorn
from threading import Thread

def start_server():
    uvicorn.run('backend.main:app', host='127.0.0.1', port=8000)

def main():
    server = Thread(target=start_server, daemon=True)
    server.start()
    webview.create_window('AI Image Generator', 'http://127.0.0.1:8000', width=1400, height=900)
    webview.start()

if __name__ == '__main__':
    main()
"@ | Out-File -FilePath "desktop.py" -Encoding UTF8

# Create start.bat
@"
@echo off
echo Starting AI Image Generator...
call venv\Scripts\activate
python desktop.py
pause
"@ | Out-File -FilePath "start.bat" -Encoding ASCII

# Create README.md
@"
# AI Image Generator

## Setup
1. Create virtual environment: python -m venv venv
2. Activate: venv\Scripts\activate
3. Install dependencies: pip install -r requirements.txt
4. Add API keys to .env file
5. Run: python desktop.py

## Features
- Multiple AI models (Fal.ai, DALL-E, Stable Diffusion)
- Image editing capabilities
- Project management
- Gallery view
"@ | Out-File -FilePath "README.md" -Encoding UTF8

# Create .gitignore
@"
__pycache__/
*.py[cod]
venv/
.env
*.db
storage/images/*
storage/thumbnails/*
storage/temp/*
.vscode/
.idea/
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host "`nProject structure created successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Create virtual environment: python -m venv venv" -ForegroundColor White
Write-Host "2. Activate it: .\venv\Scripts\activate" -ForegroundColor White
Write-Host "3. Install packages: pip install -r requirements.txt" -ForegroundColor White
Write-Host "4. Add your API keys to the .env file" -ForegroundColor White
Write-Host "5. Run the app: python desktop.py" -ForegroundColor White

Write-Host "`nProject location: $(Get-Location)" -ForegroundColor Magenta