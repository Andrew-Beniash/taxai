"""
Hugging Face Inference API Manager for Tax Law Application

This module provides an alternative to loading the full model locally
by using the Hugging Face Inference API. This is useful for testing
or when running on hardware with limited resources.

Usage requires a Hugging Face API token with proper permissions.
"""

import logging
import os
import json
import requests
from typing import Dict, List, Any, Optional
from app.config import MODEL_PATH
from rag.rag_system import TaxLawRAG
from core_ai_engine.prompt_engineering import create_tax_query_prompt, format_ai_response_with_citations
from app.ai.mock_response import create_mock_query_response
from app.ai.response_formatter import format_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables 
_rag_system = None

def _get_huggingface_token():
    """
    Get Hugging Face API token from environment variable or .env file
    """
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        logger.warning("HUGGINGFACE_TOKEN not found in environment variables")
        # Try to read it from a token file
        token_path = os.path.expanduser("~/.huggingface/token")
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                hf_token = f.read().strip()
                logger.info("Found Hugging Face token in ~/.huggingface/token")
    
    return hf_token

def get_rag_system():
    """
    Initialize and return the RAG system for tax law document retrieval.
    """
    global _rag_system
    if _rag_system is None:
        logger.info("Initializing RAG system")
        try:
            _rag_system = TaxLawRAG()
            logger.info(f"RAG system initialized with {_rag_system.get_document_count()} documents")
        except Exception as e:
            logger.error(f"Error initializing RAG system: {str(e)}")
            raise RuntimeError(f"Failed to initialize RAG system: {str(e)}")
    
    return _rag_system

def generate_with_inference_api(prompt: str, fallback_to_mock: bool = True) -> str:
    """
    Generate text using the Hugging Face Inference API
    
    Args:
        prompt: The text prompt to send to the model
        fallback_to_mock: Whether to use mock responses when the API is unavailable
        
    Returns:
        The generated text response
    """
    # Get Hugging Face token
    hf_token = _get_huggingface_token()
    if not hf_token:
        raise ValueError(
            "HUGGINGFACE_TOKEN not found. Please set this environment variable "
            "or add it to your .env file."
        )
    
    # Define the API endpoint
    api_url = f"https://api-inference.huggingface.co/models/{MODEL_PATH}"
    
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the payload
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.2,
            "do_sample": True
        }
    }
    
    # Make the API request
    try:
        logger.info(f"Sending request to Inference API: {api_url}")
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse the response
        result = response.json()
        
        # Extract the generated text
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
            
            # If the response includes the prompt, remove it
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
                
            return generated_text
        else:
            logger.error(f"Unexpected API response format: {result}")
            return "Error: Unexpected response from the Inference API"
    
    except requests.exceptions.HTTPError as e:
        # Handle common API errors
        error_msg = f"Inference API error: {str(e)}"
        
        if response.status_code == 401:
            error_msg = "Authentication failed. Please check your Hugging Face API token."
        elif response.status_code == 403:
            error_msg = "Access denied. Your account may not have access to this model."
        elif response.status_code == 429:
            error_msg = "Too many requests. You may be rate-limited by the Hugging Face API."
        elif response.status_code == 503:
            error_msg = "Hugging Face Inference API is temporarily unavailable."
            
            # If we should fallback to mock responses
            if fallback_to_mock:
                logger.warning("Falling back to mock response due to API unavailability")
                return None  # Signal to use mock response
        
        logger.error(error_msg)
        
        # Propagate the error if not falling back to mock
        if not fallback_to_mock or response.status_code not in [503, 429]:
            raise RuntimeError(error_msg)
        return None
    
    except Exception as e:
        logger.error(f"Error calling Inference API: {str(e)}")
        
        # If we should fallback to mock responses
        if fallback_to_mock:
            logger.warning("Falling back to mock response due to exception")
            return None  # Signal to use mock response
            
        raise RuntimeError(f"Failed to call Inference API: {str(e)}")

def generate_ai_response(query: str, use_mock: bool = False) -> Dict[str, Any]:
    """
    Generate an AI response to a tax law query using the Hugging Face Inference API.
    
    Args:
        query: The tax law query to process
        use_mock: Force using mock responses instead of the API
        
    Returns:
        Dict containing the response, citations, and confidence score
    """
    try:
        # Get RAG system
        rag = get_rag_system()
        
        # Step 1: Retrieve relevant tax law documents
        logger.info(f"Retrieving context for query: {query}")
        context_docs = rag.search(query, n_results=3)
        
        if not context_docs:
            logger.warning(f"No relevant documents found for query: {query}")
            # Fallback to handle the case with no context
            context_docs = [{
                "content": "No specific tax law reference found.",
                "metadata": {"source": "System Note"}
            }]
        
        # If we're using mock responses, skip the API call
        if use_mock:
            logger.info("Using mock response as requested")
            return create_mock_query_response(query, context_docs)
        
        # Step 2: Create prompt with retrieved context
        logger.info("Creating prompt with context")
        prompt = create_tax_query_prompt(query, context_docs)
        
        # Step 3: Generate response using the Inference API
        logger.info("Generating AI response via Inference API")
        response_text = generate_with_inference_api(prompt)
        
        # If API call failed or returned None, use mock response
        if response_text is None:
            logger.info("API unavailable, using mock response")
            return create_mock_query_response(query, context_docs)
        
        # Extract the answer part (after the prompt)
        if "ANSWER:" in prompt and "ANSWER:" in response_text:
            response_text = response_text.split("ANSWER:", 1)[1].strip()
        
        # Step 4: Format response with citations
        formatted_response = format_ai_response_with_citations(response_text, context_docs)
        
        # Step 5: Use our enhanced response formatter for better citation handling
        enhanced_response = format_response(response_text, context_docs)
        
        # Return the enhanced formatted response
        return enhanced_response
    
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        
        # Try using mock response as a fallback for any errors
        try:
            logger.warning("Attempting to use mock response due to error")
            return create_mock_query_response(query, context_docs if 'context_docs' in locals() else [])
        except:
            # If even the mock response fails, propagate the original error
            raise RuntimeError(f"Failed to generate AI response: {str(e)}")

def initialize():
    """
    Initialize the RAG system.
    """
    try:
        # Load RAG system
        get_rag_system()
        return True
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        return False
