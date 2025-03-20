"""
Simple script for searching the Tax Law Knowledge Base.
This script provides a command-line interface for querying tax law information.
"""
import os
import sys
import logging
import argparse
from pathlib import Path
import textwrap

# Add the parent directory to the Python path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base.src.knowledge_base import TaxLawKnowledgeBase


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_results(results, max_width=100):
    """
    Format search results for display.
    
    Args:
        results: Search results from the knowledge base
        max_width: Maximum width for text wrapping
        
    Returns:
        Formatted string with search results
    """
    if not results["documents"] or not results["documents"][0]:
        return "No results found."
    
    formatted_output = []
    
    for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        # Format document metadata
        title = metadata.get("title", "Unknown Document")
        source = metadata.get("source", "Unknown Source")
        doc_id = metadata.get("document_id", "Unknown ID")
        
        # Format content with wrapped text
        content = doc.strip()
        wrapped_content = textwrap.fill(content, width=max_width)
        
        # Assemble the formatted result
        result = f"\n{'='*max_width}\n"
        result += f"RESULT {i+1}\n"
        result += f"{'='*max_width}\n"
        result += f"Title: {title}\n"
        result += f"Source: {source}\n"
        result += f"Document ID: {doc_id}\n"
        result += f"{'-'*max_width}\n"
        result += f"{wrapped_content}\n"
        
        formatted_output.append(result)
    
    return "\n".join(formatted_output)


def interactive_search(kb, max_results=3):
    """
    Run an interactive search session.
    
    Args:
        kb: The knowledge base instance
        max_results: Maximum number of results to display
    """
    print("\n" + "="*60)
    print("TAX LAW KNOWLEDGE BASE SEARCH")
    print("="*60)
    print("Enter 'exit' or 'quit' to end the session.")
    print("="*60 + "\n")
    
    while True:
        # Get user query
        query = input("\nEnter your tax law question: ")
        
        # Check for exit command
        if query.lower() in ['exit', 'quit']:
            print("\nExiting search. Goodbye!")
            break
        
        # Skip empty queries
        if not query.strip():
            continue
        
        try:
            # Search the knowledge base
            results = kb.search(query, n_results=max_results)
            
            # Display results
            print("\nSearch Results:")
            print(format_results(results))
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            print(f"\nAn error occurred: {str(e)}")


def main():
    """Main function to run the tax law search tool."""
    parser = argparse.ArgumentParser(description="Search for tax law information.")
    parser.add_argument("--query", "-q", type=str, help="The search query (if not provided, runs in interactive mode)")
    parser.add_argument("--results", "-r", type=int, default=3, help="Number of results to display (default: 3)")
    parser.add_argument("--directory", "-d", type=str, help="Path to knowledge base directory")
    
    args = parser.parse_args()
    
    # Determine knowledge base directory
    if args.directory:
        base_dir = args.directory
    else:
        # Use default path
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize knowledge base
    kb = TaxLawKnowledgeBase(base_directory=base_dir)
    
    # Check if the knowledge base is empty
    documents = kb.list_documents()
    if not documents:
        print("WARNING: The knowledge base appears to be empty. Run populate_knowledge_base.py first.")
        return
    
    if args.query:
        # Single query mode
        results = kb.search(args.query, n_results=args.results)
        print(format_results(results))
    else:
        # Interactive mode
        interactive_search(kb, max_results=args.results)


if __name__ == "__main__":
    main()
