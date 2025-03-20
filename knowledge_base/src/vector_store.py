"""
Module for managing the vector database using ChromaDB.
This module provides functionality to store and retrieve tax law document embeddings.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .schema import TaxLawMetadata
from .embedding import EmbeddingGenerator


logger = logging.getLogger(__name__)


class TaxLawVectorStore:
    """Vector store for tax law documents using ChromaDB."""
    
    def __init__(
        self, 
        persist_directory: str,
        collection_name: str = "tax_law_documents",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the tax law vector store.
        
        Args:
            persist_directory: Directory where ChromaDB will persist data
            collection_name: Name of the ChromaDB collection
            embedding_model: Name of the embedding model to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client with persistence
        logger.info(f"Initializing ChromaDB with persistence directory: {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        
        # Get or create collection
        self._initialize_collection()
        
    def _initialize_collection(self):
        """Initialize or get the ChromaDB collection."""
        try:
            # Try to get the existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Retrieved existing collection: {self.collection_name}")
            logger.info(f"Collection count: {self.collection.count()}")
        except Exception as e:
            # Collection doesn't exist or another error occurred
            logger.info(f"Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Tax law documents and their embeddings"}
            )
    
    def add_document(
        self, 
        document_id: str,
        text: str, 
        metadata: TaxLawMetadata,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> List[str]:
        """
        Add a document to the vector store.
        
        Args:
            document_id: Unique identifier for the document
            text: The text content of the document
            metadata: Metadata for the document
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of IDs for the chunks added to the collection
        """
        # Ensure document_id in metadata matches the provided ID
        metadata.document_id = document_id
        
        # Chunk the document
        chunks = self.embedding_generator.chunk_document(
            document=text,
            chunk_size=chunk_size,
            overlap=chunk_overlap
        )
        
        # Generate chunk IDs
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Generate embeddings for each chunk
        embeddings = self.embedding_generator.generate_embeddings(chunks)
        
        # Convert metadata to dictionary and add chunk information
        metadata_dict = metadata.to_dict()
        
        # Create metadata for each chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata_dict.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_total"] = len(chunks)
            chunk_metadata["chunk_content_preview"] = chunk[:100] + "..." if len(chunk) > 100 else chunk
            metadatas.append(chunk_metadata)
        
        # Add chunks to the collection
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"Added document {document_id} with {len(chunks)} chunks to the collection")
        return chunk_ids
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for documents similar to the query.
        
        Args:
            query: The search query
            n_results: Number of results to return
            filter_criteria: Optional filter to apply to the search
            
        Returns:
            Dictionary containing search results
        """
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Perform the search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_criteria
        )
        
        return results
    
    def get_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document ID.
        
        Args:
            document_id: The ID of the document to retrieve
            
        Returns:
            List of chunks with their embeddings and metadata
        """
        # Query for all chunks with the given document_id
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        return results
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document and all its chunks from the collection.
        
        Args:
            document_id: The ID of the document to delete
        """
        # Delete all chunks with the given document_id
        self.collection.delete(
            where={"document_id": document_id}
        )
        
        logger.info(f"Deleted document {document_id} from the collection")
