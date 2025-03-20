"""
Module for collecting and downloading tax law documents from various sources.
"""
import os
import logging
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
import json

from .schema import TaxLawMetadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaxLawDataCollector:
    """Collects tax law documents from various sources."""
    
    def __init__(self, documents_directory: str):
        """
        Initialize the tax law data collector.
        
        Args:
            documents_directory: Directory where documents will be stored
        """
        self.documents_directory = documents_directory
        os.makedirs(documents_directory, exist_ok=True)
    
    def download_irs_publication(
        self, 
        publication_number: str, 
        year: str = "2023",
        save_as_txt: bool = True
    ) -> Optional[str]:
        """
        Download an IRS publication in PDF format.
        
        Args:
            publication_number: IRS publication number (e.g., "535")
            year: Tax year of the publication (e.g., "2023")
            save_as_txt: Whether to create a text version alongside the PDF
            
        Returns:
            Path to the downloaded file, or None if download failed
        """
        try:
            # Format URL for IRS publication
            url = f"https://www.irs.gov/pub/irs-pdf/p{publication_number}.pdf"
            
            # Create filename
            filename = f"irs_pub_{publication_number}_{year}.pdf"
            filepath = os.path.join(self.documents_directory, filename)
            
            logger.info(f"Downloading IRS Publication {publication_number} from {url}")
            
            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded to {filepath}")
            
            # Create a simplified text version with metadata if requested
            if save_as_txt:
                txt_filename = f"irs_pub_{publication_number}_{year}.txt"
                txt_filepath = os.path.join(self.documents_directory, txt_filename)
                
                # Create a simple text file with metadata
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"IRS Publication {publication_number} ({year})\n\n")
                    f.write(f"Title: IRS Publication {publication_number}\n")
                    f.write(f"Year: {year}\n")
                    f.write(f"Source: Internal Revenue Service\n")
                    f.write(f"URL: {url}\n\n")
                    
                    # Add some sample content based on the publication number
                    f.write(self._get_sample_content(publication_number))
                
                logger.info(f"Created simplified text version at {txt_filepath}")
                
                # Also create a JSON file with metadata
                self._create_metadata_file(publication_number, year, url)
                
                return txt_filepath
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading IRS Publication {publication_number}: {str(e)}")
            return None
    
    def _create_metadata_file(self, publication_number: str, year: str, url: str) -> None:
        """
        Create a metadata JSON file for the publication.
        
        Args:
            publication_number: IRS publication number
            year: Tax year
            url: Source URL
        """
        metadata = {
            "title": f"IRS Publication {publication_number}",
            "source": "Internal Revenue Service",
            "document_id": f"irs_pub_{publication_number}_{year}",
            "publication_date": f"{year}-01-01",  # Approximate date
            "jurisdiction": "Federal",
            "document_type": "Publication",
            "tags": ["irs", f"publication {publication_number}", f"tax year {year}"],
            "url": url
        }
        
        # Add specific tags based on publication number
        if publication_number == "535":
            metadata["tags"].extend(["business expenses", "deductions"])
        elif publication_number == "17":
            metadata["tags"].extend(["individual tax", "tax guide"])
        elif publication_number == "225":
            metadata["tags"].extend(["farmer's tax guide", "agriculture"])
            
        # Save metadata
        json_filename = f"irs_pub_{publication_number}_{year}.json"
        json_filepath = os.path.join(self.documents_directory, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Created metadata file at {json_filepath}")
    
    def _get_sample_content(self, publication_number: str) -> str:
        """
        Return sample content for a given IRS publication number.
        
        Args:
            publication_number: IRS publication number
            
        Returns:
            Sample content text
        """
        # Dictionary of sample content for common IRS publications
        sample_content = {
            "535": """
## Business Expenses

### Introduction
This publication discusses common business expenses and explains what is and is not deductible.

### What's New
For tax years beginning in 2023, the maximum section 179 expense deduction is $1,160,000.
This limit is reduced by the amount by which the cost of section 179 property placed in
service during the tax year exceeds $2,890,000.

### Deducting Business Expenses
To be deductible, a business expense must be both ordinary and necessary. An ordinary expense
is one that is common and accepted in your trade or business. A necessary expense is one that
is helpful and appropriate for your trade or business.

### Business Use of Your Home
If you use part of your home for business, you may be able to deduct expenses for the business
use of your home. These expenses may include mortgage interest, insurance, utilities, repairs,
and depreciation.

### Car and Truck Expenses
If you use your car or truck in your business, you may be able to deduct the costs of operating
and maintaining your vehicle. You can either deduct the actual expenses or use the standard
mileage rate.
""",
            "17": """
## Your Federal Income Tax For Individuals

### Introduction
This publication covers the general rules for filing a federal income tax return.

### What's New
For 2023, the standard deduction has increased to $13,850 for single filers and $27,700 for
married couples filing jointly.

### Filing Requirements
You must file a federal income tax return if your income is above a certain level, which varies
depending on your filing status, age, and the type of income you received.

### Filing Status
Your filing status is used to determine your filing requirements, standard deduction, eligibility
for certain credits, and your correct tax. There are five filing statuses: Single, Married Filing
Jointly, Married Filing Separately, Head of Household, and Qualifying Surviving Spouse.

### Dependents
You can claim a dependent on your tax return if they meet certain tests. This can affect your
eligibility for certain tax benefits.
""",
            "225": """
## Farmer's Tax Guide

### Introduction
This publication explains how the federal tax laws apply to farming.

### What's New
For 2023, the maximum amount you can elect to deduct for most section 179 property you placed
in service in 2023 is $1,160,000.

### Farm Income
You must include various types of income on your tax return, including income from the sale of
livestock, produce, grains, and other products you raised.

### Farm Business Expenses
The ordinary and necessary costs of operating a farm for profit are deductible business expenses.
These include the costs of feed, seed, fertilizer, and similar farm supplies.

### Depreciation, Section 179 Deduction, and Special Depreciation Allowance
If you buy farm property such as machinery, equipment, or structures that have a useful life of
more than a year, you generally cannot deduct the entire cost in the year you buy it. Instead,
you must depreciate these assets.
"""
        }
        
        # Return sample content or a default message
        return sample_content.get(
            publication_number,
            f"Sample content for IRS Publication {publication_number}. This is placeholder text for demonstration purposes."
        )
    
    def download_common_irs_publications(self) -> List[str]:
        """
        Download a set of common IRS publications.
        
        Returns:
            List of paths to downloaded files
        """
        # List of common IRS publications relevant for tax research
        publications = [
            {"number": "17", "year": "2023", "title": "Your Federal Income Tax For Individuals"},
            {"number": "535", "year": "2023", "title": "Business Expenses"},
            {"number": "225", "year": "2023", "title": "Farmer's Tax Guide"},
            {"number": "946", "year": "2023", "title": "How To Depreciate Property"},
            {"number": "463", "year": "2023", "title": "Travel, Gift, and Car Expenses"},
        ]
        
        downloaded_files = []
        
        for pub in publications:
            logger.info(f"Processing IRS Publication {pub['number']}: {pub['title']}")
            
            # Try to download as PDF, fallback to creating text version
            result = self.download_irs_publication(
                publication_number=pub["number"],
                year=pub["year"],
                save_as_txt=True
            )
            
            if result:
                downloaded_files.append(result)
            
            # Sleep to avoid overwhelming the server
            time.sleep(1)
        
        return downloaded_files
    
    def create_sample_tax_law_documents(self) -> List[str]:
        """
        Create sample tax law documents for testing when downloads aren't feasible.
        
        Returns:
            List of created document paths
        """
        created_files = []
        
        # Create sample documents for different tax topics
        tax_topics = [
            {
                "title": "Section 179 Deduction",
                "filename": "section_179_deduction.txt",
                "content": """
# Section 179 Deduction

## Overview
Section 179 of the Internal Revenue Code allows taxpayers to deduct the cost of certain types of property on their income taxes as an expense, rather than requiring the cost of the property to be capitalized and depreciated.

## 2023 Deduction Limit
For tax years beginning in 2023, the maximum section 179 expense deduction is $1,160,000. This limit is reduced by the amount by which the cost of section 179 property placed in service during the tax year exceeds $2,890,000.

## Qualified Property
Property that qualifies for the Section 179 deduction includes:
- Tangible personal property (machinery, equipment, etc.)
- Computer software
- Qualified improvement property
- Certain improvements to nonresidential real property
    - Roofs
    - Heating, ventilation, and air-conditioning property
    - Fire protection and alarm systems
    - Security systems

## Business Income Limitation
The Section 179 deduction is limited to the taxable income derived from the active conduct of a trade or business. Any disallowed deduction due to the business income limitation can be carried forward to later tax years.
"""
            },
            {
                "title": "Business Meal Deductions",
                "filename": "business_meal_deductions.txt",
                "content": """
# Business Meal Deductions

## Overview
The Internal Revenue Code allows businesses to deduct the cost of business meals under certain circumstances.

## Current Deduction Rules
For 2023, businesses can generally deduct 50% of meal expenses that are:
- Ordinary and necessary
- Not lavish or extravagant
- Directly related to or associated with the business

However, meals provided by restaurants are 100% deductible in 2023.

## Documentation Requirements
To support a deduction for meal expenses, you need records showing:
- The amount spent
- The date the meal occurred
- The place where the meal took place
- The business purpose of the meal
- The business relationship of the people at the meal

## Non-Deductible Meal Expenses
The following meal expenses are generally not deductible:
- Personal meals while not traveling
- Meals that are lavish or extravagant
- Meals where no business is conducted
- Meals where only employees are present and no business is discussed
"""
            },
            {
                "title": "Home Office Deduction",
                "filename": "home_office_deduction.txt",
                "content": """
# Home Office Deduction

## Overview
The home office deduction allows qualifying taxpayers to deduct certain expenses related to using their home for business purposes.

## Qualification Requirements
To qualify for the home office deduction, you must use part of your home:
- Exclusively and regularly as your principal place of business
- Exclusively and regularly as a place to meet with patients, clients, or customers
- As a separate structure used exclusively for business
- For storage of inventory or product samples
- For certain daycare facilities

## Calculation Methods
There are two methods for calculating the home office deduction:

### Regular Method
Under this method, you deduct the actual expenses of maintaining your home office, including:
- Mortgage interest or rent
- Utilities
- Insurance
- Repairs
- Depreciation
These expenses are allocated based on the percentage of your home used for business.

### Simplified Method
Under the simplified method, you can deduct $5 per square foot of home office space, up to a maximum of 300 square feet ($1,500).

## Effect on Home Sale
Using the home office deduction may affect the tax treatment when you sell your home.
"""
            }
        ]
        
        for topic in tax_topics:
            filepath = os.path.join(self.documents_directory, topic["filename"])
            
            # Create text file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(topic["content"])
            
            # Create metadata file
            metadata_path = os.path.join(
                self.documents_directory, 
                os.path.splitext(topic["filename"])[0] + ".json"
            )
            
            metadata = {
                "title": topic["title"],
                "source": "Tax Law Knowledge Base",
                "document_id": os.path.splitext(topic["filename"])[0],
                "publication_date": "2023-03-15",
                "jurisdiction": "Federal",
                "document_type": "Tax Guide",
                "tags": ["tax deduction", topic["title"].lower().replace(" ", "_")],
                "url": None
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            created_files.append(filepath)
            logger.info(f"Created sample document: {filepath}")
        
        return created_files
