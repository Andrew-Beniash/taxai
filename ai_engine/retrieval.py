"""
Retrieval component for the AI-powered tax law system.
This module integrates the RAG system with the AI query processor.
"""

import os
import sys
from typing import List, Dict, Any

# Import centralized configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the RAG system
from rag.rag_system import TaxLawRAG

# Create a singleton instance of the RAG system
_rag_instance = None

def get_rag_system(reload=False) -> TaxLawRAG:
    """
    Get or initialize the RAG system.
    
    Args:
        reload: Whether to force reloading the RAG system
        
    Returns:
        An instance of TaxLawRAG
    """
    global _rag_instance
    
    if _rag_instance is None or reload:
        _rag_instance = TaxLawRAG(
            db_path="./data/tax_law_db",
            collection_name="tax_laws",
            embedding_model_name="all-MiniLM-L6-v2"
        )
    
    return _rag_instance

def retrieve_tax_laws(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve relevant tax law documents based on the query.
    
    Args:
        query: The tax-related query
        n_results: Number of relevant documents to retrieve
        
    Returns:
        List of relevant tax law references
    """
    rag = get_rag_system()
    
    # Use hybrid search to get better results
    results = rag.hybrid_search(query, n_results=n_results)
    
    # Format for LLM context
    return results

def retrieve_context_for_query(query: str, n_results: int = 3) -> List[str]:
    """
    Retrieve relevant tax law context as formatted strings ready for the LLM.
    
    Args:
        query: The tax-related query
        n_results: Number of relevant documents to retrieve
        
    Returns:
        List of formatted context strings
    """
    # Get the raw document results
    results = retrieve_tax_laws(query, n_results)
    
    # Format the documents for LLM consumption
    formatted_context = []
    
    for result in results:
        # Get document content
        content = result['content']
        
        # Get metadata (if available)
        metadata = result.get('metadata', {})
        source = metadata.get('source', 'Unknown source')
        title = metadata.get('title', 'Untitled')
        year = metadata.get('year', '')
        
        # Format the reference with metadata
        reference = f"{title} ({source}, {year}): {content}"
        formatted_context.append(reference)
    
    return formatted_context
