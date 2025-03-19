import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# AI model settings (to be used later)
MODEL_PATH = os.getenv("MODEL_PATH", "mistralai/Mistral-7B-v0.1")
