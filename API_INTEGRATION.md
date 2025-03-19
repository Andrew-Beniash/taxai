# AI Query Processing API Integration

This document explains how to use the API for tax law query processing with RAG (Retrieval Augmented Generation) integration.

## Overview

The system provides an API endpoint for processing tax-related queries using AI models augmented with retrieved tax law documents. The API returns structured responses with citations and confidence scores.

## API Endpoint

### Query Processing Endpoint

**URL**: `/api/v1/query`  
**Method**: `POST`  
**Content-Type**: `application/json`

#### Request Body

```json
{
  "query": "What are the rules for business travel deductions?",
  "context": ["Optional list of tax law references to include"]
}
```

- `query` (required): The tax-related question or query
- `context` (optional): List of tax law references to include in the AI prompt

#### Response Body

```json
{
  "response": "Business travel expenses are the ordinary and necessary expenses of traveling away from home for your business, profession, or job. These expenses are generally deductible if they are (1) ordinary and necessary and (2) you are traveling away from your tax home...",
  "citations": ["IRS Publication 463", "Treasury Regulation § 1.162-2"],
  "confidence_score": 0.85,
  "processing_time": 1.25
}
```

- `response`: The AI-generated answer to the tax query
- `citations`: List of tax law references cited in the response
- `confidence_score`: Model confidence in the response (0-1)
- `processing_time`: Time taken to process the query (in seconds)

## RAG Integration

The API automatically performs the following steps:

1. Preprocesses the query to identify tax-specific terminology
2. Retrieves relevant tax law documents from the vector database using semantic search
3. Formats the AI prompt with the query and retrieved context
4. Generates a response using the language model
5. Returns the structured response with extracted citations

## Running the API

Start the FastAPI server by running:

```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the API server
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Testing the API

You can test the API integration with:

```bash
# Test RAG integration with sample data
python test_rag_integration.py

# Run Streamlit UI for interactive testing
streamlit run streamlit_app.py
```

## API Client Example

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/query"

# Request headers
headers = {
    "Content-Type": "application/json"
}

# Request data
data = {
    "query": "What are the deductions for small businesses?"
}

# Send the request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Check if the request was successful
if response.status_code == 200:
    result = response.json()
    print(f"Response: {result['response']}")
    print(f"Citations: {result['citations']}")
    print(f"Confidence Score: {result['confidence_score']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Frontend Integration

To integrate with a frontend application, use standard HTTP requests to the API endpoint. For example, with React:

```javascript
async function queryTaxLaw(query) {
  const response = await fetch('http://localhost:8000/api/v1/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  
  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }
  
  return await response.json();
}
```

## Additional Notes

- The API is secured with CORS to allow requests only from specific origins
- The RAG system uses ChromaDB for vector storage and retrieval
- The AI model is either Mistral-7B-Instruct or Llama-3.1-8B-Instruct based on configuration
