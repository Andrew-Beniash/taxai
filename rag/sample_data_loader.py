"""
Sample Data Loader for Tax Law RAG System

This module loads sample tax law documents into the RAG system
for testing and demonstration purposes.
"""

import logging
from rag.rag_system import TaxLawRAG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample tax law documents
SAMPLE_DOCUMENTS = [
    {
        "id": "irs-section-179",
        "content": """
        Section 179 allows taxpayers to deduct the cost of certain property as an expense when the 
        property is placed in service. For tax years beginning in 2023, the maximum section 179 
        expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of 
        section 179 property placed in service during the tax year exceeds $2,890,000.
        
        The Section 179 deduction applies to tangible personal property such as machinery and equipment 
        purchased for use in a trade or business, and if the taxpayer elects, qualified real property.
        """,
        "metadata": {
            "source": "IRS Publication 946",
            "year": 2023,
            "title": "Section 179 Deduction",
            "url": "https://www.irs.gov/publications/p946"
        }
    },
    {
        "id": "small-business-deduction",
        "content": """
        Small businesses can generally deduct ordinary and necessary business expenses. An ordinary expense 
        is one that is common and accepted in your industry. A necessary expense is one that is helpful and 
        appropriate for your business.
        
        Common small business deductions include:
        - Business use of your home or car
        - Salaries and wages for employees
        - Rent for business property
        - Interest on business loans
        - Insurance for your business
        - Retirement plans
        - Business taxes and licenses
        - Business travel, meals, and entertainment (with limitations)
        - Business interest and bank fees
        - Advertising and marketing
        """,
        "metadata": {
            "source": "IRS Small Business Guide",
            "year": 2023,
            "title": "Small Business Tax Deductions",
            "url": "https://www.irs.gov/businesses/small-businesses-self-employed"
        }
    },
    {
        "id": "corporate-tax-rates",
        "content": """
        For tax years beginning after December 31, 2017, the Tax Cuts and Jobs Act replaced the graduated 
        corporate tax structure with a flat 21% corporate tax rate. This flat rate applies to most corporations, 
        regardless of income level.
        
        S corporations generally don't pay income tax at the corporate level. Instead, income and losses 
        are passed through to shareholders, who report them on their personal tax returns.
        """,
        "metadata": {
            "source": "IRS Corporate Tax Guide",
            "year": 2023,
            "title": "Corporate Tax Rates",
            "url": "https://www.irs.gov/corporations"
        }
    },
    {
        "id": "home-office-deduction",
        "content": """
        If you use part of your home for business, you may be able to deduct expenses for the business 
        use of your home. The home office deduction is available for homeowners and renters.
        
        To qualify for the deduction, you must use part of your home:
        - Exclusively and regularly as your principal place of business,
        - Exclusively and regularly as a place where you meet clients or customers in the normal course of business, or
        - On a regular basis for certain storage use.
        
        You can calculate the home office deduction using either the:
        - Regular method (calculating actual expenses), or
        - Simplified method (standard deduction of $5 per square foot, up to 300 square feet).
        """,
        "metadata": {
            "source": "IRS Publication 587",
            "year": 2023,
            "title": "Business Use of Your Home",
            "url": "https://www.irs.gov/publications/p587"
        }
    },
    {
        "id": "depreciation-basics",
        "content": """
        Depreciation is an annual income tax deduction that allows you to recover the cost or other basis 
        of certain property over the time you use the property. It is an allowance for the wear and tear, 
        deterioration, or obsolescence of the property.
        
        Most types of tangible property (except land), such as buildings, machinery, vehicles, furniture, 
        and equipment are depreciable. Likewise, certain intangible property, such as patents, copyrights, 
        and computer software is depreciable.
        
        The Modified Accelerated Cost Recovery System (MACRS) is the proper depreciation method for most property. 
        MACRS consists of two depreciation systems: the General Depreciation System (GDS) and the 
        Alternative Depreciation System (ADS).
        """,
        "metadata": {
            "source": "IRS Publication 946",
            "year": 2023,
            "title": "How to Depreciate Property",
            "url": "https://www.irs.gov/publications/p946"
        }
    }
]

def load_sample_data(rag_system=None):
    """
    Load sample tax law documents into the RAG system.
    
    Args:
        rag_system: Optional TaxLawRAG instance. If None, creates a new one.
    
    Returns:
        The TaxLawRAG instance with sample data loaded.
    """
    # Create or use provided RAG system
    if rag_system is None:
        logger.info("Creating new RAG system")
        rag_system = TaxLawRAG()
    
    # Get current document count
    initial_count = rag_system.get_document_count()
    logger.info(f"Initial document count: {initial_count}")
    
    # Index each sample document
    for doc in SAMPLE_DOCUMENTS:
        try:
            logger.info(f"Indexing document: {doc['id']}")
            rag_system.index_document(
                doc_id=doc["id"],
                content=doc["content"],
                metadata=doc["metadata"]
            )
        except Exception as e:
            logger.error(f"Error indexing document {doc['id']}: {str(e)}")
    
    # Verify documents were added
    final_count = rag_system.get_document_count()
    logger.info(f"Final document count: {final_count}")
    logger.info(f"Added {final_count - initial_count} documents")
    
    return rag_system

# Allow running this module directly
if __name__ == "__main__":
    logger.info("Loading sample tax law documents into RAG system")
    rag = load_sample_data()
    
    # Test a query
    test_query = "What deductions are available for a home office?"
    results = rag.search(test_query)
    
    print(f"\nQuery: {test_query}")
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Document ID: {result['id']}")
        print(f"Content: {result['content'][:150]}...")
        print(f"Source: {result['metadata'].get('source', 'Unknown')}")
        if result.get('distance') is not None:
            print(f"Distance: {result['distance']}")
