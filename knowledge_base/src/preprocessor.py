"""
Module for preprocessing tax law documents.
This module provides functionality to clean and structure tax law documents.
"""
import re
import logging
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class TaxDocumentPreprocessor:
    """
    Preprocesses tax law documents to improve embedding quality.
    """
    
    def __init__(self):
        """Initialize the preprocessor."""
        pass
    
    def preprocess(self, text: str) -> str:
        """
        Clean and preprocess tax law document text.
        
        Args:
            text: The raw document text
            
        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        text = self.remove_excessive_whitespace(text)
        
        # Fix common OCR errors in tax documents
        text = self.fix_ocr_errors(text)
        
        # Normalize section references
        text = self.normalize_section_references(text)
        
        # Fix paragraph breaks
        text = self.fix_paragraph_breaks(text)
        
        return text
    
    def remove_excessive_whitespace(self, text: str) -> str:
        """
        Remove excessive whitespace from the document.
        
        Args:
            text: Document text
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newlines (to preserve paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove spaces at the beginning of lines
        text = re.sub(r'\n +', '\n', text)
        
        return text.strip()
    
    def fix_ocr_errors(self, text: str) -> str:
        """
        Fix common OCR errors in tax documents.
        
        Args:
            text: Document text
            
        Returns:
            Corrected text
        """
        # Fix common OCR errors in tax documents
        replacements = {
            r'I RS': 'IRS',
            r'Sect\s*[i1]on': 'Section',
            r'[0O]rd[i1]nary': 'Ordinary',
            r'[i1]ncome': 'income',
            r'd[e3]duct[i1]on': 'deduction',
            r'cr[e3]d[i1]t': 'credit',
            r't[a4]x[a4]ble': 'taxable',
            r'r[e3]gul[a4]t[i1][o0]n': 'regulation'
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def normalize_section_references(self, text: str) -> str:
        """
        Normalize section references in tax documents.
        
        Args:
            text: Document text
            
        Returns:
            Text with normalized section references
        """
        # Normalize IRC section references
        # "IRC Sec. 123" or "I.R.C. § 123" -> "IRC Section 123"
        text = re.sub(r'(IRC|I\.R\.C\.)(\s+|\s*§\s*|\s*Sec\.?\s+)(\d+)', r'IRC Section \3', text)
        
        # Normalize Treasury Regulation references
        # "Treas. Reg. 1.123-4" -> "Treasury Regulation 1.123-4"
        text = re.sub(r'Treas\.?\s*Reg\.?\s*(\d+\.\d+\-\d+)', r'Treasury Regulation \1', text)
        
        return text
    
    def fix_paragraph_breaks(self, text: str) -> str:
        """
        Fix paragraph breaks in the document.
        
        Args:
            text: Document text
            
        Returns:
            Text with fixed paragraph breaks
        """
        # Ensure sentences end with a period
        text = re.sub(r'([a-z])\s*\n\s*([A-Z])', r'\1. \2', text)
        
        # Ensure proper spacing after periods
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        
        return text
    
    def extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a tax law document.
        
        Args:
            text: Document text
            
        Returns:
            List of sections with their titles and content
        """
        # Regular expression to match section headers (customize based on your documents)
        section_pattern = re.compile(r'(Section \d+[\.\d]*|§ \d+[\.\d]*)\s+(.*?)\n', re.IGNORECASE)
        
        # Find all sections
        section_matches = list(section_pattern.finditer(text))
        
        sections = []
        
        # Extract section content
        for i, match in enumerate(section_matches):
            section_num = match.group(1)
            section_title = match.group(2).strip()
            start_pos = match.end()
            
            # Determine where this section ends (at the start of the next section or end of text)
            end_pos = section_matches[i+1].start() if i < len(section_matches) - 1 else len(text)
            
            section_content = text[start_pos:end_pos].strip()
            
            sections.append({
                "number": section_num,
                "title": section_title,
                "content": section_content
            })
        
        return sections
