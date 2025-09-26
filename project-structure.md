# AI Image Generator - Project Structure

## Directory Structure
```
ai-image-generator/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── security.py             # Encryption for API keys
│   ├── api/
│   │   ├── __init__.py
│   │   ├── generation.py       # Generation endpoints
│   │   ├── projects.py         # Project management endpoints
│   │   ├── gallery.py          # Gallery & history endpoints
│   │   ├── settings.py         # Settings endpoints
│   │   └── dashboard.py        # Analytics endpoints
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py            # Base provider class
│   │   ├── fal_ai.py          # Fal.ai integration
│   │   ├── replicate_ai.py    # Replicate integration
│   │   ├── openai_provider.py # OpenAI DALL-E integration
│   │   └── openrouter.py      # OpenRouter integration
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py     # Image processing utilities
│       ├── prompt_utils.py    # Prompt enhancement/templates
│       └── file_manager.py    # File storage management
├── frontend/
│   ├── index.html              # Main HTML file
│   ├── css/
│   │   ├── main.css           # Main styles
│   │   ├── components.css     # Component styles
│   │   └── themes.css         # Light/dark themes
│   ├── js/
│   │   ├── app.js            # Main application
│   │   ├── api.js            # API client
│   │   ├── generation.js     # Generation logic
│   │   ├── gallery.js        # Gallery management
│   │   ├── projects.js       # Project management
│   │   ├── settings.js       # Settings management
│   │   ├── ui.js             # UI utilities
│   │   └── components.js     # Reusable components
│   └── assets/
│       └── icons/            # UI icons
├── storage/
│   ├── images/               # Generated images
│   ├── thumbnails/           # Image thumbnails
│   └── temp/                 # Temporary files
├── database/
│   └── app.db                # SQLite database
├── desktop.py                # Desktop application entry point
├── requirements.txt          # Python dependencies
├── package.json             # Frontend dependencies (optional)
├── config.yaml              # Application configuration
└── README.md                # Project documentation
```

## Installation Requirements

### Python Dependencies (requirements.txt)
```txt
# Core
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Desktop
pywebview==4.4.1

# API Providers
openai==1.3.5
replicate==0.20.0
httpx==0.25.1
aiohttp==3.9.0

# Image Processing
Pillow==10.1.0
python-magic==0.4.27

# Security
cryptography==41.0.7
python-jose[cryptography]==3.3.0
passlib==1.7.4
bcrypt==4.1.1

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
PyYAML==6.0.1
aiofiles==23.2.1
```

## Initial Configuration (config.yaml)
```yaml
app:
  name: "AI Image Generator"
  version: "1.0.0"
  debug: false
  host: "127.0.0.1"
  port: 8000

storage:
  base_path: "./storage"
  images_dir: "images"
  thumbnails_dir: "thumbnails"
  temp_dir: "temp"
  max_image_size: 10485760  # 10MB
  thumbnail_size: [256, 256]

database:
  url: "sqlite:///./database/app.db"
  echo: false

security:
  secret_key: "CHANGE_THIS_TO_RANDOM_SECRET_KEY"
  algorithm: "HS256"
  access_token_expire_minutes: 43200  # 30 days

generation:
  max_concurrent: 3
  timeout: 120  # seconds
  default_steps: 20
  default_cfg_scale: 7.5

ui:
  theme: "dark"
  items_per_page: 20
  enable_shortcuts: true
```

## Setup Instructions

### 1. Create Project Directory
```bash
mkdir ai-image-generator
cd ai-image-generator
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
# Create database directory
mkdir database

# Run database migrations (we'll create these next)
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Create Storage Directories
```bash
mkdir -p storage/images storage/thumbnails storage/temp
```

### 5. Set Environment Variables
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./database/app.db
FAL_API_KEY=your-fal-api-key
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key
```

### 6. Run the Application
```bash
# Development mode
python desktop.py --dev

# Production mode
python desktop.py
```

## Development Workflow

### Backend Development
```bash
# Run FastAPI in development mode
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Development
- Open `http://localhost:8000` in your browser
- Use browser dev tools for debugging
- Hot reload enabled with `--reload` flag

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Endpoints Structure

### Generation
- `POST /api/generate` - Generate image
- `GET /api/generation/{id}` - Get generation status
- `POST /api/generation/cancel/{id}` - Cancel generation

### Gallery
- `GET /api/gallery` - List all images
- `GET /api/gallery/{id}` - Get image details
- `PUT /api/gallery/{id}` - Update image metadata
- `DELETE /api/gallery/{id}` - Delete image
- `POST /api/gallery/{id}/favorite` - Toggle favorite

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Settings
- `GET /api/settings` - Get all settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/api-keys` - Save API keys
- `GET /api/settings/test-connection` - Test API connection

### Dashboard
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/usage` - Get usage by provider
- `GET /api/dashboard/trends` - Get generation trends