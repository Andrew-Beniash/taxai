"""
Configuration settings for the AI-powered tax law system.
This file centralizes all configuration options.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Model settings
USE_MISTRAL = os.getenv("USE_MISTRAL", "true").lower() == "true"
MODEL_NAMES = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
    "llama": "meta-llama/Llama-3.1-8B-Instruct"
}

# Current model name based on settings
CURRENT_MODEL = MODEL_NAMES["mistral"] if USE_MISTRAL else MODEL_NAMES["llama"]

# Device settings
USE_CUDA = os.getenv("USE_CUDA", "false").lower() == "true"
QUANTIZATION_BITS = int(os.getenv("QUANTIZATION_BITS", "16"))
