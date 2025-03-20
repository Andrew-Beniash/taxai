# Tax Law Knowledge Base

This module provides a vector database for storing and retrieving tax law documents using ChromaDB, a lightweight vector database optimized for efficient similarity search.

## Features

- Store tax law documents with rich metadata (title, source, publication date, etc.)
- Convert documents into vector embeddings for semantic search
- Search for tax law references based on natural language queries
- Process various document formats (PDF, text, JSON)
- Chunking strategy for handling large documents
- Preprocessing of tax law documents to improve embedding quality

## Directory Structure

```
knowledge_base/
├── vector_db/          # ChromaDB persistent storage
├── documents/          # Raw tax law documents
├── src/                # Source code
│   ├── __init__.py
│   ├── vector_store.py # ChromaDB configuration and operations
│   ├── embedding.py    # Document embedding generation
│   ├── schema.py       # Metadata schema definition
│   ├── document_loader.py # Document loading utilities
│   ├── preprocessor.py # Text preprocessing
│   └── knowledge_base.py # Main interface
├── example.py          # Example usage
├── setup_vector_db.py  # Script to set up the vector database
├── populate_knowledge_base.py # Script to populate with sample documents
├── SCHEMA.md           # Documentation of the document schema
└── requirements.txt    # Dependencies
```

## Requirements

- Python 3.10+
- ChromaDB
- sentence-transformers
- PyPDF2 (for PDF processing)
- pydantic

## Getting Started

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up the vector database:

```bash
python setup_vector_db.py
```

3. Populate the knowledge base with sample documents:

```bash
python populate_knowledge_base.py
```

4. Run the example script to see how the knowledge base works:

```bash
python example.py
```

## Usage

```python
from knowledge_base.src.knowledge_base import TaxLawKnowledgeBase

# Initialize the knowledge base
kb = TaxLawKnowledgeBase(base_directory="/path/to/knowledge_base")

# Add a document to the knowledge base
chunk_ids = kb.add_document(
    file_path="path/to/document.pdf",
    custom_metadata={
        "title": "IRS Publication 535",
        "source": "IRS",
        "document_type": "Publication"
    }
)

# Search for relevant tax law references
results = kb.search(
    query="What is the maximum section 179 deduction?",
    n_results=5
)

# Display search results
for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    print(f"Result {i+1}:")
    print(f"Document: {metadata.get('title')}")
    print(f"Content: {doc}")
```

## Metadata Schema

The knowledge base stores the following metadata for each document:

- `title`: Title of the tax law document
- `source`: Source of the document (e.g., IRS, Tax Court)
- `document_id`: Unique identifier for the document
- `publication_date`: Publication date of the document
- `jurisdiction`: Jurisdiction (e.g., Federal, State)
- `document_type`: Type of document (e.g., Regulation, Ruling, Publication)
- `sections`: Relevant sections or chapters
- `tags`: Tags for categorization
- `url`: URL to the original document

See `SCHEMA.md` for detailed documentation of the metadata schema.

## Adding Custom Documents

You can add your own tax law documents to the knowledge base by:

1. Placing them in the `documents/` directory
2. Using the `add_document()` method to process them
3. Optionally providing custom metadata

Supported document formats:
- PDF files
- Text files
- JSON files (with text and metadata fields)

## Vector Database Management

The vector database is implemented using ChromaDB and provides:

- Efficient semantic search using document embeddings
- Rich metadata filtering capabilities
- Chunking and processing for large documents
- Persistent storage of embeddings and metadata

To manage the vector database:

- `setup_vector_db.py`: Initialize the vector store
- `vector_store.py`: Contains the low-level ChromaDB operations
- `knowledge_base.py`: Provides a high-level interface for database operations
