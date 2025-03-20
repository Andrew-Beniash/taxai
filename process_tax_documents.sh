#!/bin/bash

# This script runs the tax law document processing pipeline
# It collects, preprocesses, and chunks tax documents for the AI-powered tax law system

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install required packages if needed
echo "Installing document processing requirements..."
pip install -r src/document_processing/requirements.txt

# Default settings
USE_SAMPLE_DATA=false
MANUAL_DIR=""
RAW_DIR="data/raw"
PROCESSED_DIR="data/processed"
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --sample)
            USE_SAMPLE_DATA=true
            shift
            ;;
        --manual-dir)
            MANUAL_DIR="$2"
            shift
            shift
            ;;
        --raw-dir)
            RAW_DIR="$2"
            shift
            shift
            ;;
        --processed-dir)
            PROCESSED_DIR="$2"
            shift
            shift
            ;;
        --chunk-size)
            CHUNK_SIZE="$2"
            shift
            shift
            ;;
        --chunk-overlap)
            CHUNK_OVERLAP="$2"
            shift
            shift
            ;;
        *)
            # Unknown option
            echo "Unknown option: $1"
            shift
            ;;
    esac
done

# Prepare command
CMD="python -m src.document_processing.main"
CMD+=" --raw-dir $RAW_DIR"
CMD+=" --processed-dir $PROCESSED_DIR"
CMD+=" --chunk-size $CHUNK_SIZE"
CMD+=" --chunk-overlap $CHUNK_OVERLAP"

if [ "$USE_SAMPLE_DATA" = true ]; then
    CMD+=" --use-sample-data"
fi

if [ ! -z "$MANUAL_DIR" ]; then
    CMD+=" --manual-dir \"$MANUAL_DIR\""
fi

# Run the document processing pipeline
echo "Running document processing pipeline with command:"
echo "$CMD"
eval "$CMD"

echo "Document processing completed!"
echo "Raw documents stored in: $RAW_DIR"
echo "Processed documents stored in: $PROCESSED_DIR"

# Deactivate virtual environment if activated
if [ -d "venv" ]; then
    deactivate
fi
