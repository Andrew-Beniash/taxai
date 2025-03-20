# Tax Law Document Processing Module

This module handles the collection, preprocessing, and chunking of tax law documents for the AI-powered tax law system. It prepares data for vector storage and retrieval in the knowledge base.

## Components

1. **Document Collector** - Collects tax law documents from various sources:
   - IRS publications
   - Internal Revenue Code sections
   - Legal rulings and tax guides
   - Sample tax documents for development

2. **Document Preprocessor** - Cleans and standardizes documents:
   - Extracts text from different file formats (PDF, DOCX, HTML, TXT)
   - Removes unnecessary formatting, headers, and footers
   - Standardizes content for improved AI processing

3. **Document Chunker** - Splits documents into smaller chunks:
   - Creates semantically coherent chunks of appropriate size
   - Preserves context with overlapping text
   - Maintains metadata for accurate retrieval and citation

## Usage

### Running the Complete Pipeline

The easiest way to run the complete document processing pipeline is to use the provided script:

```bash
./process_tax_documents.sh
```

### Options

The script accepts several options:

- `--sample`: Use sample tax law documents for development
- `--manual-dir [PATH]`: Process documents from a custom directory
- `--raw-dir [PATH]`: Specify directory for raw documents
- `--processed-dir [PATH]`: Specify directory for processed documents
- `--chunk-size [SIZE]`: Set maximum size for document chunks
- `--chunk-overlap [SIZE]`: Set overlap size between chunks

Example:

```bash
./process_tax_documents.sh --sample --chunk-size 800 --chunk-overlap 150
```

### Using Individual Components

You can also use the individual components in your code:

```python
from src.document_processing.document_collector import TaxDocumentCollector
from src.document_processing.document_preprocessor import TaxDocumentPreprocessor
from src.document_processing.document_chunker import TaxDocumentChunker

# Collect documents
collector = TaxDocumentCollector()
documents = collector.collect_sample_tax_laws()

# Preprocess documents
preprocessor = TaxDocumentPreprocessor()
processed_docs = preprocessor.process_all_documents()

# Chunk documents
chunker = TaxDocumentChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_all_documents()
```

## Requirements

The document processing module requires the following dependencies:

- Python 3.10+
- requests
- beautifulsoup4
- PyMuPDF
- python-docx
- tqdm

Install them using:

```bash
pip install -r src/document_processing/requirements.txt
```

## Directory Structure

- `/data/raw`: Raw tax law documents
- `/data/processed`: Preprocessed and chunked documents
- `/src/document_processing`: Code for document processing
