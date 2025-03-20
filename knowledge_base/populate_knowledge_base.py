"""
Script to populate the Tax Law Knowledge Base with sample documents.
"""
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base.src.knowledge_base import TaxLawKnowledgeBase
from knowledge_base.src.data_collector import TaxLawDataCollector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Download sample tax law documents and populate the knowledge base."""
    # Initialize paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    documents_dir = os.path.join(base_dir, "documents")
    
    # Ensure the documents directory exists
    os.makedirs(documents_dir, exist_ok=True)
    
    # Initialize knowledge base
    kb = TaxLawKnowledgeBase(base_directory=base_dir)
    
    # Initialize data collector
    collector = TaxLawDataCollector(documents_directory=documents_dir)
    
    print("Step 1: Creating sample tax law documents...")
    # Create sample tax law documents (when network access is limited)
    sample_files = collector.create_sample_tax_law_documents()
    
    try:
        print("Step 2: Downloading common IRS publications...")
        # Try to download IRS publications (if network allows)
        download_files = collector.download_common_irs_publications()
        all_files = sample_files + download_files
    except Exception as e:
        logger.warning(f"Could not download IRS publications: {str(e)}")
        logger.warning("Using only sample documents instead.")
        all_files = sample_files
    
    print(f"Step 3: Adding {len(all_files)} documents to the knowledge base...")
    # Add all documents to the knowledge base
    for file_path in all_files:
        # Get the relative path from the documents directory
        rel_path = os.path.relpath(file_path, documents_dir)
        logger.info(f"Processing {rel_path}...")
        
        try:
            # Check if metadata file exists
            json_path = os.path.splitext(file_path)[0] + ".json"
            if os.path.exists(json_path):
                logger.info(f"Using metadata from {os.path.basename(json_path)}")
            
            # Add to knowledge base
            chunk_ids = kb.add_document(file_path=rel_path)
            logger.info(f"Added document with {len(chunk_ids)} chunks")
        except Exception as e:
            logger.error(f"Error processing {rel_path}: {str(e)}")
    
    print("Step 4: Displaying all documents in the knowledge base...")
    # List all documents in the knowledge base
    documents = kb.list_documents()
    
    print("\nAll Documents in Knowledge Base:")
    for doc in documents:
        print(f"- {doc.get('title', 'Unknown')} (ID: {doc.get('document_id', 'Unknown')})")
    
    print("\nStep 5: Testing search functionality...")
    # Test search functionality
    test_queries = [
        "What is the maximum section 179 deduction for 2023?",
        "How do I calculate home office deductions?",
        "What business meal expenses are deductible?",
        "What are the requirements for depreciating property?"
    ]
    
    for query in test_queries:
        print(f"\nSearch Query: '{query}'")
        results = kb.search(query, n_results=1)
        
        if results["documents"] and results["documents"][0]:
            print("Top Result:")
            doc = results["documents"][0][0]
            metadata = results["metadatas"][0][0]
            print(f"Source: {metadata.get('title', 'Unknown')}")
            print(f"Content Preview: {doc[:150]}...")
        else:
            print("No results found.")
    
    print("\nKnowledge Base population complete! The system is ready for tax law queries.")


if __name__ == "__main__":
    main()
