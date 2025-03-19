"""
Document preprocessing utilities for tax law documents.

This module provides functions to preprocess tax law documents before indexing them in the RAG system.
"""

import re
import nltk
from typing import List, Dict, Any, Optional
import logging

# Download necessary NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text from tax law documents.
    
    Args:
        text: Raw text content from a document
        
    Returns:
        Cleaned text ready for embedding
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters, but keep important punctuation for tax documents
    text = re.sub(r'[^\w\s.,;:()\-§&%$]', '', text)
    
    return text


def chunk_document(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split a document into smaller chunks for better embedding and retrieval.
    
    Args:
        text: Document text to chunk
        max_chunk_size: Maximum chunk size in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Clean the text first
    text = clean_text(text)
    
    # If the document is smaller than max chunk size, return as is
    if len(text) <= max_chunk_size:
        return [text]
    
    # Get sentences using NLTK
    sentences = nltk.sent_tokenize(text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed max size, save the chunk and start a new one
        if len(current_chunk) + len(sentence) > max_chunk_size:
            chunks.append(current_chunk)
            
            # Start new chunk with overlap from the previous chunk
            if overlap > 0 and len(current_chunk) > overlap:
                # Find the last space within the overlap region
                overlap_text = current_chunk[-overlap:]
                last_space = overlap_text.rfind(' ')
                
                if last_space != -1:
                    # Start new chunk with overlap
                    current_chunk = current_chunk[-(overlap - last_space):] + " "
                else:
                    current_chunk = ""
            else:
                current_chunk = ""
                
        current_chunk += sentence + " "
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def extract_tax_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract tax-specific entities like section numbers, dollar amounts, and percentages.
    
    Args:
        text: Document text to extract entities from
        
    Returns:
        Dictionary of extracted entities by type
    """
    entities = {
        'section_numbers': [],
        'dollar_amounts': [],
        'percentages': [],
        'tax_years': []
    }
    
    # Extract section numbers (e.g., Section 179, §179)
    section_pattern = r'(?:Section|§)\s*(\d+(?:\.\d+)?(?:\([a-z]\))?)'
    entities['section_numbers'] = re.findall(section_pattern, text)
    
    # Extract dollar amounts
    dollar_pattern = r'\$\s*([\d,]+(?:\.\d+)?)'
    entities['dollar_amounts'] = re.findall(dollar_pattern, text)
    
    # Extract percentages
    percentage_pattern = r'(\d+(?:\.\d+)?)%'
    entities['percentages'] = re.findall(percentage_pattern, text)
    
    # Extract tax years
    tax_year_pattern = r'(?:tax year|year)\s*(\d{4})'
    entities['tax_years'] = re.findall(tax_year_pattern, text, re.IGNORECASE)
    
    return entities


def prepare_document_for_indexing(doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Prepare a document for indexing by chunking and extracting metadata.
    
    Args:
        doc_id: Document identifier
        text: Document text
        metadata: Optional metadata about the document
        
    Returns:
        List of document chunks ready for indexing
    """
    if metadata is None:
        metadata = {}
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Extract entities to enhance metadata
    entities = extract_tax_entities(cleaned_text)
    
    # Merge extracted entities with provided metadata
    enhanced_metadata = metadata.copy()
    enhanced_metadata.update({
        'section_numbers': entities['section_numbers'],
        'dollar_amounts': entities['dollar_amounts'],
        'percentages': entities['percentages'],
        'tax_years': entities['tax_years']
    })
    
    # Chunk the document
    chunks = chunk_document(cleaned_text)
    
    # Prepare document chunks for indexing
    indexable_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}-chunk-{i}"
        
        # Create a copy of the metadata for each chunk
        chunk_metadata = enhanced_metadata.copy()
        chunk_metadata.update({
            'chunk_id': i,
            'total_chunks': len(chunks),
            'is_first_chunk': i == 0,
            'is_last_chunk': i == len(chunks) - 1
        })
        
        indexable_chunks.append({
            'id': chunk_id,
            'content': chunk,
            'metadata': chunk_metadata
        })
    
    return indexable_chunks


def preprocess_irs_publication(text: str) -> str:
    """
    Specialized preprocessing for IRS publications.
    
    Args:
        text: Raw text of an IRS publication
        
    Returns:
        Preprocessed text optimized for RAG
    """
    # Replace common IRS abbreviations
    replacements = {
        "IRC": "Internal Revenue Code",
        "IRS": "Internal Revenue Service",
        "Rev. Proc.": "Revenue Procedure",
        "Rev. Rul.": "Revenue Ruling",
        "Sec.": "Section",
        "§": "Section"
    }
    
    # Apply replacements
    for abbr, full in replacements.items():
        text = re.sub(rf'\b{re.escape(abbr)}\b', full, text)
    
    # Remove line numbers often found in IRS publications
    text = re.sub(r'^\s*\d+\s+', '', text, flags=re.MULTILINE)
    
    # Remove page numbers
    text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
    
    # Clean up the text
    return clean_text(text)


# Example usage
if __name__ == "__main__":
    sample_text = """
    Section 179 allows taxpayers to deduct the cost of certain property as an expense when the 
    property is placed in service. For tax years beginning in 2023, the maximum section 179 
    expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of 
    section 179 property placed in service during the tax year exceeds $2,890,000.
    
    IRC §168(k) provides for 100% additional first-year depreciation deduction for qualified 
    property acquired and placed in service after September 27, 2017, and before January 1, 2023.
    This is often referred to as "bonus depreciation" and applies to both new and used property.
    
    The tax rate for corporations was reduced from 35% to 21% starting in tax year 2018.
    """
    
    # Extract entities
    entities = extract_tax_entities(sample_text)
    print("Extracted entities:", entities)
    
    # Chunk the document
    chunks = chunk_document(sample_text, max_chunk_size=500)
    print(f"\nDocument was split into {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    
    # Prepare for indexing
    indexable_docs = prepare_document_for_indexing("sample-doc", sample_text, {"source": "IRS Publication"})
    print(f"\nCreated {len(indexable_docs)} indexable document chunks")
    print(f"First chunk metadata: {indexable_docs[0]['metadata']}")
