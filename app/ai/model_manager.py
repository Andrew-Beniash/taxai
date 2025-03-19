"""
AI Model Manager for Tax Law Application

This module handles loading and caching the AI model (Mistral-7B)
and provides function for processing tax law queries.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from app.config import MODEL_PATH
from rag.rag_system import TaxLawRAG
from core_ai_engine.prompt_engineering import create_tax_query_prompt, format_ai_response_with_citations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables to store model and tokenizer
_model = None
_tokenizer = None
_rag_system = None

def get_model():
    """
    Loads and returns the model, with caching to avoid reloading.
    """
    global _model
    if _model is None:
        logger.info(f"Loading model: {MODEL_PATH}")
        try:
            # For GPU
            if torch.cuda.is_available():
                logger.info("Using GPU for model inference")
                device = torch.device("cuda")
                _model = AutoModelForCausalLM.from_pretrained(
                    MODEL_PATH, 
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                ).to(device)
            else:
                # For CPU (with quantization to reduce memory usage)
                logger.info("Using CPU for model inference (with quantization)")
                _model = AutoModelForCausalLM.from_pretrained(
                    MODEL_PATH,
                    device_map="auto",
                    load_in_8bit=True  # Use quantization to reduce memory needs
                )
                
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise RuntimeError(f"Failed to load AI model: {str(e)}")
    
    return _model

def get_tokenizer():
    """
    Loads and returns the tokenizer, with caching to avoid reloading.
    """
    global _tokenizer
    if _tokenizer is None:
        logger.info(f"Loading tokenizer: {MODEL_PATH}")
        try:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            logger.info("Tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Error loading tokenizer: {str(e)}")
            raise RuntimeError(f"Failed to load tokenizer: {str(e)}")
    
    return _tokenizer

def get_rag_system():
    """
    Initialize and return the RAG system for tax law document retrieval.
    """
    global _rag_system
    if _rag_system is None:
        logger.info("Initializing RAG system")
        try:
            _rag_system = TaxLawRAG()
            logger.info(f"RAG system initialized with {_rag_system.get_document_count()} documents")
        except Exception as e:
            logger.error(f"Error initializing RAG system: {str(e)}")
            raise RuntimeError(f"Failed to initialize RAG system: {str(e)}")
    
    return _rag_system

def generate_ai_response(query: str, max_length: int = 512) -> Dict[str, Any]:
    """
    Generate an AI response to a tax law query using the loaded model and RAG system.
    
    Args:
        query: The tax law query to process
        max_length: Maximum token length for response generation
    
    Returns:
        Dict containing the response, citations, and confidence score
    """
    try:
        # Get model and tokenizer
        model = get_model()
        tokenizer = get_tokenizer()
        rag = get_rag_system()
        
        # Step 1: Retrieve relevant tax law documents
        logger.info(f"Retrieving context for query: {query}")
        context_docs = rag.search(query, n_results=3)
        
        if not context_docs:
            logger.warning(f"No relevant documents found for query: {query}")
            # Fallback to handle the case with no context
            context_docs = [{
                "content": "No specific tax law reference found.",
                "metadata": {"source": "System Note"}
            }]
        
        # Step 2: Create prompt with retrieved context
        logger.info("Creating prompt with context")
        prompt = create_tax_query_prompt(query, context_docs)
        
        # Step 3: Generate response using the model
        logger.info("Generating AI response")
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        
        # Move inputs to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        # Generate output
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_length=max_length,
                temperature=0.3,  # Lower temperature for fact-based responses
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2
            )
        
        # Decode and format the output
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the answer part (after the prompt)
        if "ANSWER:" in prompt and "ANSWER:" in response_text:
            response_text = response_text.split("ANSWER:", 1)[1].strip()
        
        # Step 4: Format response with citations
        formatted_response = format_ai_response_with_citations(response_text, context_docs)
        
        # Step 5: Create response structure with citations in the required format
        citations = []
        for source in formatted_response.get("sources", []):
            source_doc = context_docs[source["id"]-1] if source["id"] <= len(context_docs) else None
            
            if source_doc:
                citations.append({
                    "source": source_doc.get("metadata", {}).get("source", source["citation"]),
                    "url": source_doc.get("metadata", {}).get("url", None),
                    "text": source_doc.get("content", "")[:200] + "..."  # Limit citation text length
                })
        
        # Return the formatted response
        return {
            "response": formatted_response.get("answer", response_text),
            "citations": citations,
            "confidence_score": 0.85  # Default confidence score (could be calculated more dynamically)
        }
    
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        raise RuntimeError(f"Failed to generate AI response: {str(e)}")

def initialize():
    """
    Initialize all AI components to ensure they're ready for API requests.
    This can be called during application startup.
    """
    try:
        # Load model, tokenizer and RAG system
        get_model()
        get_tokenizer()
        get_rag_system()
        return True
    except Exception as e:
        logger.error(f"Error initializing AI components: {str(e)}")
        return False
