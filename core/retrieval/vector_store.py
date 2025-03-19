import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TaxLawVectorStore:
    """Class for managing the vector database of tax law documents."""
    
    def __init__(self, collection_name: str = "tax_laws", embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the tax law vector store with ChromaDB and embedding model.
        
        Args:
            collection_name: Name of the ChromaDB collection to store tax law documents
            embedding_model_name: Name of the sentence transformer model for embeddings
        """
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path="./db")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(collection_name)
            logger.info(f"Created new collection: {collection_name}")
        
        # Load the embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)
        logger.info(f"Loaded embedding model: {embedding_model_name}")
    
    def add_document(self, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a tax law document to the vector store.
        
        Args:
            document_id: Unique identifier for the document
            content: Text content of the document
            metadata: Additional metadata for the document (source, publication date, etc.)
        """
        if metadata is None:
            metadata = {}
        
        # Generate embedding for the document
        embedding = self.embedding_model.encode(content)
        
        # Add document to ChromaDB
        self.collection.add(
            ids=[document_id],
            embeddings=[embedding.tolist()],
            documents=[content],
            metadatas=[metadata]
        )
        
        logger.info(f"Added document {document_id} to vector store")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add multiple tax law documents to the vector store.
        
        Args:
            documents: List of document dictionaries with id, content, and metadata
        """
        ids = []
        contents = []
        metadatas = []
        embeddings = []
        
        for doc in documents:
            ids.append(doc["id"])
            contents.append(doc["content"])
            metadatas.append(doc.get("metadata", {}))
            
            # Generate embedding for the document
            embedding = self.embedding_model.encode(doc["content"])
            embeddings.append(embedding.tolist())
        
        # Add documents to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the vector store.
        
        Args:
            document_id: Unique identifier for the document to delete
        """
        self.collection.delete(ids=[document_id])
        logger.info(f"Deleted document {document_id} from vector store")
    
    def update_document(self, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update an existing document in the vector store.
        
        Args:
            document_id: Unique identifier for the document
            content: Updated text content of the document
            metadata: Updated metadata for the document
        """
        # Delete the existing document
        self.delete_document(document_id)
        
        # Add the updated document
        self.add_document(document_id, content, metadata)
        
        logger.info(f"Updated document {document_id} in vector store")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "document_count": count,
            "collection_name": self.collection.name
        }
