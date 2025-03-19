import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.retrieval import TaxLawVectorStore, TaxLawRetriever

def main():
    """Example of using the tax law retrieval system."""
    # Sample tax law documents
    tax_laws = [
        {
            "id": "irs-section-179",
            "content": "Section 179 of the Internal Revenue Code allows taxpayers to deduct the cost of certain types of property on their income taxes as an expense, rather than requiring the cost of the property to be capitalized and depreciated. This property is generally limited to tangible, depreciable, personal property which is acquired by purchase for use in the active conduct of a trade or business.",
            "metadata": {
                "source": "IRS Code",
                "section": "179",
                "title": "Section 179 Deduction"
            }
        },
        {
            "id": "irs-section-162",
            "content": "IRC Section 162 allows business owners to deduct ordinary and necessary business expenses. To be deductible, a business expense must be both ordinary and necessary. An ordinary expense is one that is common and accepted in your trade or business. A necessary expense is one that is helpful and appropriate for your trade or business.",
            "metadata": {
                "source": "IRS Code",
                "section": "162",
                "title": "Business Expenses"
            }
        },
        {
            "id": "irs-publication-535",
            "content": "Publication 535 discusses common business expenses and explains what is and is not deductible. The general rules for deducting business expenses are discussed in the opening chapter. The chapters that follow cover specific expenses and list other publications and forms you may need.",
            "metadata": {
                "source": "IRS Publication",
                "publication": "535",
                "title": "Business Expenses"
            }
        }
    ]
    
    # Initialize vector store and add documents
    vector_store = TaxLawVectorStore()
    vector_store.add_documents(tax_laws)
    
    # Initialize retriever
    retriever = TaxLawRetriever()
    
    # Test with a sample query
    query = "What are the tax deductions for small business equipment purchases?"
    results = retriever.retrieve_tax_laws(query)
    
    # Print results
    print(f"Query: {query}\n")
    print("Retrieved tax law references:")
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['metadata'].get('title', 'Untitled')}")
        print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
        print(f"   Relevance score: {result['relevance_score']:.4f}")
        print(f"   Keyword score: {result['keyword_score']:.4f}")
        print(f"   Content: {result['content'][:150]}...")

if __name__ == "__main__":
    main()
