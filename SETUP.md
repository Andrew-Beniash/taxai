# TaxAI Setup Guide

This guide provides detailed instructions for setting up the TaxAI development environment.

## Prerequisites

- Python 3.9 or higher
- Git

## Setup Instructions

### 1. Clone the Repository (if applicable)

If you're starting with an existing repository:

```bash
git clone <repository-url>
cd taxai
```

If you're setting up from scratch, continue to step 2.

### 2. Make Setup Scripts Executable

Before using the shell scripts, make them executable:

```bash
chmod +x setup.sh run_dev.sh init_git.sh
```

### 3. Initialize the Development Environment

Run the setup script to create the virtual environment and install dependencies:

```bash
./setup.sh
```

This script will:
- Check your Python version
- Create a virtual environment
- Install all required dependencies
- Create necessary directories
- Generate a default .env file with development settings

### 4. Initialize Git Repository (if starting from scratch)

If you're setting up a new project, initialize the Git repository:

```bash
./init_git.sh
```

This script will:
- Initialize a new Git repository
- Create the initial commit
- Set up the develop branch according to our branching strategy

### 5. Start the Development Server

To start the development server:

```bash
./run_dev.sh
```

The server should now be running at http://localhost:8000

## Running Tests

To run the tests:

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test categories
pytest tests/unit
pytest tests/integration
```

## Project Structure

```
taxai/
├── src/                    # Source code
│   ├── api/                # API endpoints
│   ├── agents/             # Agent implementations
│   ├── core/               # Core application logic
│   ├── db/                 # Database models and connections
│   ├── knowledge/          # Knowledge base management
│   ├── models/             # Data models
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── data/                   # Data storage (created by setup.sh)
│   ├── chroma/             # Vector database storage
│   └── documents/          # Document storage
├── .github/workflows/      # CI/CD configuration
├── venv/                   # Virtual environment (created by setup.sh)
├── .env                    # Environment variables (created by setup.sh)
├── setup.sh                # Environment setup script
├── run_dev.sh              # Development server script
├── init_git.sh             # Git initialization script
├── requirements.txt        # Dependencies
└── README.md               # Project overview
```

## Environment Variables

The main environment variables are stored in the `.env` file:

- `DEBUG`: Enable debug mode (true/false)
- `DATABASE_URI`: Database connection string
- `MODEL_TYPE`: Type of LLM to use (llama3, mistral, etc.)
- `MODEL_PATH`: Path to local LLM model (if applicable)
- `MODEL_API_KEY`: API key for cloud-based LLM (if applicable)
- `VECTOR_DB_TYPE`: Type of vector database (chroma, pinecone, etc.)
- `VECTOR_DB_PERSIST_DIR`: Directory for vector database persistence
- `SECRET_KEY`: Secret key for security operations
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

## Branching Strategy

Please refer to the `BRANCHING_STRATEGY.md` file for details on our Git workflow.
