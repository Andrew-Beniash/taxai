# app/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Tax Law Assistant"
    
    # Database settings (will be implemented later)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/taxai")
    
    class Config:
        env_file = ".env"

settings = Settings()
