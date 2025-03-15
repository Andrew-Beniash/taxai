"""
Configuration Management for TaxAI

This module loads and manages application configuration from environment variables,
providing a central point for accessing configuration values.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    
    URI: str = Field(
        default="sqlite:///./taxai.db",  # Default to SQLite for initial development
        description="Database connection URI",
    )
    POOL_SIZE: int = Field(
        default=5,
        description="Connection pool size",
    )
    ECHO: bool = Field(
        default=False,
        description="Echo SQL queries (for debugging)",
    )


class AIConfig(BaseModel):
    """AI model configuration settings."""
    
    MODEL_PATH: Optional[str] = Field(
        default=None,
        description="Path to local LLM model",
    )
    MODEL_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for cloud-based LLM",
    )
    MODEL_TYPE: str = Field(
        default="llama3",
        description="Type of LLM (llama3, mistral, etc.)",
    )
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model to use for text embeddings",
    )


class VectorDBConfig(BaseModel):
    """Vector database configuration settings."""
    
    TYPE: str = Field(
        default="chroma",
        description="Vector DB type (chroma, pinecone, etc.)",
    )
    PERSIST_DIRECTORY: str = Field(
        default=str(BASE_DIR / "data" / "chroma"),
        description="Directory for persisting ChromaDB",
    )
    PINECONE_API_KEY: Optional[str] = Field(
        default=None,
        description="Pinecone API key (if using Pinecone)",
    )
    PINECONE_ENVIRONMENT: Optional[str] = Field(
        default=None,
        description="Pinecone environment (if using Pinecone)",
    )


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    
    SECRET_KEY: str = Field(
        default="changeme_in_production",  # Will be overridden from env variable
        description="Secret key for JWT token encryption",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm for JWT token encryption",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Expiration time for access tokens in minutes",
    )


class Config(BaseModel):
    """Main application configuration."""
    
    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag",
    )
    API_PREFIX: str = Field(
        default="/api/v1",
        description="Prefix for all API endpoints",
    )
    DATABASE: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration",
    )
    AI: AIConfig = Field(
        default_factory=AIConfig,
        description="AI configuration",
    )
    VECTOR_DB: VectorDBConfig = Field(
        default_factory=VectorDBConfig,
        description="Vector database configuration",
    )
    SECURITY: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration",
    )
    DATA_DIR: str = Field(
        default=str(BASE_DIR / "data"),
        description="Directory for storing application data",
    )

    # Override defaults with environment variables
    def __init__(self, **data):
        super().__init__(**data)
        
        # Set debug mode from environment
        if os.getenv("DEBUG") is not None:
            self.DEBUG = os.getenv("DEBUG").lower() in ("true", "1", "t")
        
        # Database config from environment
        if os.getenv("DATABASE_URI"):
            self.DATABASE.URI = os.getenv("DATABASE_URI")
        
        # AI config from environment
        if os.getenv("MODEL_PATH"):
            self.AI.MODEL_PATH = os.getenv("MODEL_PATH")
        if os.getenv("MODEL_API_KEY"):
            self.AI.MODEL_API_KEY = os.getenv("MODEL_API_KEY")
        if os.getenv("MODEL_TYPE"):
            self.AI.MODEL_TYPE = os.getenv("MODEL_TYPE")
        if os.getenv("EMBEDDING_MODEL"):
            self.AI.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
        
        # Vector DB config from environment
        if os.getenv("VECTOR_DB_TYPE"):
            self.VECTOR_DB.TYPE = os.getenv("VECTOR_DB_TYPE")
        if os.getenv("VECTOR_DB_PERSIST_DIR"):
            self.VECTOR_DB.PERSIST_DIRECTORY = os.getenv("VECTOR_DB_PERSIST_DIR")
        if os.getenv("PINECONE_API_KEY"):
            self.VECTOR_DB.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        if os.getenv("PINECONE_ENVIRONMENT"):
            self.VECTOR_DB.PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
        
        # Security config from environment
        if os.getenv("SECRET_KEY"):
            self.SECURITY.SECRET_KEY = os.getenv("SECRET_KEY")
        if os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
            try:
                self.SECURITY.ACCESS_TOKEN_EXPIRE_MINUTES = int(
                    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
                )
            except (TypeError, ValueError):
                pass  # Use default if invalid


# Create a global configuration instance
config = Config()
