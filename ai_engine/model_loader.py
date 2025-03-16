"""
Model loader for the AI-powered tax law system.
This module handles loading, optimization, and inference with the LLM (Llama 3 or Mistral).
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, List, Union, Optional

# Import centralized configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USE_MISTRAL, CURRENT_MODEL

# Model configuration
MODEL_NAME = CURRENT_MODEL

# Define device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BITS = 4 if DEVICE == "cuda" else 16  # Use 4-bit quantization on GPU, 16-bit on CPU


class ModelLoader:
    """Handles loading and optimization of LLM for tax law processing."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load and optimize the language model."""
        print(f"Loading {MODEL_NAME} on {DEVICE} with {BITS}-bit quantization...")
        
        try:
            # Load tokenizer
            print(f"Loading model: {MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            
            # Configure quantization for model loading
            quantization_config = None
            if BITS == 4:
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load model with quantization if on GPU
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                quantization_config=quantization_config,
                device_map="auto" if DEVICE == "cuda" else None,
                torch_dtype=torch.float16 if BITS == 16 else None
            )
            
            # Move model to CPU if not using CUDA
            if DEVICE == "cpu":
                self.model = self.model.to(DEVICE)
                
            print(f"Model loaded successfully!")
            return True
        
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def generate_response(self, query: str, max_length: int = 512) -> str:
        """
        Generate a response based on the input query.
        
        Args:
            query: The tax-related query to process
            max_length: Maximum length of the generated response
            
        Returns:
            The generated text response
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(query, return_tensors="pt").to(DEVICE)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                num_return_sequences=1
            )
        
        # Decode and return response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # For instruction-tuned models, extract just the assistant's response
        if USE_MISTRAL:
            # Mistral format - extract content after [/INST]
            if "[/INST]" in full_response:
                response = full_response.split("[/INST]")[-1].strip()
            else:
                # Fallback to standard extraction
                response = full_response[len(self.tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):].strip()
        elif "<|assistant|>" in full_response:
            # Llama 3.1 format - extract after <|assistant|>
            response = full_response.split("<|assistant|>")[-1].strip()
        else:
            # Generic extraction for other models
            response = full_response[len(self.tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):].strip()
        
        return response


# Create a singleton instance
model_loader = ModelLoader()
