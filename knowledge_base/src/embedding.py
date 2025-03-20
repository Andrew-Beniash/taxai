"""
Module for generating embeddings for tax law documents.
This module provides functionality to convert text documents into vector embeddings.
"""
from typing import List, Union, Dict, Any
import os
import logging
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Class to generate embeddings for tax law documents."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator with a Sentence Transformer model.
        
        Args:
            model_name: Name of the pre-trained model to use for embeddings.
                       Default is "all-MiniLM-L6-v2" which provides a good
                       balance between quality and performance.
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Embedding model loaded successfully with embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text document.
        
        Args:
            text: The text content to embed
            
        Returns:
            A list of floats representing the document embedding
        """
        return self.model.encode(text).tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple text documents.
        
        Args:
            texts: List of text contents to embed
            
        Returns:
            A list of embeddings, where each embedding is a list of floats
        """
        return [self.model.encode(text).tolist() for text in texts]

    def chunk_document(self, document: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split a document into smaller chunks for better embedding.
        
        Args:
            document: The full document text
            chunk_size: Maximum number of characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of document chunks
        """
        chunks = []
        start = 0
        
        while start < len(document):
            # Find the end of the current chunk
            end = min(start + chunk_size, len(document))
            
            # If we're not at the end of the document, try to find a period or newline to break at
            if end < len(document):
                # Look for a good breaking point (period followed by space, or newline)
                for i in range(end, max(start, end - 100), -1):
                    if document[i-1:i+1] in ['. ', '.\n']:
                        end = i
                        break
            
            # Add the chunk to our list
            chunks.append(document[start:end])
            
            # Calculate the start of the next chunk with overlap
            start = end - overlap
            
        return chunks
