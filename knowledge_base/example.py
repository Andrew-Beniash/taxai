"""
Example script demonstrating how to use the Tax Law Knowledge Base.
"""
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base.src.knowledge_base import TaxLawKnowledgeBase
from knowledge_base.src.schema import TaxLawMetadata
from datetime import date


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Example demonstrating knowledge base operations."""
    # Initialize knowledge base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb = TaxLawKnowledgeBase(base_directory=base_dir)
    
    # Example 1: Add a sample document with custom metadata
    sample_text_path = os.path.join(base_dir, "documents", "sample_irs_pub.txt")
    
    # Ensure the documents directory exists
    os.makedirs(os.path.join(base_dir, "documents"), exist_ok=True)
    
    # Create a sample document if it doesn't exist
    if not os.path.exists(sample_text_path):
        with open(sample_text_path, "w") as f:
            f.write("""IRS Publication 535 (2023), Business Expenses
        
For use in preparing 2023 Returns

Section 1. What's New
For tax years beginning in 2023, the maximum section 179 expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of section 179 property placed in service during the tax year exceeds $2,890,000.

Section 2. Introduction
This publication discusses common business expenses and explains what is and is not deductible. The general rules for deducting business expenses are discussed in the opening chapter. The chapters that follow cover specific expenses and list other publications and forms you may need.

Section 3. Deducting Business Expenses
You can deduct the cost of operating your business. These costs are known as business expenses and include:
- Rent
- Utilities
- Office supplies
- Employee salaries
- Business travel
- Business use of your car
- Business entertainment (limited)
""")
    
    # Add the document to the knowledge base with custom metadata
    custom_metadata = {
        "title": "IRS Publication 535 (2023)",
        "source": "Internal Revenue Service",
        "document_type": "Publication",
        "jurisdiction": "Federal",
        "publication_date": date(2023, 1, 15),
        "tags": ["business expenses", "deductions", "section 179"]
    }
    
    chunk_ids = kb.add_document(
        file_path="sample_irs_pub.txt",
        custom_metadata=custom_metadata
    )
    
    print(f"Added document with {len(chunk_ids)} chunks")
    
    # Example 2: Search the knowledge base
    query = "What is the maximum section 179 deduction for 2023?"
    results = kb.search(query, n_results=2)
    
    print("\nSearch Results:")
    for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"\nResult {i+1}:")
        print(f"Document: {metadata.get('title', 'Unknown')}")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Content: {doc[:200]}...")
    
    # Example 3: List all documents in the knowledge base
    documents = kb.list_documents()
    
    print("\nAll Documents in Knowledge Base:")
    for doc in documents:
        print(f"- {doc.get('title', 'Unknown')} (ID: {doc.get('document_id', 'Unknown')})")
    
    print("\nKnowledge Base setup complete! You can now add more documents and search for tax law information.")


if __name__ == "__main__":
    main()
