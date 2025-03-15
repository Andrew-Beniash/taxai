"""
TaxAI - Main Application Entry Point

This module initializes and runs the FastAPI application for the AI-powered Tax Law Assistant.
"""
import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TaxAI",
    description="AI-Powered Tax Law Assistant",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example root endpoint
@app.get("/")
async def root():
    """Root endpoint to verify the API is working."""
    return {"message": "Welcome to TaxAI - AI-Powered Tax Law Assistant"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is functioning."""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,  # Enable auto-reload during development
    )
