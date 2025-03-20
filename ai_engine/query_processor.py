"""
Query processor for the AI-powered tax law system.
This module handles preprocessing, response generation, and formatting for tax law queries.
"""

import re
import os
import time
import logging
import random
from typing import Dict, Any, List, Optional

# Import retrieval module
from ai_engine.retrieval import retrieve_context_for_query

# Import caching module
from ai_engine.caching import query_cache

# Import centralized configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USE_MISTRAL

from ai_engine.model_loader import model_loader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def preprocess_query(query: str) -> str:
    """
    Preprocess the tax law query before sending to the model.
    
    Args:
        query: The user's tax law question or query
        
    Returns:
        Preprocessed query ready for the LLM
    """
    # Clean up the query text
    query = query.strip()
    
    # Remove multiple spaces
    query = re.sub(r'\s+', ' ', query)
    
    # Add tax-specific context if not present
    if not any(term in query.lower() for term in ['tax', 'irs', 'deduction', 'credit', 'filing']):
        query = f"Regarding tax law: {query}"
    
    return query


def format_tax_prompt(query: str, context: Optional[List[str]] = None) -> str:
    """
    Format the prompt for tax law queries with additional context.
    
    Args:
        query: The preprocessed tax query
        context: Optional list of relevant tax law references to include
        
    Returns:
        A formatted prompt ready for the model
    """
    # Use the globally defined USE_MISTRAL variable
    
    if USE_MISTRAL:
        # Mistral instruction format
        prompt = """<s>[INST] You are a tax law expert assistant providing accurate, helpful information about tax laws, regulations, and IRS policies. Answer tax-related questions with precise, factual information. Include relevant tax code citations and IRS publication references when applicable. Provide clear explanations that are accessible to non-experts.

"""
        
        # Add the query
        prompt += query
        
        # Add context if provided
        if context and len(context) > 0:
            prompt += "\n\nRelevant tax law references:\n"
            for i, ref in enumerate(context):
                prompt += f"{i+1}. {ref}\n"
        
        prompt += "[/INST]" 
    else:
        # Llama 3.1 instruction format
        prompt = """<|system|>
        You are a tax law expert assistant providing accurate, helpful information about tax laws, regulations, and IRS policies. Answer tax-related questions with precise, factual information. Include relevant tax code citations and IRS publication references when applicable. Provide clear explanations that are accessible to non-experts.
        </|system|>

        <|user|>
        """
        
        # Add the query
        prompt += query
        
        # Add context if provided
        if context and len(context) > 0:
            prompt += "\n\nRelevant tax law references:\n"
            for i, ref in enumerate(context):
                prompt += f"{i+1}. {ref}\n"
        
        prompt += "\n</|user|>\n\n<|assistant|>"
    
    return prompt


def process_tax_query(query: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Process a tax-related query and generate an AI response.
    Uses caching to optimize performance for repeated queries.
    
    Args:
        query: The tax question from the user
        context: Optional list of relevant tax law references
        
    Returns:
        Dictionary with the AI response and metadata
        
    Raises:
        ValueError: If the model is not loaded or if the query is invalid
        Exception: For other processing errors
    """
    # Start timing for performance monitoring
    start_time = time.time()
    
    # Validate query before processing
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    # Preprocess the query
    processed_query = preprocess_query(query)
    
    # Try to get response from cache first
    cache_key_context = context if context else "no_context"
    cached_response = query_cache.get(processed_query, cache_key_context)
    
    if cached_response:
        logger.info(f"Cache hit! Retrieved response for query: {processed_query[:50]}...")
        logging.info(f"Response time (cached): {time.time() - start_time:.3f}s")
        return cached_response
    
    # Cache miss - proceed with generating a new response
    logger.info(f"Cache miss. Generating response for query: {processed_query[:50]}...")
    
    # Ensure model is loaded
    if not hasattr(model_loader, 'model') or model_loader.model is None:
        loaded = model_loader.load_model()
        if not loaded:
            raise ValueError("Failed to load AI model. Please try again later.")
    
    # If no context is provided, retrieve relevant tax law references
    try:
        if not context:
            context = retrieve_context_for_query(processed_query)
            if not context:
                logger.warning(f"No relevant tax law references found for query: {processed_query[:50]}...")
                # Continue without context rather than failing
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        # Continue without context rather than failing
        context = []
    
    # Format the prompt with tax-specific instructions
    prompt = format_tax_prompt(processed_query, context)
    
    # Generate response
    try:
        response = model_loader.generate_response(prompt)
        
        if not response or len(response.strip()) < 20:
            logger.warning("Model returned unusually short or empty response")
            response = "I apologize, but I couldn't generate a complete answer to your tax question. Please try rephrasing your question or providing more details."
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        raise Exception(f"Failed to generate AI response: {str(e)}")
    
    # Extract citations if present
    citations = extract_citations(response)
    
    # Calculate confidence score based on response quality
    confidence_score = calculate_confidence_score(response, citations, context)
    
    # Create the final response object
    result = {
        "query": query,
        "response": response,
        "citations": citations,
        "confidence_score": confidence_score,
        "response_time": time.time() - start_time
    }
    
    # Cache the response for future use
    query_cache.set(processed_query, result, cache_key_context)
    
    # Log performance metrics
    logging.info(f"Response time (uncached): {time.time() - start_time:.3f}s")
    
    return result


def extract_citations(text: str) -> List[str]:
    """
    Extract tax law citations from the generated response.
    
    Args:
        text: The AI-generated response
        
    Returns:
        List of extracted citations
    """
    # Validate input
    if not text:
        return []
        
    citation_patterns = [
        r'(IRS Publication \d+[\w\s\-\.]*)',
        r'(Treasury Regulation §[\s\d\.\-]+)',
        r'(IRC §[\s\d\.\-]+)',
        r'(Section \d+[\.\w\s\-]*)',
        r'(\d+ CFR §[\s\d\.\-]+)',
        r'(Revenue Ruling \d+[\-\d]*)',
        r'(Rev\. Proc\. \d+[\-\d]+)',
        r'(Tax Court Case \d+[\-\d\w\s\.]*)',
        r'(IRS Notice \d+[\-\d]*)'
    ]
    
    citations = []
    for pattern in citation_patterns:
        try:
            found = re.findall(pattern, text)
            citations.extend(found)
        except Exception as e:
            # Don't let regex errors crash the citation extraction
            logging.error(f"Error extracting citations with pattern {pattern}: {str(e)}")
            continue
    
    return list(set(citations))  # Remove duplicates


def calculate_confidence_score(response: str, citations: List[str], context: Optional[List[str]] = None) -> float:
    """
    Calculate a confidence score for an AI-generated response based on factors like:
    - Number of citations
    - Response length and structure
    - Presence of uncertainty phrases
    - Consistency with provided context
    
    Args:
        response: The AI-generated tax law response
        citations: List of tax law citations found in the response
        context: Optional tax law references provided as context
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    # Begin with a base score
    score = 0.7
    
    # Adjust based on response length (too short or too long responses might indicate issues)
    response_length = len(response)
    if response_length < 50:
        score -= 0.2  # Very short responses are likely not helpful
    elif 100 <= response_length <= 1000:
        score += 0.1  # Ideal length range
    
    # Adjust based on citation count
    if citations:
        # More citations typically indicate better responses
        citation_bonus = min(len(citations) * 0.05, 0.15)  # Cap at 0.15
        score += citation_bonus
    else:
        # No citations might indicate a less reliable answer
        score -= 0.1
    
    # Check for uncertainty markers that might indicate lower confidence
    uncertainty_phrases = [
        "I'm not sure", 
        "I don't know", 
        "It's unclear",
        "I'm uncertain",
        "I don't have enough information",
        "It's difficult to determine",
        "I cannot provide"
    ]
    
    # Count uncertainty phrases
    uncertainty_count = sum(1 for phrase in uncertainty_phrases if phrase.lower() in response.lower())
    if uncertainty_count > 0:
        score -= min(uncertainty_count * 0.1, 0.3)  # Cap at 0.3 penalty
    
    # If context was provided, check if it was used in the response
    if context and len(context) > 0:
        # Check if any context appears in the response (rough check)
        context_usage = 0
        for ctx in context:
            # Check if significant words from context appear in response
            significant_words = [word for word in ctx.split() if len(word) > 5]
            for word in significant_words[:10]:  # Check up to 10 significant words per context
                if word.lower() in response.lower():
                    context_usage += 1
                    break  # Count each context item only once
        
        # Adjust score based on context usage
        if context_usage > 0:
            context_bonus = min(context_usage * 0.05, 0.1)
            score += context_bonus
    
    # Ensure score is in the valid range [0.0, 1.0]
    score = max(0.0, min(score, 1.0))
    
    return score
