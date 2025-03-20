"""
Main FastAPI application for the AI-powered tax law system.
This serves as the API entry point for processing tax law queries.
"""

import os
import time
from typing import Dict, Any, List, Optional

# Import centralized configuration
from config import API_HOST, API_PORT, DEBUG, USE_MISTRAL, CURRENT_MODEL

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_engine.model_loader import model_loader
from ai_engine.query_processor import process_tax_query, preprocess_query
from ai_engine.validation import validate_query, validate_ai_response


# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Tax Law Assistant",
    description="API for processing tax law queries using AI",
    version="0.1.0"
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React development server
        "http://localhost:8000",     # FastAPI UI
        "http://localhost:8501",     # Streamlit
        "https://taxai-app.vercel.app"  # Production frontend (when deployed)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Request and response models
class QueryRequest(BaseModel):
    query: str
    context: Optional[List[str]] = None

class QueryResponse(BaseModel):
    response: str
    citations: List[str]
    confidence_score: float
    processing_time: float


# Initialize model at startup
@app.on_event("startup")
async def startup_event():
    # Print environment mode and selected model
    print(f"Starting with USE_MISTRAL={USE_MISTRAL}")
    print(f"Selected model: {CURRENT_MODEL}")
    
    # Load model in background to avoid blocking startup
    model_loader.load_model()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is operational."""
    return {"status": "healthy", "model_loaded": hasattr(model_loader, 'model') and model_loader.model is not None}


# Tax query processing endpoint
@app.post("/api/v1/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a tax law query and return AI-generated response.
    
    Args:
        request: The QueryRequest object containing the tax query
        
    Returns:
        QueryResponse with AI-generated answer and metadata
    """
    try:
        # Validate user input
        is_valid, error_message = validate_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Verify model is loaded
        if not hasattr(model_loader, 'model') or model_loader.model is None:
            raise HTTPException(status_code=503, 
                               detail="AI model is still loading. Please try again in a moment.")
        
        # Track processing time
        start_time = time.time()
        
        # Process the query
        result = process_tax_query(request.query, request.context)
        
        # Validate the AI response
        is_valid_response, response_error = validate_ai_response(result)
        if not is_valid_response:
            raise HTTPException(status_code=422, 
                               detail=response_error or "Invalid or incomplete AI response generated.")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Build response
        return {
            "response": result["response"],
            "citations": result["citations"],
            "confidence_score": result["confidence_score"],
            "processing_time": processing_time
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes and details
        raise
        
    except ValueError as ve:
        # Handle value errors (like model not loaded)
        print(f"Value error processing query: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
        
    except Exception as e:
        # Log the error (would use proper logging in production)
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, 
                          detail="An unexpected error occurred while processing your tax query. Please try again later.")


# Basic UI redirect (optional)
@app.get("/")
async def root():
    """Root endpoint that provides basic API information."""
    return {
        "message": "Tax Law AI API is running",
        "docs_url": "/docs",
        "health_check": "/health",
        "query_endpoint": "/api/v1/query"
    }


if __name__ == "__main__":
    import uvicorn
    # Run the app with uvicorn when script is executed directly
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=DEBUG)
