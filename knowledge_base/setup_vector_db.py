"""
Script to set up the vector database for storing tax law document embeddings.
This script initializes the ChromaDB directory structure and tests the connection.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import date

# Add the parent directory to the Python path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base.src.knowledge_base import TaxLawKnowledgeBase
from knowledge_base.src.schema import TaxLawMetadata
from knowledge_base.src.vector_store import TaxLawVectorStore


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_vector_db():
    """
    Set up and initialize the vector database for tax law documents.
    
    This function:
    1. Creates the required directory structure
    2. Initializes a ChromaDB instance
    3. Sets up the metadata schema
    4. Tests the connection with a sample document
    """
    # Initialize paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vector_db_dir = os.path.join(base_dir, "vector_db")
    documents_dir = os.path.join(base_dir, "documents")
    
    # Ensure directories exist
    os.makedirs(vector_db_dir, exist_ok=True)
    os.makedirs(documents_dir, exist_ok=True)
    
    logger.info(f"Created directory structure:")
    logger.info(f"  - Vector DB: {vector_db_dir}")
    logger.info(f"  - Documents: {documents_dir}")
    
    # Initialize vector store
    logger.info("Initializing ChromaDB vector store...")
    vector_store = TaxLawVectorStore(
        persist_directory=vector_db_dir,
        collection_name="tax_law_documents",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    # Test the connection with a sample document
    logger.info("Testing ChromaDB with a sample document...")
    
    # Create a sample tax law document metadata
    sample_metadata = TaxLawMetadata(
        title="Test Tax Document",
        source="Internal Revenue Service",
        document_id="test_document_001",
        publication_date=date.today(),
        jurisdiction="Federal",
        document_type="Test",
        sections=["Test Section"],
        tags=["test", "sample"],
        url=None
    )
    
    # Sample document text
    sample_text = """
    This is a test document for the tax law knowledge base.
    It's used to verify that ChromaDB is set up correctly and can store embeddings.
    """
    
    # Add the sample document to verify everything works
    chunk_ids = vector_store.add_document(
        document_id=sample_metadata.document_id,
        text=sample_text,
        metadata=sample_metadata,
        chunk_size=512,
        chunk_overlap=50
    )
    
    # Test search functionality
    logger.info("Testing search functionality...")
    search_results = vector_store.search("test document", n_results=1)
    
    if search_results["documents"] and search_results["documents"][0]:
        logger.info("Search test successful!")
        doc = search_results["documents"][0][0]
        logger.info(f"Found document: {doc[:50]}...")
    else:
        logger.warning("Search test did not return results. Check ChromaDB setup.")
    
    # Clean up the test document
    logger.info("Cleaning up test document...")
    vector_store.delete_document(sample_metadata.document_id)
    
    # Initialize the knowledge base to verify integration
    logger.info("Initializing knowledge base to verify integration...")
    kb = TaxLawKnowledgeBase(base_directory=base_dir)
    
    # Print completion message
    logger.info("Vector database setup complete!")
    logger.info("You can now run populate_knowledge_base.py to add tax law documents.")
    logger.info("Use TaxLawKnowledgeBase class to interact with the knowledge base.")


if __name__ == "__main__":
    print("Setting up ChromaDB vector database for tax law documents...")
    setup_vector_db()
    print("Setup complete!")
