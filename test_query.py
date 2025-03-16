"""
Test script for the AI query processing.
This script allows for simple testing of the tax law query functionality.
"""

import requests
import json
import time
import argparse

def test_api_query(query, api_url="http://localhost:8000"):
    """Test the query API endpoint."""
    
    endpoint = f"{api_url}/api/v1/query"
    
    payload = {
        "query": query
    }
    
    print(f"Sending query: {query}")
    print(f"To endpoint: {endpoint}")
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload)
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*50)
            print("QUERY RESULT:")
            print("="*50)
            print(f"Response: {result['response']}")
            print("\nCitations:")
            for citation in result['citations']:
                print(f"- {citation}")
            print("\nMetadata:")
            print(f"- Confidence score: {result['confidence_score']}")
            print(f"- Processing time: {result['processing_time']:.2f} seconds")
            print(f"- Total request time: {request_time:.2f} seconds")
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the tax law query API")
    parser.add_argument("--query", type=str, default="What are the tax deductions available for small businesses?",
                       help="Tax law query to test")
    parser.add_argument("--url", type=str, default="http://localhost:8000",
                       help="API URL")
    
    args = parser.parse_args()
    test_api_query(args.query, args.url)
