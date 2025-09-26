# backend/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class ProviderType(enum.Enum):
    FAL_AI = "fal_ai"
    REPLICATE = "replicate"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


class GenerationStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    type = Column(Enum(ProviderType), nullable=False)
    base_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    requires_auth = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    models = relationship("Model", back_populates="provider")
    api_keys = relationship("ApiKey", back_populates="provider")
    generations = relationship("Generation", back_populates="provider")


class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    name = Column(String(100), nullable=False)
    display_name = Column(String(100))
    model_id = Column(String(255), nullable=False)  # API model identifier
    type = Column(Enum(ModelType), default=ModelType.IMAGE)
    description = Column(Text)
    
    # Model capabilities
    max_width = Column(Integer, default=1024)
    max_height = Column(Integer, default=1024)
    supports_img2img = Column(Boolean, default=False)
    supports_inpainting = Column(Boolean, default=False)
    supports_video = Column(Boolean, default=False)
    
    # Cost tracking
    cost_per_generation = Column(Float, default=0.0)
    
    # Metadata
    config_schema = Column(JSON)  # JSON schema for model-specific config
    default_config = Column(JSON)  # Default configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    provider = relationship("Provider", back_populates="models")
    generations = relationship("Generation", back_populates="model")
    presets = relationship("Preset", back_populates="model")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Statistics
    generation_count = Column(Integer, default=0)
    
    # Relationships
    generations = relationship("Generation", back_populates="project")
    collections = relationship("Collection", back_populates="project")


class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="collections")
    generations = relationship("GenerationCollection", back_populates="collection")


class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    model_id = Column(Integer, ForeignKey("models.id"))
    
    # Generation parameters
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    seed = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    steps = Column(Integer)
    cfg_scale = Column(Float)
    sampler = Column(String(50))
    scheduler = Column(String(50))
    
    # Image2Image parameters
    init_image_path = Column(String(500))
    denoising_strength = Column(Float)
    
    # Additional parameters (model-specific)
    extra_params = Column(JSON)
    
    # Status and timing
    status = Column(Enum(GenerationStatus), default=GenerationStatus.PENDING)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    generation_time = Column(Float)  # seconds
    
    # Metadata
    api_response = Column(JSON)  # Store full API response
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="generations")
    provider = relationship("Provider", back_populates="generations")
    model = relationship("Model", back_populates="generations")
    images = relationship("Image", back_populates="generation", cascade="all, delete-orphan")
    collections = relationship("GenerationCollection", back_populates="generation")


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey("generations.id"))
    
    # File information
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500))
    file_size = Column(Integer)  # bytes
    file_hash = Column(String(64))  # SHA256
    
    # Image properties
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(10))  # png, jpg, webp
    
    # User metadata
    is_favorite = Column(Boolean, default=False)
    rating = Column(Integer)  # 1-5 stars
    notes = Column(Text)
    tags = Column(JSON)  # Array of tags
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    generation = relationship("Generation", back_populates="images")


class GenerationCollection(Base):
    __tablename__ = "generation_collections"
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey("generations.id"))
    collection_id = Column(Integer, ForeignKey("collections.id"))
    added_at = Column(DateTime, default=func.now())
    
    # Relationships
    generation = relationship("Generation", back_populates="collections")
    collection = relationship("Collection", back_populates="generations")


class Preset(Base):
    __tablename__ = "presets"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # 'style', 'technical', 'project'
    
    # Preset configuration
    config = Column(JSON, nullable=False)  # All generation parameters
    
    # Usage tracking
    use_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Metadata
    is_system = Column(Boolean, default=False)  # Built-in presets
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    model = relationship("Model", back_populates="presets")


class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    encrypted_key = Column(Text, nullable=False)
    label = Column(String(100))  # Optional label for multiple keys
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    last_used = Column(DateTime)
    request_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    provider = relationship("Provider", back_populates="api_keys")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    template = Column(Text, nullable=False)
    negative_template = Column(Text)
    
    # Template variables
    variables = Column(JSON)  # List of variable names and descriptions
    
    # Categorization
    category = Column(String(50))
    tags = Column(JSON)
    
    # Usage tracking
    use_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Metadata
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    category = Column(String(50))  # 'ui', 'storage', 'performance', etc.
    description = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UsageStats(Base):
    __tablename__ = "usage_stats"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    model_id = Column(Integer, ForeignKey("models.id"))
    
    # Counters
    generation_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Timing
    total_generation_time = Column(Float, default=0.0)
    avg_generation_time = Column(Float, default=0.0)
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)
    
    # Relationships
    provider = relationship("Provider")
    model = relationship("Model")