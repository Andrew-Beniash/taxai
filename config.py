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
    "llama": "meta-llama/Llama-3.1-8B-Instruct",
    "zephyr": "HuggingFaceH4/zephyr-7b-beta"
}

# Allow model override from environment
MODEL_OVERRIDE = os.getenv("MODEL_OVERRIDE", "")

# Current model name based on settings
if MODEL_OVERRIDE:
    CURRENT_MODEL = MODEL_OVERRIDE
else:
    CURRENT_MODEL = MODEL_NAMES["mistral"] if USE_MISTRAL else MODEL_NAMES["llama"]

# Hugging Face API settings
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
USE_HUGGINGFACE_API = os.getenv("USE_HUGGINGFACE_API", "true").lower() == "true"

# Device settings (only used for local model, not for Hugging Face API)
USE_CUDA = os.getenv("USE_CUDA", "false").lower() == "true"
QUANTIZATION_BITS = int(os.getenv("QUANTIZATION_BITS", "16"))
