#!/usr/bin/env python3
"""
This script verifies the connection to AWS SageMaker endpoint and tests sending a sample query.
"""

import os
import json
import boto3
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get AWS configuration
aws_region = os.getenv("AWS_REGION", "us-east-1")
sagemaker_endpoint_name = os.getenv("SAGEMAKER_ENDPOINT_NAME", "tax-ai-llm-endpoint")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Check if AWS credentials are available
if not aws_access_key_id or not aws_secret_access_key:
    print("Error: AWS credentials not found. Please check your .env file.")
    print("Make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set.")
    sys.exit(1)

print(f"Testing connection to AWS SageMaker endpoint: {sagemaker_endpoint_name} in region {aws_region}")

# Test query
test_query = "What are the main deductions available for small businesses under Section 179?"

try:
    # Create SageMaker runtime client
    runtime_client = boto3.client(
        'sagemaker-runtime',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    print("✅ Successfully created SageMaker runtime client")
    
    # Create a sample payload for testing
    payload = {
        "inputs": test_query,
        "parameters": {
            "max_new_tokens": 100,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": True
        }
    }
    
    # Convert the payload to JSON
    payload_bytes = json.dumps(payload).encode('utf-8')
    
    print("Sending test query to SageMaker endpoint...")
    
    # Invoke the SageMaker endpoint
    response = runtime_client.invoke_endpoint(
        EndpointName=sagemaker_endpoint_name,
        ContentType='application/json',
        Body=payload_bytes
    )
    
    # Parse the response
    response_body = json.loads(response['Body'].read().decode('utf-8'))
    
    print("✅ Successfully received response from SageMaker endpoint")
    print("\nResponse overview:")
    print(f"HTTP Status: {response['ResponseMetadata']['HTTPStatusCode']}")
    print(f"Content Type: {response['ContentType']}")
    
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
    
    print("\n✅ SageMaker connection verification completed successfully")
    
except Exception as e:
    print(f"\n❌ Error connecting to SageMaker endpoint: {str(e)}")
    print("\nPlease check your AWS credentials, region, and endpoint name.")
    print("Make sure the SageMaker endpoint exists and is running.")
    sys.exit(1)
