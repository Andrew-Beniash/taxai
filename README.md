# AI-Powered Tax Law System

This project implements a tax law query processing system using AI (Large Language Models) to provide accurate responses to tax-related questions.

## Features

- AI-powered tax law query processing
- API endpoints for integrating with frontend applications
- Model optimization with quantization to improve performance
- Docker support for containerized deployment

## Project Structure

```
taxai/
├── ai_engine/                # AI model and query processing
│   ├── __init__.py           
│   ├── model_loader.py       # Handles loading and optimizing LLM
│   └── query_processor.py    # Processes tax law queries
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── Dockerfile                # Docker configuration
├── test_query.py             # Test script for API
└── README.md                 # Project documentation
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- [Hugging Face account](https://huggingface.co/) with access to Llama 3 or Mistral models
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository
```
git clone <repository-url>
cd taxai
```

2. Create a virtual environment and activate it
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Configure your environment variables in `.env` file
```
# Choose model (USE_MISTRAL=true for Mistral, false for Llama 3)
USE_MISTRAL=false
```

5. Authenticate with Hugging Face
```
huggingface-cli login
```

### Running the API

1. Start the FastAPI server:
```
uvicorn main:app --reload
```

2. Access the API at http://localhost:8000
   - API documentation: http://localhost:8000/docs

### Testing

Run a test query:
```
python test_query.py --query "What are the tax deductions for small businesses?"
```

### Docker Deployment

1. Build the Docker image:
```
docker build -t taxai .
```

2. Run the container:
```
docker run -p 8000:8000 taxai
```

## Model Selection

This system supports two LLM options:

1. **Llama 3.1 (8B) Instruct**: Better reasoning capabilities, more accurate for complex tax scenarios (requires Meta approval for access)
2. **Mistral (7B) Instruct**: Faster response times, suitable for simpler queries and is openly accessible

By default, the system is configured to use Mistral since it doesn't require special access permissions. To switch between models, update the `USE_MISTRAL` variable in your `.env` file.

### Note on Model Access

The Llama 3.1 model requires special access from Meta. You'll need to request access at [Meta's Llama website](https://llama.meta.com/) before you can use it. Until then, the system will default to using Mistral's open-access model.

## Future Improvements

- [ ] Implement Retrieval-Augmented Generation (RAG) for better factual accuracy
- [ ] Add document upload and processing capabilities
- [ ] Develop an agent orchestration system
- [ ] Enhance compliance validation for tax laws
