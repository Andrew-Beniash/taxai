#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Install LangChain packages
echo "Installing LangChain packages..."
pip install langchain-community langchain-experimental

# Run verification
echo "Verifying installation..."
python verify_ai_setup.py

echo "Installation complete!"
