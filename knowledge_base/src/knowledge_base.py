"""
Main module for the Tax Law Knowledge Base.
This module provides a unified interface for the knowledge base operations.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .vector_store import TaxLawVectorStore
from .document_loader import DocumentLoader
from .preprocessor import TaxDocumentPreprocessor
from .schema import TaxLawMetadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaxLawKnowledgeBase:
    """
    Main class for interacting with the Tax Law Knowledge Base.
    """
    
    def __init__(
        self,
        base_directory: str,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the Tax Law Knowledge Base.
        
        Args:
            base_directory: Base directory for knowledge base data
            embedding_model: Name of the embedding model to use
        """
        self.base_directory = base_directory
        
        # Set up directories
        self.vector_db_dir = os.path.join(base_directory, "vector_db")
        self.documents_dir = os.path.join(base_directory, "documents")
        
        # Ensure directories exist
        os.makedirs(self.vector_db_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)
        
        # Initialize components
        self.vector_store = TaxLawVectorStore(
            persist_directory=self.vector_db_dir,
            embedding_model=embedding_model
        )
        self.document_loader = DocumentLoader(documents_directory=self.documents_dir)
        self.preprocessor = TaxDocumentPreprocessor()
        
        logger.info(f"Initialized Tax Law Knowledge Base at {base_directory}")
    
    def add_document(
        self,
        file_path: str,
        custom_metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> List[str]:
        """
        Add a document to the knowledge base.
        
        Args:
            file_path: Path to the document file
            custom_metadata: Optional custom metadata to override extracted metadata
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of chunk IDs for the added document
        """
        logger.info(f"Adding document: {file_path}")
        
        # Load and preprocess the document
        text, metadata_dict = self.document_loader.load_document(file_path)
        processed_text = self.preprocessor.preprocess(text)
        
        # Update metadata with custom values if provided
        if custom_metadata:
            metadata_dict.update(custom_metadata)
        
        # Create metadata object
        metadata = self.document_loader.create_metadata(metadata_dict)
        
        # Generate a document ID if not provided
        document_id = metadata.document_id
        
        # Add to vector store
        chunk_ids = self.vector_store.add_document(
            document_id=document_id,
            text=processed_text,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        logger.info(f"Successfully added document {document_id} with {len(chunk_ids)} chunks")
        return chunk_ids
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for documents related to a query.
        
        Args:
            query: The search query
            n_results: Number of results to return
            filter_criteria: Optional filter to apply to the search
            
        Returns:
            Dictionary containing search results
        """
        logger.info(f"Searching for: {query}")
        return self.vector_store.search(query, n_results, filter_criteria)
    
    def get_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve a document by its ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            List of document chunks with metadata
        """
        logger.info(f"Retrieving document: {document_id}")
        return self.vector_store.get_document(document_id)
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the knowledge base.
        
        Args:
            document_id: ID of the document to delete
        """
        logger.info(f"Deleting document: {document_id}")
        self.vector_store.delete_document(document_id)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the knowledge base.
        
        Returns:
            List of document metadata
        """
        logger.info("Listing all documents")
        # Get unique document IDs
        collection_data = self.vector_store.collection.get()
        
        if not collection_data["metadatas"]:
            return []
        
        # Extract unique document IDs from the chunks
        unique_docs = {}
        for metadata in collection_data["metadatas"]:
            doc_id = metadata.get("document_id")
            if doc_id and doc_id not in unique_docs:
                # Store only the first chunk metadata for each document
                unique_docs[doc_id] = metadata
        
        return list(unique_docs.values())
    
    def batch_add_documents(
        self,
        directory: Optional[str] = None,
        file_extensions: List[str] = ['.pdf', '.txt', '.json'],
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> Dict[str, List[str]]:
        """
        Add multiple documents from a directory to the knowledge base.
        
        Args:
            directory: Directory containing documents (default: documents_dir)
            file_extensions: List of file extensions to include
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dictionary mapping document IDs to their chunk IDs
        """
        directory = directory or self.documents_dir
        logger.info(f"Batch adding documents from: {directory}")
        
        results = {}
        files_processed = 0
        
        # Walk through the directory
        for root, _, files in os.walk(directory):
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.documents_dir)
                    
                    try:
                        chunk_ids = self.add_document(
                            file_path=rel_path,
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap
                        )
                        doc_id = os.path.basename(file_path)
                        results[doc_id] = chunk_ids
                        files_processed += 1
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
        
        logger.info(f"Batch processing complete. {files_processed} files processed.")
        return results
