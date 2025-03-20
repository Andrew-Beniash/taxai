"""
Test script for Hugging Face Inference API integration.

This script tests the AI model integration with the RAG system
using the Hugging Face Inference API instead of loading the model locally.
This is a lighter-weight alternative for testing.
"""

import logging
import sys
from app.ai.inference_api_manager import generate_ai_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run a test query through the Inference API"""
    
    # Sample tax law query
    test_query = "What are the tax deductions available for small businesses?"
    
    logger.info(f"Processing test query through Inference API: {test_query}")
    
    try:
        # Generate AI response with fallback to mock if API is unavailable
        response = generate_ai_response(test_query)
        
        # Print the results
        print("\n" + "="*80)
        print(f"QUERY: {test_query}")
        print("="*80)
        
        # Indicate if this is a mock response
        if response.get("is_mock"):
            print("RESPONSE (MOCK - API UNAVAILABLE): ")
        else:
            print("RESPONSE (via Inference API): ")
            
        print(response['response'])
        print("-"*80)
        print("CITATIONS:")
        
        if response.get("citations"):
            for i, citation in enumerate(response["citations"], 1):
                print(f"[{i}] {citation['source']}")
                if citation.get("url"):
                    print(f"    URL: {citation['url']}")
                if citation.get("text"):
                    print(f"    Text: {citation['text']}")
                print()
        else:
            print("No citations provided.")
        
        print("-"*80)
        print(f"Confidence Score: {response.get('confidence_score', 'N/A')}")
        
        if response.get("is_mock"):
            print("\nNOTE: The Hugging Face Inference API is currently unavailable.")
            print("This is a mock response generated for testing purposes.")
            print("Try again later when the API is available.")
        
        print("="*80)
        
        logger.info("Test completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        
        # Print helpful instructions for authentication errors
        if "Authentication failed" in str(e) or "Unauthorized" in str(e):
            print("\n" + "!"*80)
            print("AUTHENTICATION ERROR: Unable to access the Hugging Face Inference API")
            print("!"*80)
            print("\nTo fix this issue:")
            print("1. Get a Hugging Face token from: https://huggingface.co/settings/tokens")
            print("2. Set it as an environment variable:")
            print("   export HUGGINGFACE_TOKEN=\"your_token_here\"")
            print("3. Or add it to your .env file:")
            print("   HUGGINGFACE_TOKEN=your_token_here")
            print("\nSee the guide in docs/huggingface_authentication.md for more details.")
            print("!"*80)
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
