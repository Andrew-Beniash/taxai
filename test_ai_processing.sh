#!/bin/bash

# Test AI Processing Integration Script
echo "Testing AI Processing Integration"
echo "================================="

# First load sample data into the RAG system
echo "Loading sample data into RAG system..."
python -m rag.sample_data_loader

# Then run the test script
echo "Running AI integration test..."
python test_ai_integration.py

echo "Test completed."
