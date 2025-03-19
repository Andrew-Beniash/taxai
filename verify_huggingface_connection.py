#!/usr/bin/env python3
"""
This script verifies the connection to Hugging Face API and tests sending a sample query.
"""

import os
import requests
import json
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get Hugging Face configuration
api_key = os.getenv("HUGGINGFACE_API_KEY", "")
use_mistral = os.getenv("USE_MISTRAL", "true").lower() == "true"
model_name = "mistralai/Mistral-7B-Instruct-v0.2" if use_mistral else "meta-llama/Llama-3.1-8B-Instruct"

# Check if API key is available
if not api_key:
    print("Error: Hugging Face API key not found. Please check your .env file.")
    print("Make sure HUGGINGFACE_API_KEY is set.")
    sys.exit(1)

print(f"Testing connection to Hugging Face API for model: {model_name}")

# Test query
test_query = "What are the main deductions available for small businesses under Section 179?"

# Prepare headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Prepare payload
payload = {
    "inputs": test_query,
    "parameters": {
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "return_full_text": True
    }
}

try:
    # Make API request
    print("Sending test query to Hugging Face API...")
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model_name}",
        headers=headers,
        json=payload
    )
    
    # Check response
    if response.status_code == 200:
        print("✅ Successfully received response from Hugging Face API")
        
        # Parse the response
        response_body = response.json()
        
        print("\nResponse overview:")
        print(f"HTTP Status: {response.status_code}")
        
        # Print the first part of the response to verify it's working
        if isinstance(response_body, list) and len(response_body) > 0:
            generated_text = response_body[0].get('generated_text', '')
            print("\nGenerated text preview (first 200 chars):")
            print(generated_text[:200] + "..." if len(generated_text) > 200 else generated_text)
        elif isinstance(response_body, dict):
            generated_text = response_body.get('generated_text', '')
            print("\nGenerated text preview (first 200 chars):")
            print(generated_text[:200] + "..." if len(generated_text) > 200 else generated_text)
        else:
            print(f"\nUnexpected response format: {response_body}")
        
        print("\n✅ Hugging Face API connection verification completed successfully")
    else:
        print(f"\n❌ Error from Hugging Face API: Status {response.status_code}")
        print(f"Response: {response.text}")
        print("\nPossible issues:")
        if response.status_code == 401:
            print("- Invalid API key. Check your HUGGINGFACE_API_KEY in the .env file.")
        elif response.status_code == 403:
            print("- You don't have permission to use this model. You may need to request access or subscribe.")
        elif response.status_code == 404:
            print("- Model not found. Check the model name.")
        else:
            print("- Check your API key and model name.")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Error connecting to Hugging Face API: {str(e)}")
    print("\nPlease check your internet connection and API key.")
    sys.exit(1)
