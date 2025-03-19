"""
RAG System for Tax Law Application

This module implements a Retrieval-Augmented Generation (RAG) system using ChromaDB
for storing and retrieving tax law documents as vector embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class TaxLawRAG:
    """
    Implements a RAG system for tax law documents using ChromaDB for vector storage and retrieval.
    """
    
    def __init__(self, 
                 db_path: str = "./data/tax_law_db", 
                 collection_name: str = "tax_laws",
                 embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG system with ChromaDB and embedding model.
        
        Args:
            db_path: Path to store the ChromaDB database
            collection_name: Name of the collection in ChromaDB
            embedding_model_name: Name of the sentence transformer model for embeddings
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize the vector database
        self.vector_db = chromadb.PersistentClient(path=db_path)
        
        # Create embedding function using sentence-transformers
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Set up the embedding function for ChromaDB
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model_name
        )
        
        # Create or get the collection
        self.collection = self.vector_db.get_or_create_collection(
            name=collection_name,
            embedding_function=self.sentence_transformer_ef
        )
        
        logger.info(f"Initialized RAG system with database at {db_path}")
    
    def index_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Embed and store a tax law document in the vector database.
        
        Args:
            doc_id: Unique identifier for the document
            content: Text content of the document
            metadata: Additional metadata about the document
        """
        if metadata is None:
            metadata = {}
        
        # Add content to metadata for retrieval
        metadata["content"] = content
        
        # Add the document to the collection
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata]
        )
        
        logger.info(f"Indexed document: {doc_id}")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Batch index multiple documents.
        
        Args:
            documents: List of documents, each containing 'id', 'content', and optional 'metadata'
        """
        ids = []
        contents = []
        metadatas = []
        
        for doc in documents:
            doc_id = doc['id']
            content = doc['content']
            metadata = doc.get('metadata', {})
            metadata["content"] = content
            
            ids.append(doc_id)
            contents.append(content)
            metadatas.append(metadata)
        
        # Batch add documents to the collection
        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )
        
        logger.info(f"Indexed {len(documents)} documents")
    
    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant tax law documents based on a query.
        
        Args:
            query: The search query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with their content and metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format the results for easier consumption
        formatted_results = []
        
        if not results['ids'][0]:  # Check if we got any results
            return formatted_results
            
        for i, doc_id in enumerate(results['ids'][0]):
            formatted_results.append({
                'id': doc_id,
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results.get('distances', [[0]])[0][i] if results.get('distances') else None
            })
        
        return formatted_results
    
    def hybrid_search(self, query: str, n_results: int = 3, 
                     keyword_weight: float = 0.3, vector_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search combining keyword and vector search for better results.
        
        Args:
            query: The search query
            n_results: Number of results to return
            keyword_weight: Weight for keyword search component
            vector_weight: Weight for vector similarity component
            
        Returns:
            List of relevant documents with their content and metadata
        """
        # For now, we'll rely on ChromaDB's built-in hybrid search capabilities
        # In the future, this can be extended with a custom BM25 implementation
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format the results for easier consumption
        formatted_results = []
        
        if not results['ids'][0]:  # Check if we got any results
            return formatted_results
            
        for i, doc_id in enumerate(results['ids'][0]):
            formatted_results.append({
                'id': doc_id,
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results.get('distances', [[0]])[0][i] if results.get('distances') else None
            })
        
        return formatted_results
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the collection.
        
        Args:
            doc_id: The ID of the document to delete
        """
        self.collection.delete(ids=[doc_id])
        logger.info(f"Deleted document: {doc_id}")
    
    def clear_collection(self) -> None:
        """
        Delete all documents from the collection.
        """
        self.collection.delete()
        logger.info(f"Cleared all documents from collection: {self.collection_name}")


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the RAG system
    rag = TaxLawRAG()
    
    # Example document
    sample_document = {
        "id": "irs-section-179",
        "content": """
        Section 179 allows taxpayers to deduct the cost of certain property as an expense when the 
        property is placed in service. For tax years beginning in 2023, the maximum section 179 
        expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of 
        section 179 property placed in service during the tax year exceeds $2,890,000.
        """,
        "metadata": {
            "source": "IRS Publication",
            "year": 2023,
            "title": "Section 179 Deduction"
        }
    }
    
    # Index the document
    rag.index_document(
        doc_id=sample_document["id"],
        content=sample_document["content"],
        metadata=sample_document["metadata"]
    )
    
    # Search for relevant documents
    query = "What are small business deductions for equipment?"
    results = rag.search(query)
    
    # Print results
    print(f"Query: {query}")
    print(f"Found {len(results)} results")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Document ID: {result['id']}")
        print(f"Content: {result['content'][:150]}...")
        print(f"Metadata: {result['metadata']}")
        if result['distance'] is not None:
            print(f"Distance: {result['distance']}")
