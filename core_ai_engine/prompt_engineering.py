"""
Prompt Engineering module for Tax Law AI queries.

This module handles the creation of optimized prompts for tax law queries,
integrating retrieved context from tax databases and ensuring responses
include proper citations and legal references.
"""

def create_tax_query_prompt(query, context_docs, include_citations=True):
    """
    Creates an optimized prompt for tax law queries with relevant context.
    
    Args:
        query (str): The user's tax law question
        context_docs (list): List of relevant tax law documents/citations
        include_citations (bool): Whether to instruct the model to include citations
    
    Returns:
        str: A formatted prompt ready for the LLM
    """
    # Start with a clear system instruction
    system_instruction = (
        "You are a tax law assistant providing accurate information based on official tax regulations. "
        "Answer the following tax question using the provided tax law references. "
        "Be concise, accurate, and focus only on factual information from authoritative sources."
    )
    
    # Format the retrieved context documents
    formatted_context = ""
    for i, doc in enumerate(context_docs, 1):
        # Extract document content and source
        content = doc.get("content", "")
        source = doc.get("source", f"Reference {i}")
        
        # Add to the formatted context with clear citation
        formatted_context += f"Reference [{i}]: {source}\n{content}\n\n"
    
    # Build citation instruction if needed
    citation_instruction = ""
    if include_citations:
        citation_instruction = (
            "Important: In your answer, cite specific references by their number (e.g., [1], [2]) "
            "when using information from them. If information is not found in the provided references, "
            "clearly state this rather than providing uncertain information."
        )
    
    # Final prompt assembly
    prompt = f"""{system_instruction}

TAX LAW REFERENCES:
{formatted_context}

{citation_instruction}

USER QUESTION: {query}

ANSWER:"""
    
    return prompt


def format_ai_response_with_citations(response, context_docs):
    """
    Post-processes AI responses to ensure proper formatting and citation handling.
    
    Args:
        response (str): The raw AI-generated response
        context_docs (list): The context documents used in the query
    
    Returns:
        dict: A structured response with answer text and formatted citations
    """
    # Extract sources from context documents for the bibliography
    sources = []
    for i, doc in enumerate(context_docs, 1):
        source = doc.get("source", f"Reference {i}")
        sources.append({"id": i, "citation": source})
    
    # Create a structured response
    structured_response = {
        "answer": response,
        "sources": sources
    }
    
    return structured_response


def generate_tax_law_response(query, context_docs, model, tokenizer, max_length=512):
    """
    End-to-end function to generate AI responses to tax law queries.
    
    Args:
        query (str): The user's tax question
        context_docs (list): Relevant tax law documents retrieved
        model: The LLM model (Mistral, Llama, etc.)
        tokenizer: The tokenizer for the model
        max_length (int): Maximum response length
        
    Returns:
        dict: A formatted response with citations
    """
    # Create the optimized prompt
    prompt = create_tax_query_prompt(query, context_docs)
    
    # Prepare for model inference
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    
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
    
    return formatted_response
