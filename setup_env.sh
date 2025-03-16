#!/bin/bash

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install essential libraries for AI/ML and API development
pip install --upgrade pip
pip install fastapi uvicorn torch transformers langchain langchain-community langchain-experimental faiss-cpu chromadb python-multipart pydantic pytest sentence-transformers

# Create a requirements.txt file with installed packages
pip freeze > requirements.txt

# Print confirmation message
echo "Python virtual environment has been set up successfully!"
echo "To activate the environment in the future, run: source venv/bin/activate"
