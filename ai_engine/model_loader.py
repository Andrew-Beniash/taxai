"""
Model loader for the AI-powered tax law system.
This module uses Hugging Face's API for model inference.
"""

import os
import requests
import torch
import sys
from typing import Dict, List, Union, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM

# Import centralized configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    USE_MISTRAL, 
    CURRENT_MODEL,
    HUGGINGFACE_API_KEY,
    USE_HUGGINGFACE_API,
    USE_CUDA,
    QUANTIZATION_BITS
)

class ModelLoader:
    """Handles loading and optimization of LLM for tax law processing."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
    def load_model(self):
        """Load the model - either using the Hugging Face API or locally."""
        if USE_HUGGINGFACE_API:
            try:
                # Load tokenizer locally for text processing
                print(f"Loading tokenizer for {CURRENT_MODEL}")
                self.tokenizer = AutoTokenizer.from_pretrained(CURRENT_MODEL)
                print(f"Tokenizer loaded successfully!")
                
                # Test the API connection
                response = requests.get(
                    f"{self.api_url}{CURRENT_MODEL}", 
                    headers=self.headers
                )
                if response.status_code == 200:
                    print(f"Successfully connected to Hugging Face API for {CURRENT_MODEL}")
                    return True
                else:
                    print(f"Error connecting to Hugging Face API: {response.status_code} - {response.text}")
                    if response.status_code == 401:
                        print("Invalid API key. Check your HUGGINGFACE_API_KEY in the .env file.")
                    elif response.status_code == 403:
                        print("You don't have permission to use this model. You may need to request access or subscribe.")
                    return False
            
            except Exception as e:
                print(f"Error setting up model: {str(e)}")
                return False
        else:
            # Fallback to local model loading
            print("Using local model loading instead of Hugging Face API.")
            print(f"Loading {CURRENT_MODEL} locally...")
            
            try:
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(CURRENT_MODEL)
                
                # Device configuration
                device = "cuda" if torch.cuda.is_available() and USE_CUDA else "cpu"
                bits = 4 if device == "cuda" else QUANTIZATION_BITS
                
                # Configure quantization for model loading
                quantization_config = None
                if bits == 4 and device == "cuda":
                    from transformers import BitsAndBytesConfig
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4"
                    )
                
                # Load model with quantization if on GPU
                self.model = AutoModelForCausalLM.from_pretrained(
                    CURRENT_MODEL,
                    quantization_config=quantization_config,
                    device_map="auto" if device == "cuda" else None,
                    torch_dtype=torch.float16 if bits == 16 else None
                )
                
                # Move model to CPU if not using CUDA
                if device == "cpu":
                    self.model = self.model.to(device)
                    
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
        if USE_HUGGINGFACE_API:
            if not self.tokenizer:
                raise ValueError("Tokenizer not loaded. Call load_model() first.")
            
            try:
                # Tokenize input to determine input length for response processing
                inputs = self.tokenizer(query, return_tensors="pt")
                
                # Prepare payload for Hugging Face API
                payload = {
                    "inputs": query,
                    "parameters": {
                        "max_new_tokens": max_length,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True,
                        "return_full_text": True  # Return the full response including the prompt
                    }
                }
                
                # Make API request
                response = requests.post(
                    f"{self.api_url}{CURRENT_MODEL}",
                    headers=self.headers,
                    json=payload
                )
                
                # Handle API response
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract generated text based on the response format
                    if isinstance(result, list) and len(result) > 0:
                        full_response = result[0].get('generated_text', '')
                    else:
                        full_response = result.get('generated_text', '')
                    
                    # Process the response based on model type
                    if USE_MISTRAL:
                        # Mistral format - extract content after [/INST]
                        if "[/INST]" in full_response:
                            response_text = full_response.split("[/INST]")[-1].strip()
                        else:
                            # Fallback to standard extraction
                            response_text = full_response[len(self.tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):].strip()
                    elif "<|assistant|>" in full_response:
                        # Llama 3.1 format - extract after <|assistant|>
                        response_text = full_response.split("<|assistant|>")[-1].strip()
                    else:
                        # Generic extraction for other models
                        response_text = full_response[len(self.tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):].strip()
                    
                    return response_text
                else:
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    print(error_msg)
                    return f"I'm sorry, I encountered an error while processing your request. Please try again later. ({response.status_code})"
                    
            except Exception as e:
                print(f"Error in API call: {str(e)}")
                return f"I apologize, but I encountered an error while processing your request. Please try again later. (Error: {str(e)})"
                
        else:
            # Use local model for inference
            if not self.model or not self.tokenizer:
                raise ValueError("Model not loaded. Call load_model() first.")
            
            # Tokenize input
            inputs = self.tokenizer(query, return_tensors="pt")
            if torch.cuda.is_available() and USE_CUDA:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
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
