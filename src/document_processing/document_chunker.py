"""
Document Chunker Module

This module is responsible for splitting large tax law documents into smaller,
manageable chunks that are suitable for vector embeddings and retrieval.
"""

import os
import re
import logging
import json
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Iterator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaxDocumentChunker:
    """
    Splits large tax law documents into smaller chunks.
    
    This class handles the chunking of tax law documents into smaller,
    semantically coherent pieces suitable for vector embeddings.
    """
    
    def __init__(
        self, 
        input_dir: str = None, 
        output_dir: str = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the TaxDocumentChunker.
        
        Args:
            input_dir: Directory containing processed tax documents.
                       Defaults to '/data/processed' in the project directory.
            output_dir: Directory where chunked documents will be saved.
                        If None, defaults to the same as input_dir.
            chunk_size: Maximum number of characters in each chunk.
            chunk_overlap: Number of characters of overlap between chunks.
        """
        # Get the project root directory
        project_root = Path(os.path.abspath(__file__)).parent.parent.parent
        
        if input_dir is None:
            input_dir = os.path.join(project_root, 'data', 'processed')
        
        if output_dir is None:
            output_dir = input_dir
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Chunk size: {self.chunk_size}, Chunk overlap: {self.chunk_overlap}")
    
    def chunk_all_documents(self) -> Dict[str, List[Dict]]:
        """
        Chunk all processed documents in the input directory.
        
        Returns:
            Dictionary mapping document names to their chunks
        """
        result = {}
        
        for file_path in glob.glob(os.path.join(self.input_dir, "*_processed.txt")):
            try:
                doc_name = os.path.basename(file_path)
                chunks = self.chunk_document(file_path)
                
                if chunks:
                    result[doc_name] = chunks
                    
                    # Also save chunks to JSON file
                    output_file = os.path.join(
                        self.output_dir, 
                        f"{os.path.splitext(doc_name)[0]}_chunks.json"
                    )
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(chunks, f, indent=2)
                    
                    logger.info(f"Saved {len(chunks)} chunks for {doc_name} to {os.path.basename(output_file)}")
            
            except Exception as e:
                logger.error(f"Error chunking {file_path}: {str(e)}")
        
        return result
    
    def chunk_document(self, file_path: str) -> List[Dict]:
        """
        Chunk a single document.
        
        Args:
            file_path: Path to the document to chunk
            
        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            doc_name = os.path.basename(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Get document metadata from the filename
            metadata = self._extract_metadata_from_filename(doc_name)
            
            # Determine the chunking strategy based on document type
            if "section" in doc_name.lower() or "code" in doc_name.lower():
                # For tax code sections, try to chunk by sections
                chunks = self._chunk_by_section(text, metadata)
            else:
                # For other documents, use overlapping chunks
                chunks = self._chunk_by_size(text, metadata)
            
            return chunks
        
        except Exception as e:
            logger.error(f"Error chunking document {file_path}: {str(e)}")
            return []
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict:
        """
        Extract metadata from the filename.
        
        Args:
            filename: Name of the document file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "source": filename,
            "document_type": "tax_document"
        }
        
        # Extract document type from filename
        lower_filename = filename.lower()
        if "section" in lower_filename or "irc" in lower_filename:
            metadata["document_type"] = "tax_code_section"
            
            # Try to extract section number
            section_match = re.search(r'section_(\d+)', lower_filename)
            if section_match:
                metadata["section_number"] = section_match.group(1)
        
        elif "publication" in lower_filename or "pub" in lower_filename:
            metadata["document_type"] = "irs_publication"
            
            # Try to extract publication number
            pub_match = re.search(r'publication_(\d+)', lower_filename)
            if pub_match:
                metadata["publication_number"] = pub_match.group(1)
        
        elif "ruling" in lower_filename:
            metadata["document_type"] = "revenue_ruling"
        
        return metadata
    
    def _chunk_by_section(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Chunk text by logical sections (e.g., for tax code).
        
        Args:
            text: Document text to chunk
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        
        # Split text by section headers
        # This regex looks for patterns like "Section 179(d)(1)" or "## Section 61"
        sections = re.split(r'(?:\n|^)(?:#{1,6}\s*)?(?:Section\s+\d+[a-zA-Z]*(?:\(\w+\))*)', text)
        headers = re.findall(r'(?:\n|^)((?:#{1,6}\s*)?(?:Section\s+\d+[a-zA-Z]*(?:\(\w+\))*))(?=\n|$)', text)
        
        # If we couldn't find sections, fall back to chunking by size
        if len(sections) <= 1:
            return self._chunk_by_size(text, metadata)
        
        # First item will be empty or introduction
        if sections[0].strip():
            # There's an introduction before the first section
            intro_chunk = {
                "text": sections[0].strip(),
                "metadata": {**metadata, "section": "introduction"}
            }
            chunks.append(intro_chunk)
        
        # Process each section
        for i, (section_text, header) in enumerate(zip(sections[1:], headers)):
            # Check if this section is too long and needs to be further chunked
            if len(section_text) > self.chunk_size * 1.5:
                # If too long, chunk by size with this section's header
                section_metadata = {
                    **metadata,
                    "section": header.strip(),
                    "section_index": i
                }
                subsection_chunks = self._chunk_by_size(section_text, section_metadata)
                chunks.extend(subsection_chunks)
            else:
                # Otherwise, keep the section as a single chunk
                chunk = {
                    "text": section_text.strip(),
                    "metadata": {
                        **metadata,
                        "section": header.strip(),
                        "section_index": i
                    }
                }
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_size(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Chunk text by size with overlapping chunks.
        
        Args:
            text: Document text to chunk
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        
        # Find good chunk boundaries (end of sentences or paragraphs)
        chunk_starts = list(self._get_chunk_boundaries(text, self.chunk_size, self.chunk_overlap))
        
        # Create chunks
        for i, start_idx in enumerate(chunk_starts):
            # Calculate end index for this chunk
            end_idx = start_idx + self.chunk_size
            
            # If this is the last chunk, set end_idx to the end of the text
            if i == len(chunk_starts) - 1:
                end_idx = len(text)
            
            # Extract the chunk text
            chunk_text = text[start_idx:end_idx].strip()
            
            # Skip empty chunks
            if not chunk_text:
                continue
            
            # Create chunk with metadata
            chunk = {
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "start_char": start_idx,
                    "end_char": end_idx
                }
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def _get_chunk_boundaries(self, text: str, chunk_size: int, overlap: int) -> Iterator[int]:
        """
        Find optimal chunk boundaries (preferably at end of sentences or paragraphs).
        
        Args:
            text: Document text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks
            
        Yields:
            Starting indices for each chunk
        """
        # First chunk starts at the beginning
        yield 0
        
        # Determine start indices for remaining chunks
        text_len = len(text)
        position = chunk_size
        
        while position < text_len:
            # Adjust position by moving back to find a good boundary
            end_boundary = min(position, text_len)
            
            # Try to find paragraph break
            paragraph_break = text.rfind('\n\n', position - chunk_size, end_boundary)
            if paragraph_break != -1 and (end_boundary - paragraph_break) < chunk_size // 2:
                position = paragraph_break + 2  # +2 to include the newline
                yield position - overlap
                position += chunk_size - overlap
                continue
            
            # Try to find end of sentence
            sentence_break = -1
            for pattern in ['. ', '? ', '! ', '.\n', '?\n', '!\n']:
                sentence_break = max(sentence_break, text.rfind(pattern, position - chunk_size, end_boundary))
            
            if sentence_break != -1 and (end_boundary - sentence_break) < chunk_size // 2:
                position = sentence_break + 2  # +2 to include the period and space
                yield position - overlap
                position += chunk_size - overlap
                continue
            
            # If no good boundary is found, just cut at chunk_size
            yield position - overlap
            position += chunk_size - overlap


# Example usage
if __name__ == "__main__":
    chunker = TaxDocumentChunker()
    chunk_results = chunker.chunk_all_documents()
    
    total_chunks = sum(len(chunks) for chunks in chunk_results.values())
    print(f"Created {total_chunks} chunks from {len(chunk_results)} documents")
    
    for doc_name, chunks in chunk_results.items():
        print(f"  - {doc_name}: {len(chunks)} chunks")
