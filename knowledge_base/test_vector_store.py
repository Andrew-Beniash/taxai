"""
Script to test the vector database functionality for storing tax law documents.
This script verifies that ChromaDB is properly set up and can store and retrieve embeddings.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import date
import time

# Add the parent directory to the Python path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base.src.vector_store import TaxLawVectorStore
from knowledge_base.src.schema import TaxLawMetadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_vector_store():
    """
    Test the vector store functionality.
    
    This function tests:
    1. Connection to ChromaDB
    2. Adding documents with metadata
    3. Searching for documents
    4. Retrieving and deleting documents
    """
    # Initialize paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vector_db_dir = os.path.join(base_dir, "vector_db")
    
    # Ensure vector_db directory exists
    os.makedirs(vector_db_dir, exist_ok=True)
    
    # Initialize vector store
    logger.info("Initializing ChromaDB vector store...")
    vector_store = TaxLawVectorStore(
        persist_directory=vector_db_dir,
        collection_name="test_collection",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    # Create test documents
    test_documents = [
        {
            "id": "test_doc_1",
            "title": "Business Expenses",
            "content": """
            For tax years beginning in 2023, the maximum section 179 expense deduction is $1,160,000.
            This limit is reduced by the amount by which the cost of section 179 property placed in
            service during the tax year exceeds $2,890,000.
            """
        },
        {
            "id": "test_doc_2",
            "title": "Home Office Deduction",
            "content": """
            The home office deduction allows qualifying taxpayers to deduct certain expenses
            related to using their home for business purposes. To qualify, you must use
            part of your home exclusively and regularly for business.
            """
        }
    ]
    
    # Test adding documents
    logger.info("Testing document addition...")
    for doc in test_documents:
        # Create metadata
        metadata = TaxLawMetadata(
            title=doc["title"],
            source="Test Source",
            document_id=doc["id"],
            publication_date=date.today(),
            jurisdiction="Federal",
            document_type="Test",
            tags=["test"],
            url=None
        )
        
        # Add document
        chunk_ids = vector_store.add_document(
            document_id=doc["id"],
            text=doc["content"],
            metadata=metadata,
            chunk_size=512,
            chunk_overlap=50
        )
        
        logger.info(f"Added document '{doc['title']}' with {len(chunk_ids)} chunks")
    
    # Test collection count
    document_count = vector_store.collection.count()
    logger.info(f"Collection contains {document_count} chunks")
    
    # Wait a moment for ChromaDB to process embeddings
    time.sleep(1)
    
    # Test search functionality
    logger.info("Testing search functionality...")
    search_queries = [
        "What are section 179 deductions?",
        "How do I qualify for home office deductions?"
    ]
    
    for query in search_queries:
        logger.info(f"Searching for: '{query}'")
        results = vector_store.search(query, n_results=1)
        
        if results["documents"] and results["documents"][0]:
            doc = results["documents"][0][0]
            metadata = results["metadatas"][0][0]
            logger.info(f"Found document: '{metadata.get('title')}'")
            logger.info(f"Content preview: {doc[:50]}...")
        else:
            logger.error(f"No results found for query: '{query}'")
    
    # Test document retrieval
    logger.info("Testing document retrieval...")
    for doc in test_documents:
        doc_results = vector_store.get_document(doc["id"])
        logger.info(f"Retrieved document '{doc['id']}' with {len(doc_results['ids'])} chunks")
    
    # Test document deletion
    logger.info("Testing document deletion...")
    for doc in test_documents:
        vector_store.delete_document(doc["id"])
        logger.info(f"Deleted document '{doc['id']}'")
    
    # Verify deletion
    document_count = vector_store.collection.count()
    logger.info(f"Collection now contains {document_count} chunks")
    
    if document_count == 0:
        logger.info("All test documents successfully deleted")
    else:
        logger.warning(f"Document deletion test failed, {document_count} chunks remain")
    
    logger.info("Vector store testing complete!")


if __name__ == "__main__":
    print("Testing ChromaDB vector store for tax law documents...")
    test_vector_store()
    print("Testing complete!")
