"""
Tax Law Document Processing Pipeline

This script runs the complete document processing pipeline:
1. Collecting tax law documents
2. Preprocessing and cleaning the documents
3. Chunking the documents for vector storage

This can be run as a standalone script or imported and used in other modules.
"""

import os
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional

from document_collector import TaxDocumentCollector
from document_preprocessor import TaxDocumentPreprocessor
from document_chunker import TaxDocumentChunker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaxDocumentPipeline:
    """
    Orchestrates the complete tax document processing pipeline.
    """
    
    def __init__(
        self,
        raw_dir: str = None,
        processed_dir: str = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the document processing pipeline.
        
        Args:
            raw_dir: Directory for storing raw documents.
                     If None, defaults to '/data/raw' in the project directory.
            processed_dir: Directory for storing processed documents.
                          If None, defaults to '/data/processed' in the project directory.
            chunk_size: Maximum size of document chunks.
            chunk_overlap: Overlap between document chunks.
        """
        # Get the project root directory
        project_root = Path(os.path.abspath(__file__)).parent.parent.parent
        
        if raw_dir is None:
            raw_dir = os.path.join(project_root, 'data', 'raw')
        
        if processed_dir is None:
            processed_dir = os.path.join(project_root, 'data', 'processed')
        
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize pipeline components
        self.collector = TaxDocumentCollector(output_dir=raw_dir)
        self.preprocessor = TaxDocumentPreprocessor(input_dir=raw_dir, output_dir=processed_dir)
        self.chunker = TaxDocumentChunker(
            input_dir=processed_dir,
            output_dir=processed_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Ensure directories exist
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
        
        logger.info(f"Pipeline initialized with:")
        logger.info(f"  Raw directory: {raw_dir}")
        logger.info(f"  Processed directory: {processed_dir}")
        logger.info(f"  Chunk size: {chunk_size}")
        logger.info(f"  Chunk overlap: {chunk_overlap}")
    
    def run_pipeline(self, use_sample_data: bool = False, manual_dir: str = None) -> Dict[str, List[Dict]]:
        """
        Run the complete document processing pipeline.
        
        Args:
            use_sample_data: If True, generate sample tax law documents for development.
            manual_dir: If provided, also collect documents from this directory.
            
        Returns:
            Dictionary mapping document names to their chunks
        """
        logger.info("Starting tax document processing pipeline")
        
        # Step 1: Collect documents
        collected_docs = []
        
        if use_sample_data:
            logger.info("Generating sample tax law documents")
            collected_docs.extend(self.collector.collect_sample_tax_laws())
        
        if manual_dir:
            logger.info(f"Collecting documents from manual directory: {manual_dir}")
            collected_docs.extend(self.collector.collect_from_manual_directory(manual_dir))
        
        # Also collect some common IRS publications
        if not collected_docs:
            logger.info("Collecting IRS publications")
            collected_docs.extend(self.collector.collect_irs_publications())
            collected_docs.extend(self.collector.collect_tax_code_sections())
        
        logger.info(f"Collected {len(collected_docs)} documents")
        
        # Step 2: Preprocess documents
        logger.info("Preprocessing documents")
        processed_docs = self.preprocessor.process_all_documents()
        logger.info(f"Preprocessed {len(processed_docs)} documents")
        
        # Step 3: Chunk documents
        logger.info("Chunking documents")
        chunk_results = self.chunker.chunk_all_documents()
        
        total_chunks = sum(len(chunks) for chunks in chunk_results.values())
        logger.info(f"Created {total_chunks} chunks from {len(chunk_results)} documents")
        
        return chunk_results


def main():
    """Main function to run the document processing pipeline."""
    parser = argparse.ArgumentParser(description="Process tax law documents.")
    parser.add_argument("--raw-dir", type=str, help="Directory for raw documents")
    parser.add_argument("--processed-dir", type=str, help="Directory for processed documents")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Size of document chunks")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Overlap between chunks")
    parser.add_argument("--manual-dir", type=str, help="Directory with manually collected documents")
    parser.add_argument("--use-sample-data", action="store_true", help="Generate sample tax law documents")
    
    args = parser.parse_args()
    
    # Initialize and run the pipeline
    pipeline = TaxDocumentPipeline(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    pipeline.run_pipeline(
        use_sample_data=args.use_sample_data,
        manual_dir=args.manual_dir
    )


if __name__ == "__main__":
    main()
