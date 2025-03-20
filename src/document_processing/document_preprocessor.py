"""
Document Preprocessor Module

This module handles cleaning and preprocessing of tax law documents to convert
them into a standardized text format suitable for AI processing.
"""

import os
import re
import logging
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
import fitz  # PyMuPDF for PDF processing
import docx  # python-docx for DOCX processing
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaxDocumentPreprocessor:
    """
    Preprocesses tax law documents to prepare them for AI processing.
    
    This class handles the cleaning, format standardization, and 
    noise removal from tax documents.
    """
    
    def __init__(self, input_dir: str = None, output_dir: str = None):
        """
        Initialize the TaxDocumentPreprocessor.
        
        Args:
            input_dir: Directory containing raw tax documents.
                       Defaults to '/data/raw' in the project directory.
            output_dir: Directory where processed documents will be saved.
                        Defaults to '/data/processed' in the project directory.
        """
        # Get the project root directory
        project_root = Path(os.path.abspath(__file__)).parent.parent.parent
        
        if input_dir is None:
            input_dir = os.path.join(project_root, 'data', 'raw')
        
        if output_dir is None:
            output_dir = os.path.join(project_root, 'data', 'processed')
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def process_all_documents(self) -> List[str]:
        """
        Process all documents in the input directory.
        
        Returns:
            List of paths to processed documents
        """
        processed_files = []
        
        # Process different file types
        for ext in ["*.txt", "*.pdf", "*.docx", "*.html"]:
            file_pattern = os.path.join(self.input_dir, ext)
            for file_path in glob.glob(file_pattern):
                try:
                    processed_path = self.process_document(file_path)
                    if processed_path:
                        processed_files.append(processed_path)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
        
        return processed_files
    
    def process_document(self, file_path: str) -> Optional[str]:
        """
        Process a single document.
        
        Args:
            file_path: Path to the document to process
            
        Returns:
            Path to the processed document or None if processing failed
        """
        file_name = os.path.basename(file_path)
        output_file = os.path.join(self.output_dir, f"{os.path.splitext(file_name)[0]}_processed.txt")
        
        try:
            # Extract text based on file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self._extract_text_from_docx(file_path)
            elif file_ext == '.html':
                text = self._extract_text_from_html(file_path)
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            else:
                logger.warning(f"Unsupported file type: {file_ext} for file {file_path}")
                return None
            
            # Clean and standardize the text
            clean_text = self._clean_text(text)
            
            # Save the processed document
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            
            logger.info(f"Successfully processed: {file_name} -> {os.path.basename(output_file)}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
                text += "\n\n"  # Add separation between pages
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_text_from_docx(self, docx_path: str) -> str:
        """
        Extract text from a DOCX file.
        
        Args:
            docx_path: Path to the DOCX file
            
        Returns:
            Extracted text
        """
        try:
            doc = docx.Document(docx_path)
            full_text = []
            
            for para in doc.paragraphs:
                full_text.append(para.text)
            
            return '\n'.join(full_text)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {docx_path}: {str(e)}")
            raise
    
    def _extract_text_from_html(self, html_path: str) -> str:
        """
        Extract text from an HTML file.
        
        Args:
            html_path: Path to the HTML file
            
        Returns:
            Extracted text
        """
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML {html_path}: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and standardize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers (common in PDFs)
        text = re.sub(r'\n\s*\d+\s*\n', '\n\n', text)
        
        # Remove headers and footers (simplified approach)
        # This is a simple heuristic and may need to be adjusted for specific documents
        lines = text.split('\n')
        cleaned_lines = []
        for i, line in enumerate(lines):
            # Skip headers (typically in first 3 lines of each page)
            if i % 25 < 2 and len(line.strip()) < 60 and line.strip().isupper():
                continue
            # Skip footers (typically in last 3 lines of each page)
            if i % 25 > 22 and len(line.strip()) < 60:
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Remove common PDF artifacts
        text = re.sub(r'Form\s+\d+', '', text)
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text)
        
        return text.strip()


# Example usage
if __name__ == "__main__":
    preprocessor = TaxDocumentPreprocessor()
    processed_files = preprocessor.process_all_documents()
    
    print(f"Processed {len(processed_files)} documents:")
    for doc in processed_files:
        print(f"  - {os.path.basename(doc)}")
