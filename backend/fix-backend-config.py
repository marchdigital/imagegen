# backend/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    fal_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200
    
    # Database
    database_url: str = "sqlite:///./database/app.db"
    
    # Application
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # This allows extra fields in .env file

settings = Settings()