"""
Tests for the Response Formatter module
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai.response_formatter import format_response, format_inline_citations, calculate_confidence_score


def test_format_response():
    """Test that response formatting works correctly"""
    # Sample test data
    ai_answer = "Small businesses can deduct up to $1,080,000 in qualifying equipment purchases for the 2023 tax year."
    references = [
        {
            "content": "For tax year 2023, the maximum section 179 expense deduction is $1,080,000.",
            "metadata": {
                "source": "IRS Publication 946",
                "url": "https://www.irs.gov/publications/p946"
            }
        },
        {
            "content": "The taxpayer may elect to treat the cost of any section 179 property as an expense which is not chargeable to capital account.",
            "metadata": {
                "source": "Internal Revenue Code § 179"
            }
        }
    ]
    
    # Format the response
    response = format_response(ai_answer, references)
    
    # Assertions
    assert "response" in response
    assert "citations" in response
    assert "confidence_score" in response
    assert len(response["citations"]) == 2
    assert response["citations"][0]["source"] == "IRS Publication 946"
    assert response["citations"][0]["text"].startswith("For tax year 2023")
    assert "url" in response["citations"][0]
    assert response["confidence_score"] > 0


def test_format_inline_citations():
    """Test that inline citation formatting works correctly"""
    # Case 1: No existing citations
    ai_answer = "According to IRS Publication 946, small businesses can deduct up to $1,080,000 in qualifying equipment purchases."
    references = [
        {
            "content": "For tax year 2023, the maximum section 179 expense deduction is $1,080,000.",
            "metadata": {
                "source": "IRS Publication 946"
            }
        }
    ]
    
    formatted = format_inline_citations(ai_answer, references)
    assert "[1]" in formatted
    
    # Case 2: Already has citations
    ai_answer_with_citations = "According to IRS Publication 946 [1], small businesses can deduct up to $1,080,000."
    formatted = format_inline_citations(ai_answer_with_citations, references)
    # Should not add duplicate citations
    assert formatted.count("[1]") == 1


def test_calculate_confidence_score():
    """Test that confidence score calculation works correctly"""
    # Test with no references
    assert calculate_confidence_score("Some response", []) < 0.5
    
    # Test with one reference
    one_ref = [{"content": "Some content", "metadata": {"source": "Some source"}}]
    one_ref_score = calculate_confidence_score("Some response", one_ref)
    assert 0.5 < one_ref_score < 0.7
    
    # Test with official IRS reference (should increase confidence)
    irs_ref = [{"content": "Some content", "metadata": {"source": "IRS Publication 946"}}]
    irs_ref_score = calculate_confidence_score("Some response", irs_ref)
    assert irs_ref_score > one_ref_score
    
    # Test with citation in response (should increase confidence)
    cited_response = "According to IRS Publication 946 [1], small businesses can deduct..."
    cited_score = calculate_confidence_score(cited_response, irs_ref)
    assert cited_score > irs_ref_score


if __name__ == "__main__":
    # Run the tests
    pytest.main(['-xvs', __file__])
