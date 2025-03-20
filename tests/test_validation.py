"""
Test suite for the validation modules in the AI-powered tax law system.
This validates input and response validation functionality.
"""

import sys
import os
import pytest
import requests
from fastapi.testclient import TestClient

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import validation module
from ai_engine.validation import validate_query, validate_ai_response
from main import app

# Create a test client
client = TestClient(app)

def test_validate_query():
    """Test the query validation function."""
    # Valid query
    is_valid, error = validate_query("What are the tax deductions for small businesses?")
    assert is_valid is True
    assert error is None
    
    # Empty query
    is_valid, error = validate_query("")
    assert is_valid is False
    assert "empty" in error.lower()
    
    # Too short query
    is_valid, error = validate_query("Tax?")
    assert is_valid is False
    assert "short" in error.lower()
    
    # Too long query (create a query exceeding 1000 characters)
    long_query = "Tax question " * 100  # 1200 characters
    is_valid, error = validate_query(long_query)
    assert is_valid is False
    assert "long" in error.lower()
    
    # Security risk query
    is_valid, error = validate_query("SELECT * FROM tax_laws;")
    assert is_valid is False
    assert "invalid" in error.lower()


def test_validate_ai_response():
    """Test the AI response validation function."""
    # Valid response
    valid_response = {
        "response": "Small businesses can deduct up to $5,000 in startup costs according to IRS Publication 535.",
        "citations": ["IRS Publication 535"],
        "confidence_score": 0.85
    }
    is_valid, error = validate_ai_response(valid_response)
    assert is_valid is True
    assert error is None
    
    # Empty response
    empty_response = {
        "response": "",
        "citations": [],
        "confidence_score": 0.0
    }
    is_valid, error = validate_ai_response(empty_response)
    assert is_valid is False
    assert "empty" in error.lower()
    
    # Too short response
    short_response = {
        "response": "Yes.",
        "citations": [],
        "confidence_score": 0.3
    }
    is_valid, error = validate_ai_response(short_response)
    assert is_valid is False
    assert "short" in error.lower()
    
    # Low confidence score
    low_confidence = {
        "response": "Small businesses may be eligible for certain deductions.",
        "citations": [],
        "confidence_score": 0.2
    }
    is_valid, error = validate_ai_response(low_confidence)
    assert is_valid is False
    assert "confidence" in error.lower()


def test_api_error_handling():
    """Test API error handling for various scenarios."""
    # Empty query - should return 400
    response = client.post("/api/v1/query", json={"query": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
    
    # Too short query - should return 400
    response = client.post("/api/v1/query", json={"query": "Hi?"})
    assert response.status_code == 400
    assert "short" in response.json()["detail"].lower()
    
    # Security risk query - should return 400
    response = client.post("/api/v1/query", json={"query": "SELECT * FROM tax_laws;"})
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", "test_validation.py"])
