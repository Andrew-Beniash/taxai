"""
Query processor for the AI-powered tax law system.
This module handles preprocessing, response generation, and formatting for tax law queries.
"""

import re
import os
from typing import Dict, Any, List, Optional

# Import centralized configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USE_MISTRAL

from ai_engine.model_loader import model_loader


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
    
    Args:
        query: The tax question from the user
        context: Optional list of relevant tax law references
        
    Returns:
        Dictionary with the AI response and metadata
    """
    # Ensure model is loaded
    if not hasattr(model_loader, 'model') or model_loader.model is None:
        model_loader.load_model()
    
    # Preprocess the query
    processed_query = preprocess_query(query)
    
    # Format the prompt with tax-specific instructions
    prompt = format_tax_prompt(processed_query, context)
    
    # Generate response
    response = model_loader.generate_response(prompt)
    
    # Extract citations if present (simple regex pattern)
    citations = re.findall(r'(IRS Publication \d+|Section \d+|\d+ U.S.C. § \d+|IRC § \d+)', response)
    
    return {
        "query": query,
        "response": response,
        "citations": citations,
        "confidence_score": 0.85  # Placeholder for now, would be model-specific in production
    }


def extract_citations(text: str) -> List[str]:
    """
    Extract tax law citations from the generated response.
    
    Args:
        text: The AI-generated response
        
    Returns:
        List of extracted citations
    """
    citation_patterns = [
        r'(IRS Publication \d+[\w\s\-\.]*)',
        r'(Treasury Regulation §[\s\d\.\-]+)',
        r'(IRC §[\s\d\.\-]+)',
        r'(Section \d+[\.\w\s\-]*)',
        r'(\d+ CFR §[\s\d\.\-]+)',
        r'(Revenue Ruling \d+[\-\d]*)'
    ]
    
    citations = []
    for pattern in citation_patterns:
        found = re.findall(pattern, text)
        citations.extend(found)
    
    return list(set(citations))  # Remove duplicates
