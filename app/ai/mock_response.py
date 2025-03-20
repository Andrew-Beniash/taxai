"""
Mock Response Generator for Tax Law Application

This module provides mock AI responses for development and testing purposes.
Used when the actual AI model or Inference API is unavailable.
"""

import logging
import random
from typing import Dict, List, Any
from app.ai.response_formatter import format_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_mock_response(query: str, context_docs: List[Dict[str, Any]]) -> str:
    """
    Generate a mock response for a tax law query based on retrieved context.
    
    Args:
        query: The tax law query
        context_docs: The retrieved context documents
        
    Returns:
        A mock AI-generated response
    """
    logger.info("Generating mock response")
    
    # Extract key terms from the query for context-aware responses
    query_lower = query.lower()
    
    # Collection of generic tax-related phrases to use in responses
    intro_phrases = [
        "Based on the tax regulations I found,",
        "According to the relevant tax laws,",
        "The tax code provides that",
        "Tax regulations specify that",
        "As outlined in the relevant tax guidance,"
    ]
    
    # Default response if no context matches
    default_response = (
        f"{random.choice(intro_phrases)} general tax principles apply. "
        "For specific advice on your situation, please consult with a qualified tax professional."
    )
    
    # If we have context docs, use them to craft a more relevant response
    if context_docs:
        # Summarize content from the first relevant document
        doc_content = context_docs[0].get("content", "")
        doc_source = context_docs[0].get("metadata", {}).get("source", "tax regulations")
        
        # Extract a relevant snippet from the content (first 200 chars)
        snippet = doc_content.strip()[:200].replace("\n", " ")
        
        # Construct a mock response that references the context
        response = (
            f"{random.choice(intro_phrases)} {snippet} "
            f"According to {doc_source} [1], this is generally how the tax treatment works for this type of situation. "
            "However, individual circumstances may vary, and it's advisable to consult with a tax professional "
            "for personalized guidance."
        )
        
        return response
    
    return default_response

def create_mock_query_response(query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a complete mock query response including citations.
    
    Args:
        query: The tax law query
        context_docs: The retrieved context documents
        
    Returns:
        Dict containing the response, citations, and confidence score
    """
    # Generate a mock text response
    response_text = generate_mock_response(query, context_docs)
    
    # Use our enhanced response formatter
    formatted_response = format_response(response_text, context_docs)
    
    # Mark it as a mock response
    formatted_response["is_mock"] = True
    
    # Lower the confidence score for mock responses
    formatted_response["confidence_score"] = min(0.7, formatted_response.get("confidence_score", 0.7))
    
    return formatted_response
