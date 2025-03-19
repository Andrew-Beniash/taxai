from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api import query_router
from app.config import ALLOWED_ORIGINS
from app.ai.model_manager import initialize as initialize_ai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tax Law AI API",
    description="API for processing tax law queries using AI",
    version="0.1.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components during startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Tax Law AI API")
    try:
        # This will pre-load the model to reduce first request latency
        # Comment out during development as needed to speed up restarts
        # initialize_ai()
        # Note: If commented out, the model will load on the first request
        logger.info("AI initialization deferred to first request")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

# Include API routes
app.include_router(query_router)

@app.get("/")
async def root():
    """Root endpoint for basic health check"""
    return {
        "service": "Tax Law AI API",
        "status": "online",
        "version": "0.1.0"
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT
    
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)
