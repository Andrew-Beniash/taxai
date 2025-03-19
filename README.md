# Tax Law AI - Retrieval-Augmented Generation (RAG) System

This repository contains a Retrieval-Augmented Generation (RAG) system designed for tax law applications. It allows for efficient storage, indexing, and retrieval of tax law documents.

## Project Structure

```
taxai/
├── ai_engine/                # AI model and query processing
├── rag/                      # RAG system
│   ├── __init__.py           # Package initialization
│   ├── rag_system.py         # Main RAG implementation
│   ├── preprocessing.py      # Document preprocessing utilities
│   └── example.py            # Example usage
├── data/
│   └── tax_law_db/           # ChromaDB database storage (created automatically)
└── requirements.txt          # Project dependencies
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Hugging Face API credentials in the `.env` file:

```
# Hugging Face API settings
USE_HUGGINGFACE_API=true
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

4. Verify the Hugging Face API connection:

```bash
# Make the verification script executable first
./make_verify_huggingface_executable.sh

# Run the verification script
./verify_huggingface_connection.py
```

## Hugging Face API Setup

This project uses the Hugging Face Inference API to run LLM models instead of hosting them locally. Here's how to set it up:

1. **Create a Hugging Face Account**:
   - Visit [huggingface.co](https://huggingface.co) and sign up for an account
   - Navigate to your profile settings

2. **Generate an API Key**:
   - Go to "Settings" > "Access Tokens"
   - Create a new token with "read" scope (or higher if you plan to upload models)
   - Copy the API key and add it to your `.env` file

3. **Model Access**:
   - Some models like Mistral-7B-Instruct may require you to accept terms of use
   - Visit the model page (e.g., [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2))
   - Click "Accept terms and access repository" if prompted

4. **Test Your Setup**:
   - Run the verification script to ensure everything is working properly

For more details on using the Hugging Face Inference API, refer to the [official documentation](https://huggingface.co/docs/api-inference/usage).

## Usage

The RAG system consists of three main components:

1. **Document Preprocessing**: Prepare and optimize tax law documents for indexing
2. **Vector Database**: Store document embeddings using ChromaDB
3. **Semantic Search**: Retrieve relevant tax law references based on user queries

### Example Usage

```python
from rag.rag_system import TaxLawRAG
from rag.preprocessing import prepare_document_for_indexing

# Initialize the RAG system
rag = TaxLawRAG(db_path="./data/tax_law_db")

# Prepare and index a document
doc = {
    "id": "irs-section-179",
    "content": "Section 179 allows taxpayers to deduct the cost of certain property...",
    "metadata": {
        "source": "IRS Publication",
        "year": 2023,
        "title": "Section 179 Deduction"
    }
}

# Index the document
rag.index_document(
    doc_id=doc["id"],
    content=doc["content"],
    metadata=doc["metadata"]
)

# Search for relevant documents
query = "What are small business deductions for equipment?"
results = rag.search(query, n_results=3)

# Display results
for result in results:
    print(f"Document: {result['id']}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Metadata: {result['metadata']}")
```

### Running the Example

To run the example script that demonstrates the RAG system:

```bash
python -m rag.example
```

This will:
1. Initialize the ChromaDB database
2. Index sample tax law documents
3. Run sample queries to show how the RAG system works

## Features

- **Cloud-based LLM**: Uses Hugging Face's Inference API for better scalability and ease of use
- **Vector Storage**: Efficiently stores and retrieves document embeddings using ChromaDB
- **Document Chunking**: Splits long documents into manageable chunks with configurable overlap
- **Metadata Extraction**: Automatically extracts tax-specific entities (section numbers, dollar amounts, etc.)
- **Semantic Search**: Finds the most relevant tax law references for user queries
- **Hybrid Search**: Combines keyword and semantic search for improved accuracy

## License

[MIT License](LICENSE)
