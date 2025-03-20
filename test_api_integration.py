"""
Comprehensive API integration tests for the AI-powered tax law system.
Run this script to verify all API endpoints work as expected.
"""

import requests
import json
import time
import argparse
from typing import Dict, Any


class APITester:
    """Tests the AI-powered tax law API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_all_tests(self):
        """Run all API tests and report results."""
        print(f"\n🧪 Testing Tax AI API at {self.base_url}")
        
        # Run each test
        self.test_health_check()
        self.test_root_endpoint()
        self.test_valid_query()
        self.test_empty_query()
        self.test_context_query()
        
        # Print summary
        print("\n📊 Test Summary:")
        print(f"  Passed: {self.passed_tests}")
        print(f"  Failed: {self.failed_tests}")
        print(f"  Total: {self.passed_tests + self.failed_tests}")
        
        # Check if all tests passed
        return self.failed_tests == 0
    
    def test_health_check(self):
        """Test the health check endpoint."""
        print("\n✅ Testing health check endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200 and response.json().get("status") == "healthy":
                print("  ✓ Health check passed")
                self.passed_tests += 1
            else:
                print(f"  ✗ Health check failed: {response.json()}")
                self.failed_tests += 1
        except Exception as e:
            print(f"  ✗ Health check exception: {str(e)}")
            self.failed_tests += 1
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        print("\n✅ Testing root endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200 and "Tax Law AI API is running" in response.text:
                print("  ✓ Root endpoint passed")
                self.passed_tests += 1
            else:
                print(f"  ✗ Root endpoint failed: {response.text}")
                self.failed_tests += 1
        except Exception as e:
            print(f"  ✗ Root endpoint exception: {str(e)}")
            self.failed_tests += 1
    
    def test_valid_query(self):
        """Test a valid tax query."""
        print("\n✅ Testing valid tax query...")
        payload = {"query": "What are the tax deductions for small businesses?"}
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/query", 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Print response time for performance measurement
            print(f"  Request took {response.elapsed.total_seconds():.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                if (
                    "response" in data and 
                    "citations" in data and 
                    "confidence_score" in data and
                    "processing_time" in data
                ):
                    print("  ✓ Valid query passed")
                    print(f"  Response preview: {data['response'][:100]}...")
                    self.passed_tests += 1
                else:
                    print(f"  ✗ Valid query missing expected fields: {data}")
                    self.failed_tests += 1
            else:
                print(f"  ✗ Valid query failed with status {response.status_code}: {response.text}")
                self.failed_tests += 1
        except Exception as e:
            print(f"  ✗ Valid query exception: {str(e)}")
            self.failed_tests += 1
    
    def test_empty_query(self):
        """Test an empty query (should be rejected)."""
        print("\n✅ Testing empty query validation...")
        payload = {"query": ""}
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/query", 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print("  ✓ Empty query correctly rejected")
                self.passed_tests += 1
            else:
                print(f"  ✗ Empty query test failed with status {response.status_code}: {response.text}")
                self.failed_tests += 1
        except Exception as e:
            print(f"  ✗ Empty query exception: {str(e)}")
            self.failed_tests += 1
    
    def test_context_query(self):
        """Test a query with context provided."""
        print("\n✅ Testing query with context...")
        payload = {
            "query": "What tax benefits apply to this expense?",
            "context": [
                "Office equipment purchase of $5,000 for a small business",
                "Made on December 15, 2024",
                "Used exclusively for business purposes"
            ]
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/query", 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and len(data["response"]) > 0:
                    print("  ✓ Context query passed")
                    print(f"  Response preview: {data['response'][:100]}...")
                    self.passed_tests += 1
                else:
                    print(f"  ✗ Context query returned empty response: {data}")
                    self.failed_tests += 1
            else:
                print(f"  ✗ Context query failed with status {response.status_code}: {response.text}")
                self.failed_tests += 1
        except Exception as e:
            print(f"  ✗ Context query exception: {str(e)}")
            self.failed_tests += 1


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Tax AI API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL")
    args = parser.parse_args()
    
    # Run tests
    tester = APITester(args.url)
    success = tester.run_all_tests()
    
    # Exit with success code if all tests passed
    exit(0 if success else 1)
