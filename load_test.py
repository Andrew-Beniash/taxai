"""
Load testing script for the AI-powered tax law API.
Tests system performance and stability under concurrent load.

Usage:
    python load_test.py --url http://localhost:8000 --users 10 --spawn-rate 2 --time 60

Requirements:
    pip install locust
"""

import time
import json
import random
from locust import HttpUser, task, between
from typing import List, Dict


# Sample tax queries that will be used for load testing
SAMPLE_QUERIES = [
    "What are the tax deductions for a small business?",
    "How are capital gains taxed in 2024?",
    "Can I deduct home office expenses?",
    "What are the tax implications of selling a rental property?",
    "How do I calculate depreciation for business equipment?",
    "What is the standard deduction for 2024?",
    "How are dividends taxed?",
    "What is the mileage rate for business travel?",
    "Can I deduct expenses for a business trip?",
    "How do I report freelance income on my taxes?",
    "What are the tax benefits of retirement accounts?",
    "How is cryptocurrency taxed?",
    "What is the tax treatment for a sole proprietorship?",
    "How do I calculate estimated tax payments?",
    "What records should I keep for tax purposes?",
]

# Sample context data to include with queries
SAMPLE_CONTEXTS = [
    ["Small business with 5 employees", "Annual revenue of $500,000", "Office equipment purchase of $10,000"],
    ["Purchased stock for $5,000", "Sold for $8,000", "Held for 2 years"],
    ["I work from home 3 days per week", "My home office is 200 sq ft", "Total home is 2,000 sq ft"],
    None,  # Sometimes send no context
]


class TaxAIUser(HttpUser):
    """Simulated user for load testing the Tax AI API."""
    
    # Wait between 3-7 seconds between tasks (simulates reading time)
    wait_time = between(3, 7)
    
    def on_start(self):
        """Initialize the user session."""
        # Check if the API is healthy before starting tests
        response = self.client.get("/health")
        if response.status_code != 200 or response.json().get("status") != "healthy":
            print("API is not healthy, aborting test")
            self.environment.runner.quit()
    
    @task(10)  # Higher weight for the main query task
    def query_tax_law(self):
        """Send a tax law query to the API."""
        # Select a random query from our samples
        query = random.choice(SAMPLE_QUERIES)
        
        # Sometimes include context
        context = random.choice(SAMPLE_CONTEXTS) if random.random() > 0.5 else None
        
        # Prepare the payload
        payload = {
            "query": query
        }
        if context:
            payload["context"] = context
        
        # Send the request and measure response time
        start_time = time.time()
        with self.client.post(
            "/api/v1/query",
            json=payload,
            catch_response=True,
            name="Tax Query"
        ) as response:
            duration = time.time() - start_time
            
            # Validate response
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "response" in data and "citations" in data:
                        # Log successful response time
                        response.success()
                        if duration > 5.0:  # Highlight slow responses
                            print(f"Warning: Slow response ({duration:.2f}s) for query: {query[:30]}...")
                    else:
                        response.failure(f"Invalid response format: {data}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 429:
                # Rate limiting is expected under heavy load
                response.success()
                print("Rate limited - this is normal under heavy load")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(1)  # Lower weight for health check
    def check_health(self):
        """Check the API health endpoint."""
        with self.client.get("/health", name="Health Check", catch_response=True) as response:
            if response.status_code != 200 or response.json().get("status") != "healthy":
                response.failure("API is not healthy")
            else:
                response.success()


# This allows running the script with locust
# e.g., locust -f load_test.py --host http://localhost:8000
if __name__ == "__main__":
    # When run directly, print instructions
    print("To run the load test, use locust:")
    print("locust -f load_test.py --host http://localhost:8000")
    print("Then open http://localhost:8089 in your browser")
