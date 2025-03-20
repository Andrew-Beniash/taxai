"""
Document Collector Module

This module is responsible for collecting tax law documents from various sources
like IRS regulations, tax code sections, and legal rulings.
"""

import os
import requests
import logging
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# IRS document sources URLs (examples)
IRS_SOURCES = {
    "regulations": "https://www.irs.gov/tax-professionals/tax-code-regulations-and-official-guidance",
    "publications": "https://www.irs.gov/forms-instructions",
    "revenue_rulings": "https://www.irs.gov/individuals/tax-trails-main-menu"
}

class TaxDocumentCollector:
    """
    Collects tax law documents from official sources.
    
    This class provides methods to download tax documents from various sources
    and save them to a local directory.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the TaxDocumentCollector.
        
        Args:
            output_dir: Directory where documents will be saved.
                        Defaults to '/data/raw' in the project directory.
        """
        if output_dir is None:
            # Get the project root directory
            project_root = Path(os.path.abspath(__file__)).parent.parent.parent
            output_dir = os.path.join(project_root, 'data', 'raw')
        
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Documents will be saved to: {self.output_dir}")
    
    def download_document(self, url: str, filename: str) -> Optional[str]:
        """
        Download a document from a URL and save it.
        
        Args:
            url: URL to download the document from
            filename: Name to save the document as
            
        Returns:
            Path to the saved file or None if download failed
        """
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                file_path = os.path.join(self.output_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Successfully downloaded: {filename}")
                return file_path
            else:
                logger.error(f"Failed to download {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            return None
    
    def collect_irs_publications(self, pub_numbers: List[int] = None) -> List[str]:
        """
        Collect specific IRS publications by their publication numbers.
        
        Args:
            pub_numbers: List of publication numbers to collect.
                         If None, it will collect some common tax publications.
                         
        Returns:
            List of paths to downloaded publications
        """
        # Default to common tax publications if none specified
        if pub_numbers is None:
            pub_numbers = [17, 334, 535, 542, 225, 463, 501, 503, 526, 936]
        
        downloaded_files = []
        
        for pub_num in pub_numbers:
            # IRS publications are usually available as PDFs
            url = f"https://www.irs.gov/pub/irs-pdf/p{pub_num}.pdf"
            filename = f"publication_{pub_num}.pdf"
            result = self.download_document(url, filename)
            if result:
                downloaded_files.append(result)
        
        return downloaded_files
    
    def collect_tax_code_sections(self, sections: List[str] = None) -> List[str]:
        """
        Collect specific Internal Revenue Code sections.
        
        Args:
            sections: List of IRC section identifiers to collect.
                     If None, it will collect some commonly referenced sections.
                     
        Returns:
            List of paths to downloaded sections
        """
        # Default to common IRC sections if none specified
        if sections is None:
            sections = ["1", "11", "21", "61", "162", "179", "401", "408", "501", "1031"]
        
        # Note: This is a placeholder. In a real implementation, 
        # you would need to find the actual source URLs for IRC sections
        
        downloaded_files = []
        
        # Mock implementation - in production, you would crawl official sources
        for section in sections:
            # For demonstration, we're creating placeholder files
            file_path = os.path.join(self.output_dir, f"irc_section_{section}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Internal Revenue Code Section {section}\n\n")
                f.write(f"This is a placeholder for IRC Section {section} content.\n")
                f.write("In a production system, this would contain the actual tax code text.\n")
            
            downloaded_files.append(file_path)
            logger.info(f"Created placeholder for IRC Section {section}")
        
        return downloaded_files
    
    def collect_from_manual_directory(self, directory: str) -> List[str]:
        """
        Collect documents from a manually downloaded directory.
        
        This is useful when documents have been manually downloaded or can't be
        automatically scraped from websites.
        
        Args:
            directory: Path to the directory containing tax documents
            
        Returns:
            List of paths to collected documents
        """
        collected_files = []
        
        if not os.path.exists(directory):
            logger.error(f"Directory does not exist: {directory}")
            return collected_files
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                # Copy the file to our raw data directory
                dest_path = os.path.join(self.output_dir, filename)
                with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                collected_files.append(dest_path)
                logger.info(f"Collected: {filename}")
        
        return collected_files

    def collect_sample_tax_laws(self) -> List[str]:
        """
        Create sample tax law documents for development and testing.
        
        This is useful for development when you don't have real documents yet.
        
        Returns:
            List of paths to created sample documents
        """
        sample_documents = []
        
        # Sample IRC Section 179 - Property that qualifies for section 179
        file_path = os.path.join(self.output_dir, "sample_section_179.txt")
        with open(file_path, 'w') as f:
            f.write("# Internal Revenue Code Section 179 - Property that qualifies for section 179\n\n")
            f.write("## Section 179(d)(1)\n\n")
            f.write("For purposes of this section, the term "section 179 property" means property—\n")
            f.write("(A) which is—\n")
            f.write("  (i) tangible property (to which section 168 applies), or\n")
            f.write("  (ii) computer software (as defined in section 197(e)(3)(B)) which is described in section 197(e)(3)(A)(i) and which is acquired by purchase for use in the active conduct of a trade or business,\n")
            f.write("(B) to which section 168 would apply without regard to this section, and\n")
            f.write("(C) which is not described in section 50(b).\n")
            f.write("Such term shall not include any property described in section 50(b) and shall not include air conditioning or heating units.")
        
        sample_documents.append(file_path)
        logger.info(f"Created sample document: {file_path}")
        
        # Sample - Business Expense Deductions
        file_path = os.path.join(self.output_dir, "sample_business_expenses.txt")
        with open(file_path, 'w') as f:
            f.write("# Business Expense Deductions - Section 162\n\n")
            f.write("## Section 162(a)\n\n")
            f.write("There shall be allowed as a deduction all the ordinary and necessary expenses paid or incurred during the taxable year in carrying on any trade or business, including—\n")
            f.write("(1) a reasonable allowance for salaries or other compensation for personal services actually rendered;\n")
            f.write("(2) traveling expenses (including amounts expended for meals and lodging other than amounts which are lavish or extravagant under the circumstances) while away from home in the pursuit of a trade or business; and\n")
            f.write("(3) rentals or other payments required to be made as a condition to the continued use or possession, for purposes of the trade or business, of property to which the taxpayer has not taken or is not taking title or in which he has no equity.")
        
        sample_documents.append(file_path)
        logger.info(f"Created sample document: {file_path}")
        
        # Sample - Home Office Deduction
        file_path = os.path.join(self.output_dir, "sample_home_office.txt")
        with open(file_path, 'w') as f:
            f.write("# Home Office Deduction - Publication 587\n\n")
            f.write("## Requirements for Qualifying to Deduct Expenses for Business Use of Your Home\n\n")
            f.write("You can deduct certain expenses for business use of your home if you use part of your home regularly and exclusively:\n")
            f.write("- As your principal place of business for any trade or business;\n")
            f.write("- As a place to meet with patients, clients, or customers in the normal course of your trade or business; or\n")
            f.write("- In the case of a separate structure not attached to your home, in connection with your trade or business.\n\n")
            f.write("The regular and exclusive business use must be for your trade or business. If you are an employee, the business use of your home must be for the convenience of your employer.\n\n")
            f.write("## Deductible Expenses\n\n")
            f.write("Expenses that you can deduct for business use of your home include:\n")
            f.write("- Real estate taxes\n")
            f.write("- Deductible mortgage interest\n")
            f.write("- Casualty losses\n")
            f.write("- Utilities\n")
            f.write("- Insurance\n")
            f.write("- Depreciation\n")
        
        sample_documents.append(file_path)
        logger.info(f"Created sample document: {file_path}")
        
        return sample_documents


# Example usage
if __name__ == "__main__":
    collector = TaxDocumentCollector()
    
    # Create sample documents for development
    sample_docs = collector.collect_sample_tax_laws()
    
    print(f"Created {len(sample_docs)} sample documents:")
    for doc in sample_docs:
        print(f"  - {os.path.basename(doc)}")
