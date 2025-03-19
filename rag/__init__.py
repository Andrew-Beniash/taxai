"""
RAG (Retrieval-Augmented Generation) package for the Tax Law Application.

This package provides tools for storing, indexing, and retrieving tax law documents
using vector embeddings and semantic search.
"""

from .rag_system import TaxLawRAG

__all__ = ['TaxLawRAG']
