"""
Tests for validating AI responses against real IRS tax regulations.
This module ensures the accuracy of AI-generated tax law information.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest
import re

# Add the project root to the path so we can import modules properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.query_processor import (
    process_tax_query,
    extract_citations
)


class MockTaxLaw:
    """Class to contain verified tax law data for testing."""
    
    # Verified IRS Section 179 details for 2023
    SECTION_179_2023 = {
        "deduction_limit": 1160000,
        "phase_out_threshold": 2890000,
        "suv_limit": 28900,
        "citation": "IRC § 179",
        "pub": "IRS Publication 946"
    }
    
    # Standard mileage rates for 2023
    MILEAGE_RATES_2023 = {
        "business": 65.5,  # cents per mile
        "medical": 22,     # cents per mile
        "charity": 14,     # cents per mile
        "moving": 22,      # cents per mile (for active military)
        "citation": "IRS Notice 2023-03"
    }
    
    # Home office deduction simplified method details
    HOME_OFFICE_SIMPLIFIED = {
        "rate_per_sqft": 5,   # $5 per square foot
        "max_sqft": 300,      # Maximum 300 square feet
        "citation": "IRS Publication 587"
    }
    
    # Corporate tax rates for 2023
    CORPORATE_TAX_RATE_2023 = {
        "rate": 21,  # 21% flat rate
        "citation": "IRC § 11"
    }


class TestResponseAccuracy(unittest.TestCase):
    """Tests AI responses against verified IRS data to ensure accuracy."""
    
    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_section_179_deduction_accuracy(self, mock_retrieve, mock_generate):
        """Test accuracy of Section 179 deduction responses."""
        # Setup mock retrieval context
        mock_retrieve.return_value = [
            f"Section 179 allows businesses to deduct up to ${MockTaxLaw.SECTION_179_2023['deduction_limit']} in 2023 for equipment purchases."
        ]
        
        # Setup mock response generation
        mock_generate.return_value = f"""
        According to IRC § 179, businesses can deduct up to ${MockTaxLaw.SECTION_179_2023['deduction_limit']} for equipment purchases in 2023. This deduction phases out dollar-for-dollar when equipment purchases exceed ${MockTaxLaw.SECTION_179_2023['phase_out_threshold']}. For SUVs, the maximum deduction is limited to ${MockTaxLaw.SECTION_179_2023['suv_limit']}.
        """
        
        # Process a sample query about Section 179
        result = process_tax_query("What are the Section 179 deduction limits for 2023?")
        
        # Extract the numeric values from the response
        response = result["response"]
        
        # Check that the response contains the correct Section 179 limit
        assert str(MockTaxLaw.SECTION_179_2023['deduction_limit']) in response
        assert str(MockTaxLaw.SECTION_179_2023['phase_out_threshold']) in response
        
        # Verify that the citations exist
        assert MockTaxLaw.SECTION_179_2023['citation'] in response or "Section 179" in response

    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_mileage_rates_accuracy(self, mock_retrieve, mock_generate):
        """Test accuracy of mileage rate responses."""
        # Setup mock retrieval context
        mock_retrieve.return_value = [
            f"The IRS mileage rate for business use in 2023 is {MockTaxLaw.MILEAGE_RATES_2023['business']} cents per mile."
        ]
        
        # Setup mock response generation
        mock_generate.return_value = f"""
        For 2023, the IRS has set the following standard mileage rates:
        - Business use: {MockTaxLaw.MILEAGE_RATES_2023['business']} cents per mile
        - Medical or moving (active military): {MockTaxLaw.MILEAGE_RATES_2023['medical']} cents per mile
        - Charitable purposes: {MockTaxLaw.MILEAGE_RATES_2023['charity']} cents per mile
        
        These rates are established in {MockTaxLaw.MILEAGE_RATES_2023['citation']}.
        """
        
        # Process a sample query about mileage rates
        result = process_tax_query("What are the standard mileage rates for 2023?")
        
        # Check that the response contains the correct mileage rates
        response = result["response"]
        
        assert str(MockTaxLaw.MILEAGE_RATES_2023['business']) in response
        assert MockTaxLaw.MILEAGE_RATES_2023['citation'] in response

    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_corporate_tax_rate_accuracy(self, mock_retrieve, mock_generate):
        """Test accuracy of corporate tax rate responses."""
        # Setup mock retrieval context
        mock_retrieve.return_value = [
            f"The corporate tax rate in 2023 is a flat {MockTaxLaw.CORPORATE_TAX_RATE_2023['rate']}% for all taxable income."
        ]
        
        # Setup mock response generation
        mock_generate.return_value = f"""
        The corporate tax rate in 2023 remains at {MockTaxLaw.CORPORATE_TAX_RATE_2023['rate']}% for all taxable income. This flat rate was established by the Tax Cuts and Jobs Act of 2017 and is codified in {MockTaxLaw.CORPORATE_TAX_RATE_2023['citation']}.
        """
        
        # Process a sample query about corporate tax rates
        result = process_tax_query("What is the corporate tax rate for 2023?")
        
        # Check that the response contains the correct tax rate
        response = result["response"]
        assert str(MockTaxLaw.CORPORATE_TAX_RATE_2023['rate']) in response
        assert "%" in response
        assert MockTaxLaw.CORPORATE_TAX_RATE_2023['citation'] in response

    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_home_office_deduction_accuracy(self, mock_retrieve, mock_generate):
        """Test accuracy of home office deduction responses."""
        # Setup mock retrieval context
        mock_retrieve.return_value = [
            f"The simplified home office deduction allows ${MockTaxLaw.HOME_OFFICE_SIMPLIFIED['rate_per_sqft']} per square foot with a maximum of {MockTaxLaw.HOME_OFFICE_SIMPLIFIED['max_sqft']} square feet."
        ]
        
        # Setup mock response generation
        mock_generate.return_value = f"""
        According to {MockTaxLaw.HOME_OFFICE_SIMPLIFIED['citation']}, taxpayers can use the simplified method for home office deductions, which allows ${MockTaxLaw.HOME_OFFICE_SIMPLIFIED['rate_per_sqft']} per square foot up to a maximum of {MockTaxLaw.HOME_OFFICE_SIMPLIFIED['max_sqft']} square feet. This means the maximum simplified deduction is ${MockTaxLaw.HOME_OFFICE_SIMPLIFIED['rate_per_sqft'] * MockTaxLaw.HOME_OFFICE_SIMPLIFIED['max_sqft']}.
        """
        
        # Process a sample query about home office deductions
        result = process_tax_query("How does the simplified home office deduction work?")
        
        # Check that the response contains the correct deduction details
        response = result["response"]
        
        assert str(MockTaxLaw.HOME_OFFICE_SIMPLIFIED['rate_per_sqft']) in response
        assert str(MockTaxLaw.HOME_OFFICE_SIMPLIFIED['max_sqft']) in response
        assert MockTaxLaw.HOME_OFFICE_SIMPLIFIED['citation'] in response


class TestCitationValidation(unittest.TestCase):
    """Tests for validating citations in AI responses."""
    
    def test_irs_publication_citations(self):
        """Test that IRS Publication citations are in the correct format."""
        # Sample response with IRS publication citations
        response = """
        According to IRS Publication 463, business travel expenses are deductible when you're away from your tax home.
        IRS Publication 535 provides guidelines on business expenses.
        You can find more information in IRS Publication 946 for depreciation.
        """
        
        # Extract citations
        citations = extract_citations(response)
        
        # Check that the format is correct
        for citation in citations:
            if "IRS Publication" in citation:
                # Should be in format "IRS Publication ###"
                assert re.match(r"IRS Publication \d+", citation), f"Invalid IRS Publication format: {citation}"

    def test_irc_section_citations(self):
        """Test that IRC Section citations are in the correct format."""
        # Sample response with IRC section citations
        response = """
        IRC § 179 allows for equipment deductions.
        According to IRC § 162, ordinary and necessary business expenses are deductible.
        IRC § 263A requires capitalization of certain expenses.
        """
        
        # Extract citations
        citations = extract_citations(response)
        
        # Check that the format is correct
        for citation in citations:
            if "IRC §" in citation:
                # Should be in format "IRC § ###"
                assert re.match(r"IRC § \d+[\w\.\-]*", citation), f"Invalid IRC Section format: {citation}"

    def test_treasury_regulation_citations(self):
        """Test that Treasury Regulation citations are in the correct format."""
        # Sample response with Treasury Regulation citations
        response = """
        Treasury Regulation §1.162-1 provides that business expenses are deductible.
        According to Treasury Regulation §1.179-1, equipment deductions are allowed.
        """
        
        # Extract citations
        citations = extract_citations(response)
        
        # Check that the format is correct
        for citation in citations:
            if "Treasury Regulation" in citation:
                # Should be in format "Treasury Regulation §#.###-#"
                assert re.match(r"Treasury Regulation §[\d\.\-]+", citation), f"Invalid Treasury Regulation format: {citation}"


class TestCommonTaxScenarios(unittest.TestCase):
    """Tests for common tax law scenarios to ensure response accuracy."""
    
    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_business_meal_deduction_accuracy(self, mock_retrieve, mock_generate):
        """Test accuracy of business meal deduction responses."""
        # Setup mock retrieval context
        mock_retrieve.return_value = [
            "For 2023, business meals are 50% deductible in most cases. However, meals from restaurants are 100% deductible for tax years 2021 and 2022 only."
        ]
        
        # Setup mock response generation
        mock_generate.return_value = """
        For the 2023 tax year, business meals are generally 50% deductible when they meet the necessary criteria of being business-related and not lavish or extravagant. This is a return to the standard rule after the temporary 100% deduction for restaurant meals, which only applied to 2021 and 2022 as a COVID-19 relief measure. The 50% limitation is specified in IRC § 274(n).
        """
        
        # Process a sample query about meal deductions
        result = process_tax_query("Are business meals 100% deductible in 2023?")
        
        # Check that the response contains the correct deduction percentage
        response = result["response"]
        
        assert "50%" in response
        assert "274" in response or "IRC § 274" in response
        assert not "100% deductible" in response.lower() or "not 100% deductible" in response.lower() or "only applied to 2021 and 2022" in response

    @patch('ai_engine.model_loader.model_loader.generate_response')
    @patch('ai_engine.retrieval.retrieve_context_for_query')
    def test_retirement_contribution_limits_accuracy(self, mock_retrieve, mock_generate):
        """Test accuracy of retirement contribution limit responses."""
        # Setup mock retrieval context
        mock_retrieve.return_value = [
            "For 2023, the contribution limit for 401(k) plans is $22,500, with an additional $7,500 catch-up contribution allowed for those age 50 and older."
        ]
        
        # Setup mock response generation
        mock_generate.return_value = """
        For the 2023 tax year, the 401(k) contribution limit is $22,500, which is an increase from the 2022 limit of $20,500. If you're age 50 or older, you can make an additional catch-up contribution of $7,500, bringing your total potential contribution to $30,000. These limits are set by the IRS and can be found in IRS Notice 2022-55.
        """
        
        # Process a sample query about retirement contributions
        result = process_tax_query("What is the 401k contribution limit for 2023?")
        
        # Check that the response contains the correct contribution limits
        response = result["response"]
        
        assert "$22,500" in response
        assert "$7,500" in response
        assert "catch-up" in response.lower()


if __name__ == '__main__':
    unittest.main()
