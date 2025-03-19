"""
Tests for the query processor module of the AI-powered tax law system.
Tests the full pipeline from query processing to response generation.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest

# Add the project root to the path so we can import modules properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.query_processor import (
    preprocess_query,
    format_tax_prompt,
    process_tax_query,
    extract_citations
)


class TestQueryProcessor(unittest.TestCase):
    """Tests for the query processor functionality."""
    
    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_process_tax_query(self, mock_retrieve, mock_generate):
        """Test the complete tax query processing pipeline."""
        # Setup mocks
        mock_retrieve.return_value = [
            "Section 179 allows businesses to deduct the full purchase price of equipment in 2023 up to $1,160,000"
        ]
        mock_generate.return_value = "According to IRC § 179, businesses can deduct up to $1,160,000 for equipment purchases in 2023."
        
        # Process a sample query
        result = process_tax_query("What equipment deductions are available for small businesses?")
        
        # Verify the result structure
        assert "query" in result
        assert "response" in result
        assert "citations" in result
        assert "confidence_score" in result
        
        # Verify the mock functions were called
        assert mock_retrieve.called
        assert mock_generate.called
        
        # Verify the content of the response
        assert "IRC § 179" in result["response"]
        assert "IRC § 179" in result["citations"]

    @patch('ai_engine.model_loader.model_loader.generate_response')
    def test_process_tax_query_with_context(self, mock_generate):
        """Test query processing with provided context."""
        # Setup mock
        mock_generate.return_value = "According to the provided information, businesses can deduct equipment purchases."
        
        # Provide context directly
        context = ["Treasury Regulation §1.179-1 allows for the deduction of equipment."]
        result = process_tax_query("What equipment deductions are available?", context=context)
        
        # Verify the result uses the provided context
        assert mock_generate.called
        assert "query" in result
        assert "response" in result
        
        # Ensure the model_loader.generate_response was called with a prompt containing our context
        called_args = mock_generate.call_args[0][0]
        assert "Treasury Regulation §1.179-1" in called_args

    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_process_tax_query_with_invalid_response(self, mock_retrieve, mock_generate):
        """Test handling of invalid or unexpected AI responses."""
        # Setup mocks to return empty or malformed responses
        mock_retrieve.return_value = []
        mock_generate.return_value = ""
        
        # Process the query
        result = process_tax_query("Invalid query")
        
        # Verify that even with empty response, the function returns a properly structured result
        assert "query" in result
        assert "response" in result
        assert "citations" in result
        assert isinstance(result["citations"], list)


class TestPerformance(unittest.TestCase):
    """Performance tests for query processing."""
    
    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_query_processing_speed(self, mock_retrieve, mock_generate):
        """Test query processing speed to ensure it's within acceptable limits."""
        import time
        
        # Setup mocks
        mock_retrieve.return_value = ["Sample tax law context"]
        mock_generate.return_value = "Sample response with IRC § 123 citation."
        
        # Measure processing time
        start_time = time.time()
        process_tax_query("What are the tax deductions for small businesses?")
        end_time = time.time()
        
        # Assert that processing time is reasonable (less than 500ms without actual API call)
        # This is more of a benchmark than a true test since we're mocking the API
        processing_time = end_time - start_time
        assert processing_time < 0.5, f"Query processing took {processing_time:.2f}s, which exceeds the benchmark of 0.5s"


class TestEdgeCases(unittest.TestCase):
    """Tests for handling edge cases in query processing."""
    
    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_empty_query(self, mock_retrieve, mock_generate):
        """Test handling of empty queries."""
        # Setup mocks
        mock_retrieve.return_value = []
        mock_generate.return_value = "I need more information to answer your tax question."
        
        # Process an empty query
        result = process_tax_query("")
        
        # Verify that the query is properly preprocessed
        assert result["query"] == ""
        assert "response" in result

    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_very_long_query(self, mock_retrieve, mock_generate):
        """Test handling of very long queries."""
        # Setup mocks
        mock_retrieve.return_value = ["Relevant tax law"]
        mock_generate.return_value = "Response to long query."
        
        # Create a very long query (over 1000 characters)
        long_query = "Tax question " * 100
        
        # Process the long query
        result = process_tax_query(long_query)
        
        # Verify that the query was processed without truncation
        assert result["query"] == long_query
        assert mock_generate.called


if __name__ == '__main__':
    unittest.main()
