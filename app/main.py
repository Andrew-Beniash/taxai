# app/main.py
from fastapi import FastAPI
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered tax law system providing answers with citations",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Basic route to verify server is running
@app.get("/")
async def root():
    return {"message": "FastAPI server is running!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run with: uvicorn app.main:app --reload
