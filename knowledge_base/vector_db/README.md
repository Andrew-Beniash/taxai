# Vector Database for Tax Law Documents

This directory contains the ChromaDB vector database files for storing tax law document embeddings.

## Directory Purpose

The vector database stores:
- Document embeddings generated from tax law texts
- Metadata associated with each document (title, source, date, etc.)
- Chunked text for retrieval-augmented generation (RAG)

## How it Works

1. Tax law documents are processed and split into chunks
2. Each chunk is embedded using the `all-MiniLM-L6-v2` model
3. Embeddings and metadata are stored in ChromaDB
4. Documents can be retrieved via semantic search based on query similarity

## Usage

Do not modify the contents of this directory manually. Instead, use the provided API:

```python
from knowledge_base.src.knowledge_base import TaxLawKnowledgeBase

# Initialize the knowledge base
kb = TaxLawKnowledgeBase(base_directory="path/to/knowledge_base")

# Add documents
kb.add_document(file_path="document.txt", custom_metadata={...})

# Search for documents
results = kb.search("What are business meal deductions?")
```

## Setup

To initialize the vector database, run the setup script:

```bash
python knowledge_base/setup_vector_db.py
```

To populate with sample tax law documents:

```bash
python knowledge_base/populate_knowledge_base.py
```
