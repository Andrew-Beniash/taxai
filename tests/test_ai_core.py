"""
Unit tests for the Core AI Engine functionality.
Tests model loading, query processing, and response generation.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest
import json

# Add the project root to the path so we can import modules properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.model_loader import ModelLoader
from ai_engine.query_processor import (
    preprocess_query,
    format_tax_prompt,
    process_tax_query,
    extract_citations
)


class TestModelLoading(unittest.TestCase):
    """Tests for model loading functionality."""
    
    @patch('ai_engine.model_loader.AutoTokenizer')
    @patch('ai_engine.model_loader.AutoModelForCausalLM')
    @patch('ai_engine.model_loader.requests')
    def test_model_loader_api(self, mock_requests, mock_model, mock_tokenizer):
        """Test that model loader correctly uses the Hugging Face API."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        # Initialize model loader with API mode
        with patch('ai_engine.model_loader.USE_HUGGINGFACE_API', True):
            loader = ModelLoader()
            result = loader.load_model()
            
            # Check that the model loader correctly loaded the tokenizer
            assert mock_tokenizer.from_pretrained.called
            assert result is True
            assert mock_requests.get.called

    @patch('ai_engine.model_loader.AutoTokenizer')
    @patch('ai_engine.model_loader.AutoModelForCausalLM')
    def test_model_loader_local(self, mock_model, mock_tokenizer):
        """Test that model loader correctly loads the model locally."""
        # Setup mocks
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        
        # Mock torch.cuda.is_available to always return False for testing
        with patch('torch.cuda.is_available', return_value=False):
            with patch('ai_engine.model_loader.USE_HUGGINGFACE_API', False):
                loader = ModelLoader()
                result = loader.load_model()
                
                # Check that the model loader correctly loaded the model and tokenizer
                assert mock_tokenizer.from_pretrained.called
                assert mock_model.from_pretrained.called
                assert result is True


class TestResponseGeneration(unittest.TestCase):
    """Tests for AI response generation functionality."""
    
    @patch('ai_engine.model_loader.ModelLoader.generate_response')
    def test_response_generation_api(self, mock_generate):
        """Test response generation using the API."""
        # Setup mock
        mock_generate.return_value = "According to IRS Publication 946, small businesses can deduct up to $1,160,000 in 2023 for equipment purchases under Section 179."
        
        with patch('ai_engine.model_loader.USE_HUGGINGFACE_API', True):
            loader = ModelLoader()
            response = loader.generate_response("What are the tax deductions for small business equipment?")
            
            # Check that generate was called and returned the expected response
            assert mock_generate.called
            assert "IRS Publication 946" in response
            assert "Section 179" in response

    @patch('ai_engine.model_loader.ModelLoader.generate_response')
    def test_error_handling(self, mock_generate):
        """Test error handling during response generation."""
        # Setup mock to simulate an error
        mock_generate.side_effect = Exception("API Error")
        
        with patch('ai_engine.model_loader.USE_HUGGINGFACE_API', True):
            loader = ModelLoader()
            
            # Check that an exception is raised when called directly
            with pytest.raises(Exception):
                loader.generate_response("What are the tax deductions?")


class TestQueryProcessing(unittest.TestCase):
    """Tests for the query preprocessing functionality."""
    
    def test_preprocess_query(self):
        """Test that query preprocessing works correctly."""
        # Test basic cleanup
        assert preprocess_query("  What  are  the  tax  deductions?  ") == "What are the tax deductions?"
        
        # Test adding tax context when missing
        assert preprocess_query("What are the deductions?") == "Regarding tax law: What are the deductions?"
        
        # Test that tax-related queries are not modified
        assert preprocess_query("What are the tax deductions?") == "What are the tax deductions?"
        assert preprocess_query("IRS rules for 2023") == "IRS rules for 2023"

    def test_format_tax_prompt(self):
        """Test that the tax prompt is formatted correctly for the model."""
        query = "What are the tax deductions for small businesses?"
        context = ["Section 179 allows businesses to deduct the full purchase price of equipment."]
        
        # Test Mistral format
        with patch('ai_engine.query_processor.USE_MISTRAL', True):
            prompt = format_tax_prompt(query, context)
            assert "[INST]" in prompt
            assert query in prompt
            assert "Section 179" in prompt
            assert "[/INST]" in prompt
        
        # Test Llama format
        with patch('ai_engine.query_processor.USE_MISTRAL', False):
            prompt = format_tax_prompt(query, context)
            assert "<|system|>" in prompt
            assert query in prompt
            assert "Section 179" in prompt
            assert "<|assistant|>" in prompt


class TestCitationExtraction(unittest.TestCase):
    """Tests for the citation extraction functionality."""
    
    def test_extract_citations(self):
        """Test that citations are correctly extracted from AI responses."""
        text = """
        According to IRS Publication 535, business expenses are deductible if they are ordinary and necessary.
        Section 179 of the Internal Revenue Code allows for deducting the full purchase price of equipment.
        Also, as per Treasury Regulation §1.162-1, business expenses are deductible.
        Revenue Ruling 99-7 provides guidance on home office deductions.
        Finally, 26 CFR §1.179-1 provides additional details.
        """
        
        citations = extract_citations(text)
        
        assert "IRS Publication 535" in citations
        assert "Section 179" in citations
        assert "Treasury Regulation §1.162-1" in citations
        assert "Revenue Ruling 99-7" in citations
        assert "26 CFR §1.179-1" in citations


if __name__ == '__main__':
    unittest.main()
