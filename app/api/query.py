from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging
from app.models.api_models import QueryRequest, QueryResponse, Citation

# Try to import from model_manager (for full model)
try:
    from app.ai.model_manager import generate_ai_response as generate_with_full_model
except ImportError:
    generate_with_full_model = None

# Import the inference API version
from app.ai.inference_api_manager import generate_ai_response as generate_with_inference_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for tax queries
router = APIRouter(
    prefix="/api",
    tags=["tax-law"],
    responses={404: {"description": "Not found"}},
)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tax Law AI API is operational"}

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest, 
    use_mock: Optional[bool] = Query(False, description="Force using mock responses for testing")
):
    """
    Process a tax law query and return AI-generated response with citations
    """
    # Input validation
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    logger.info(f"Processing tax law query: {request.query}")
    
    try:
        # Determine which model generator to use
        if generate_with_full_model is not None and not use_mock:
            # Try the full model first
            logger.info("Using full local model for query processing")
            response = generate_with_full_model(request.query)
        else:
            # Fall back to inference API
            logger.info("Using Inference API for query processing")
            response = generate_with_inference_api(request.query, use_mock=use_mock)
        
        # Add a note if this is a mock response
        if response.get("is_mock", False):
            logger.info("Generated mock response (API unavailable)")
            
        logger.info("Query processed successfully")
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Function for debugging/manual testing
def test_query_processing(query: str) -> Dict[str, Any]:
    """
    For debugging: Process a tax law query and return the result
    """
    try:
        # Try the inference API first as it's lighter
        return generate_with_inference_api(query)
    except Exception as e:
        logger.error(f"Test query processing failed: {str(e)}")
        return {"error": str(e)}

# For manual testing
if __name__ == "__main__":
    test_query = "What are the tax deductions for small businesses?"
    result = test_query_processing(test_query)
    print("Query Result:", result)
