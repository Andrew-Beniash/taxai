#!/bin/bash

# TaxAI Development Environment Setup Script

# Exit on error
set -e

# Function to display status messages
print_status() {
    echo -e "\n\033[1;34m$1\033[0m"
}

# Function to display success messages
print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

# Function to display error messages
print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

# Check if Python 3.10+ is installed
print_status "Checking Python version..."
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 9 ]); then
    print_error "Python 3.9 or higher is required. Found Python $python_version"
    exit 1
fi

print_success "Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip
print_success "Pip upgraded"

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed"

# Create necessary directories if they don't exist
print_status "Creating necessary directories..."
mkdir -p data/chroma
mkdir -p data/documents
mkdir -p logs
print_success "Directories created"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file with development settings..."
    cat > .env << EOF
# TaxAI Environment Configuration

# Debug Mode
DEBUG=true

# Database Configuration
DATABASE_URI=sqlite:///./taxai.db

# AI Model Configuration
MODEL_TYPE=llama3
# MODEL_PATH=/path/to/your/model  # Uncomment and set path to local model file
# MODEL_API_KEY=your_api_key      # Uncomment and set API key if using cloud model

# Vector Database Configuration
VECTOR_DB_TYPE=chroma
VECTOR_DB_PERSIST_DIR=./data/chroma

# Security Configuration
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    print_success ".env file created with development settings"
else
    print_status ".env file already exists"
fi

print_success "Setup complete! Your development environment is ready."
print_status "To activate the virtual environment in the future, run:"
echo "source venv/bin/activate"
print_status "To start the development server, run:"
echo "cd src && python main.py"
