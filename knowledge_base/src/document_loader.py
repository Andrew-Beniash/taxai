"""
Module for loading tax law documents from various formats.
This module provides functionality to load and preprocess tax law documents.
"""
import os
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import date
import json
import io
import PyPDF2
from pathlib import Path

from .schema import TaxLawMetadata


logger = logging.getLogger(__name__)


class DocumentLoader:
    """Loads and preprocesses tax law documents from various sources."""
    
    def __init__(self, documents_directory: str):
        """
        Initialize the document loader.
        
        Args:
            documents_directory: Directory containing the tax law documents
        """
        self.documents_directory = documents_directory
    
    def load_document(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Load a document from a file and extract its content and metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple of (document_text, metadata_dict)
        """
        file_path = os.path.join(self.documents_directory, file_path) if not os.path.isabs(file_path) else file_path
        
        # Extract document extension to determine the proper loader
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Load document based on file type
        if ext == '.pdf':
            return self._load_pdf(file_path)
        elif ext == '.txt':
            return self._load_text(file_path)
        elif ext == '.json':
            return self._load_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _load_pdf(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Load a PDF document and extract its text and metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (document_text, metadata_dict)
        """
        logger.info(f"Loading PDF document: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text() + "\n\n"
                
                # Extract basic metadata
                info = pdf_reader.metadata
                
                # Create metadata
                metadata = {
                    "title": info.title if info.title else Path(file_path).stem,
                    "source": "PDF Document",
                    "document_id": os.path.basename(file_path),
                    "publication_date": None,  # PDF metadata date format is inconsistent
                    "document_type": "PDF",
                    "file_path": file_path
                }
                
                return text, metadata
                
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise
    
    def _load_text(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Load a text document and extract its content and metadata.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Tuple of (document_text, metadata_dict)
        """
        logger.info(f"Loading text document: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Extract filename without extension as title
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]
            
            # Look for metadata in the first few lines (common in IRS documents)
            lines = text.split('\n')
            pub_date = None
            
            # Try to find a date in the first 10 lines
            for line in lines[:10]:
                date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', line)
                if date_match:
                    try:
                        month, day, year = map(int, date_match.groups())
                        if year < 100:  # 2-digit year
                            year += 2000 if year < 50 else 1900
                        pub_date = date(year, month, day).isoformat()
                        break
                    except ValueError:
                        continue
            
            # Create metadata
            metadata = {
                "title": title,
                "source": "Text Document",
                "document_id": filename,
                "publication_date": pub_date,
                "document_type": "Text",
                "file_path": file_path
            }
            
            return text, metadata
            
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise
    
    def _load_json(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Load a JSON document that contains both text and metadata.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Tuple of (document_text, metadata_dict)
        """
        logger.info(f"Loading JSON document: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Extract text and metadata from JSON
            text = data.get("text", "")
            metadata = data.get("metadata", {})
            
            # Ensure required metadata fields exist
            if "title" not in metadata:
                metadata["title"] = os.path.splitext(os.path.basename(file_path))[0]
            if "document_id" not in metadata:
                metadata["document_id"] = os.path.basename(file_path)
            if "source" not in metadata:
                metadata["source"] = "JSON Document"
            
            return text, metadata
            
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            raise
    
    def create_metadata(self, metadata_dict: Dict[str, Any]) -> TaxLawMetadata:
        """
        Create a TaxLawMetadata object from a dictionary.
        
        Args:
            metadata_dict: Dictionary containing metadata
            
        Returns:
            TaxLawMetadata object
        """
        # Convert publication_date string to date object if present
        if metadata_dict.get("publication_date") and isinstance(metadata_dict["publication_date"], str):
            try:
                metadata_dict["publication_date"] = date.fromisoformat(metadata_dict["publication_date"])
            except ValueError:
                # If date parsing fails, set to None
                metadata_dict["publication_date"] = None
        
        return TaxLawMetadata(**metadata_dict)
