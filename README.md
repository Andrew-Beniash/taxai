# AI-Powered Tax Law System

An intelligent system leveraging AI to provide accurate tax law research, document processing, and compliance validation.

## Technology Stack

- **Backend**: FastAPI, Python, LangChain, PostgreSQL
- **AI/ML**: PyTorch, LLMs (Llama 3, Mistral), FAISS, Tesseract OCR
- **Data Storage**: PostgreSQL, ChromaDB/FAISS
- **Messaging**: RabbitMQ/Kafka
- **Frontend**: React (Next.js), Tailwind CSS

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the development server: `python src/main.py`

## Project Structure

- `src/`: Source code
  - `api/`: API endpoints and routers
  - `core_ai/`: Core AI engine and tax law processing
  - `agents/`: Specialized AI agents (Research, Document Processing, Verification)
  - `security/`: Authentication and authorization
  - `database/`: Database models and connections
  - `utils/`: Utility functions
- `tests/`: Test cases