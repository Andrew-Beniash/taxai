"""
AI Package for Tax Law Application

This package contains the AI model management and integration components.
"""

from app.ai.model_manager import (
    get_model,
    get_tokenizer,
    get_rag_system,
    generate_ai_response,
    initialize
)

__all__ = [
    'get_model',
    'get_tokenizer',
    'get_rag_system',
    'generate_ai_response',
    'initialize'
]
