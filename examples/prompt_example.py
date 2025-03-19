def generate_tax_law_response_with_device(query, context_docs, model, tokenizer, max_length=512):
    """Wrapper around generate_tax_law_response that handles device placement correctly"""
    # Create the optimized prompt
    prompt = create_tax_query_prompt(query, context_docs)
    
    # Identify the device the model is on
    device = next(model.parameters()).device
    
    # Prepare for model inference with proper device placement
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    # Move inputs to the same device as the model
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate response from the model
    outputs = model.generate(
        **inputs, 
        max_length=max_length,
        temperature=0.3,  # Lower temperature for more factual responses
        do_sample=True,
        top_p=0.9,
        repetition_penalty=1.2  # Discourage repetitive text
    )
    
    # Decode the model output
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Clean up the response to extract just the answer part
    if "ANSWER:" in prompt and "ANSWER:" in response_text:
        response_text = response_text.split("ANSWER:", 1)[1].strip()
        
    # Format with proper citations
    formatted_response = format_ai_response_with_citations(response_text, context_docs)
    
    return formatted_response"""
Example usage of the prompt engineering module for tax law queries.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
import os

# Add the parent directory to path so we can import the core_ai_engine module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_ai_engine.prompt_engineering import generate_tax_law_response

# Sample function to simulate retrieving tax laws
def mock_retrieve_tax_laws(query):
    """Mock function to simulate retrieval from a vector database"""
    # This would be replaced by actual vector search in production
    return [
        {
            "content": "Section 179 allows businesses to deduct the full purchase price of qualifying equipment purchased or financed during the tax year. The maximum deduction for 2024 is $1,160,000.",
            "source": "IRS Publication 946, Section 179 Deduction"
        },
        {
            "content": "To qualify for Section 179, equipment must be used for business purposes more than 50% of the time. If business use drops below 51%, part of the deduction may need to be recaptured.",
            "source": "IRS Code § 179(d)(10)"
        }
    ]

def main():
    # Load model and tokenizer (use smaller model for example)
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # Change to your actual model
    
    print("Loading model and tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Try to load with device_map first
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
        except ImportError:
            print("Accelerate library not found. Loading model without device_map.")
            model = AutoModelForCausalLM.from_pretrained(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("\nTo fix this, please run: pip install 'accelerate>=0.26.0' transformers torch")
        return
    
    # Example query
    user_query = "What equipment qualifies for Section 179 deduction and what is the maximum deduction amount?"
    
    # Retrieve relevant tax laws
    context_docs = mock_retrieve_tax_laws(user_query)
    
    # Generate response using our prompt engineering
    print("Generating AI response...")
    try:
        response = generate_tax_law_response(user_query, context_docs, model, tokenizer)
        
        # Display results
        print("\nUser Query:")
        print(user_query)
        print("\nAI Response:")
        print(response["answer"])
        print("\nSources:")
        for source in response["sources"]:
            print(f"[{source['id']}] {source['citation']}")
    except Exception as e:
        print(f"Error generating response: {e}")
        print("Make sure you have installed all required dependencies.")
        print("pip install 'accelerate>=0.26.0' transformers torch")

if __name__ == "__main__":
    main()
