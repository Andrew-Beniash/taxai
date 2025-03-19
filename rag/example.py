"""
Example script for using the Tax Law RAG system.

This script demonstrates how to ingest tax law documents and query them using the RAG system.
"""

import logging
import os
from typing import List, Dict, Any
from rag_system import TaxLawRAG
from preprocessing import prepare_document_for_indexing, preprocess_irs_publication

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample tax law documents - in a real system, these would be loaded from files
SAMPLE_DOCUMENTS = [
    {
        "id": "irs-section-179",
        "title": "Section 179 Deduction",
        "content": """
        Section 179 allows taxpayers to deduct the cost of certain property as an expense when the 
        property is placed in service. For tax years beginning in 2023, the maximum section 179 
        expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of 
        section 179 property placed in service during the tax year exceeds $2,890,000.
        
        Section 179 property includes most tangible personal property such as machinery and equipment
        purchased for use in a trade or business, and, if elected, qualified real property. Section 179
        property also includes off-the-shelf computer software and qualified improvement property.
        """,
        "source": "IRS Publication 946",
        "year": 2023
    },
    {
        "id": "irs-bonus-depreciation",
        "title": "Bonus Depreciation",
        "content": """
        IRC §168(k) provides for 100% additional first-year depreciation deduction for qualified 
        property acquired and placed in service after September 27, 2017, and before January 1, 2023.
        
        For tax years beginning in 2023, the bonus depreciation percentage is reduced to 80%. The bonus 
        depreciation percentage will be reduced further by 20% each year until it is fully phased out:
        - 60% for property placed in service in 2024
        - 40% for property placed in service in 2025
        - 20% for property placed in service in 2026
        
        Qualified property includes tangible personal property with a recovery period of 20 years or less,
        certain computer software, qualified film and television productions, and qualified improvement property.
        """,
        "source": "IRS Publication 946",
        "year": 2023
    },
    {
        "id": "irs-home-office-deduction",
        "title": "Home Office Deduction",
        "content": """
        You may be able to deduct expenses for the business use of your home if you use part of your home:
        - Exclusively and regularly as your principal place of business;
        - Exclusively and regularly as a place where you meet clients, customers, or patients in the normal course of your business;
        - As a separate structure used exclusively and regularly for your business;
        - On a regular basis for storage of inventory or product samples; or
        - For rental use.
        
        You can calculate the home office deduction using either the:
        1. Regular method - deduct the business percentage of actual expenses (mortgage interest, insurance, utilities, repairs, etc.); or
        2. Simplified method - deduct $5 per square foot of the home used for business (maximum 300 square feet).
        
        Self-employed individuals claim this deduction on Schedule C (Form 1040). Employees cannot claim this deduction for tax years 2018 through 2025.
        """,
        "source": "IRS Publication 587",
        "year": 2023
    }
]


def prepare_and_ingest_documents(rag_system: TaxLawRAG, documents: List[Dict[str, Any]]) -> None:
    """
    Prepare and ingest sample tax law documents into the RAG system.
    
    Args:
        rag_system: The RAG system instance
        documents: List of documents to ingest
    """
    for doc in documents:
        # Preprocess the content if it's an IRS publication
        preprocessed_content = preprocess_irs_publication(doc["content"])
        
        # Prepare metadata
        metadata = {
            "title": doc.get("title", ""),
            "source": doc.get("source", ""),
            "year": doc.get("year", "")
        }
        
        # Prepare document for indexing (chunk and extract entities)
        indexable_chunks = prepare_document_for_indexing(
            doc_id=doc["id"],
            text=preprocessed_content,
            metadata=metadata
        )
        
        # Index the document chunks
        rag_system.index_documents(indexable_chunks)
        
        logger.info(f"Indexed document '{doc['title']}' with {len(indexable_chunks)} chunks")


def run_sample_queries(rag_system: TaxLawRAG) -> None:
    """
    Run sample tax law queries to demonstrate the RAG system.
    
    Args:
        rag_system: The RAG system instance
    """
    sample_queries = [
        "What is the maximum Section 179 deduction for 2023?",
        "How does bonus depreciation work?",
        "What are the requirements for a home office deduction?",
        "What percentage of bonus depreciation can I take in 2024?",
        "Can employees claim home office deductions?"
    ]
    
    for query in sample_queries:
        print("\n" + "="*80)
        print(f"Query: {query}")
        print("="*80)
        
        # Search for relevant documents
        results = rag_system.search(query, n_results=2)
        
        if not results:
            print("No relevant documents found.")
            continue
        
        # Display results
        print(f"Found {len(results)} relevant documents:\n")
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"Title: {result['metadata'].get('title', 'Unknown')}")
            print(f"Source: {result['metadata'].get('source', 'Unknown')}")
            print(f"Content: {result['content'][:200]}...")
            print()


def main():
    """Main function to run the example."""
    # Ensure the data directory exists
    os.makedirs("./data", exist_ok=True)
    
    # Initialize the RAG system
    rag = TaxLawRAG(db_path="./data/tax_law_db")
    
    # Check if the collection is empty (first run)
    doc_count = rag.get_document_count()
    logger.info(f"Current document count: {doc_count}")
    
    if doc_count == 0:
        logger.info("Ingesting sample tax law documents...")
        prepare_and_ingest_documents(rag, SAMPLE_DOCUMENTS)
    
    # Run sample queries
    run_sample_queries(rag)


if __name__ == "__main__":
    main()
