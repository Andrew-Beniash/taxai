"""
Test script for AI query processing integration.

This script tests the AI model integration with the RAG system
by processing a sample tax law query and printing the result.
"""

import logging
from app.ai.model_manager import generate_ai_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run a test query through the AI model"""
    
    # Sample tax law query
    test_query = "What are the tax deductions available for small businesses?"
    
    logger.info(f"Processing test query: {test_query}")
    
    try:
        # Generate AI response
        response = generate_ai_response(test_query)
        
        # Print the results
        print("\n" + "="*80)
        print(f"QUERY: {test_query}")
        print("="*80)
        print(f"RESPONSE: {response['response']}")
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
        print("="*80)
        
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()
