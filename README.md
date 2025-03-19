# Tax Law AI API

This project provides an AI-powered API for processing tax law queries and generating accurate responses with citations.

## Setup Instructions

### 1. Prerequisites

- Python 3.10+ installed
- pip package manager

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example .env file and modify as needed:

```bash
# The default settings should work for most development environments
# Modify if you need to change ports or host settings
```

### 5. Run the API Server

```bash
python run.py
```

The API server will be available at http://localhost:8000

## API Documentation

After starting the server, you can access the auto-generated API documentation:

- OpenAPI documentation: http://localhost:8000/docs
- ReDoc interface: http://localhost:8000/redoc

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - API health check
- `POST /api/query` - Process a tax law query

## Development

- The project uses FastAPI for API development
- Follows a modular structure for better maintenance
- Current implementation uses mock data (will be replaced with AI models)

## Next Steps

- Integrate Mistral-7B model for generating responses
- Implement vector search for tax law documents
- Add document processing capabilities
