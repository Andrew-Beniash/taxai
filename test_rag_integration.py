"""
Test script to verify the integration of the RAG system with the query API.

Run this script after setting up the system to ensure that RAG retrieval is working.
"""

import time
import os
import requests
import json

# Test loading sample documents into the RAG system
from rag.rag_system import TaxLawRAG

# Set up the RAG system
def setup_sample_data():
    """Load sample tax law documents into the RAG system."""
    rag = TaxLawRAG()
    
    # Sample tax law documents
    sample_documents = [
        {
            "id": "irs-section-179",
            "content": """
            Section 179 allows taxpayers to deduct the cost of certain property as an expense when the 
            property is placed in service. For tax years beginning in 2023, the maximum section 179 
            expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of 
            section 179 property placed in service during the tax year exceeds $2,890,000.
            """,
            "metadata": {
                "source": "IRS Publication",
                "year": 2023,
                "title": "Section 179 Deduction"
            }
        },
        {
            "id": "business-travel-expenses",
            "content": """
            Business travel expenses are the ordinary and necessary expenses of traveling away from home 
            for your business, profession, or job. Generally, you can deduct business travel expenses if 
            you can satisfy two conditions: (1) the expenses must be "ordinary and necessary" and (2) you 
            must be traveling "away from home" for your business.
            """,
            "metadata": {
                "source": "IRS Publication 463",
                "year": 2023,
                "title": "Travel, Gift, and Car Expenses"
            }
        },
        {
            "id": "home-office-deduction",
            "content": """
            You can deduct expenses for the business use of your home if you use part of your home exclusively 
            and regularly: As your principal place of business, or as a place to meet or deal with patients, 
            clients, or customers in the normal course of your business. The percentage of your home devoted 
            to business use determines the percentage of home-related expenses that you can deduct.
            """,
            "metadata": {
                "source": "IRS Publication 587",
                "year": 2023,
                "title": "Business Use of Your Home"
            }
        }
    ]
    
    # Index the documents
    rag.index_documents(sample_documents)
    print(f"Indexed {len(sample_documents)} sample tax law documents")
    
    return rag

# Test the API endpoint
def test_api_query(query):
    """Test the API endpoint with a tax law query."""
    url = "http://localhost:8000/api/v1/query"
    headers = {"Content-Type": "application/json"}
    data = {"query": query}
    
    # Send the request
    print(f"\nSending query: '{query}'")
    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()
    
    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        print(f"Response received in {end_time - start_time:.2f} seconds")
        print(f"\nAI Response:")
        print(result["response"])
        print(f"\nCitations:")
        for citation in result["citations"]:
            print(f"- {citation}")
        print(f"\nConfidence Score: {result['confidence_score']}")
        print(f"Processing Time: {result['processing_time']:.2f} seconds")
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    # Set up sample data
    print("Setting up sample data...")
    rag = setup_sample_data()
    
    # Get document count to verify loading
    doc_count = rag.get_document_count()
    print(f"Vector database contains {doc_count} documents")
    
    # Test API with several queries
    test_queries = [
        "Can I deduct the cost of equipment for my business?",
        "What are the rules for home office deductions?",
        "Are travel expenses tax deductible for business owners?"
    ]
    
    for query in test_queries:
        success = test_api_query(query)
        if not success:
            break
        print("\n" + "-" * 50)
    
    print("\nTest complete!")
