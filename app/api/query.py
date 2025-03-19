from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from app.models.api_models import QueryRequest, QueryResponse, Citation
from app.ai.model_manager import generate_ai_response

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
async def process_query(request: QueryRequest):
    """
    Process a tax law query and return AI-generated response with citations
    """
    # Input validation
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    logger.info(f"Processing tax law query: {request.query}")
    
    try:
        # Process the query using our AI model
        response = generate_ai_response(request.query)
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
        return generate_ai_response(query)
    except Exception as e:
        logger.error(f"Test query processing failed: {str(e)}")
        return {"error": str(e)}

# For manual testing
if __name__ == "__main__":
    test_query = "What are the tax deductions for small businesses?"
    result = test_query_processing(test_query)
    print("Query Result:", result)
