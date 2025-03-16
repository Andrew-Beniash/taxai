"""
Utility functions for AI/ML library verification and testing.
This module provides functions to test if the installed AI/ML libraries
are working correctly and ready for use in the tax law application.
"""

import importlib
import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_library_imports() -> Dict[str, bool]:
    """
    Checks if all required AI/ML libraries are properly installed.
    
    Returns:
        Dict[str, bool]: A dictionary with library names as keys and their import status as values.
    """
    required_libraries = [
        "torch",
        "transformers",
        "langchain",
        "chromadb",
        "faiss",
        "sentence_transformers"
    ]
    
    import_status = {}
    
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
            import_status[lib] = True
            logger.info(f"Successfully imported {lib}")
        except ImportError as e:
            import_status[lib] = False
            logger.error(f"Failed to import {lib}: {str(e)}")
    
    return import_status

def test_pytorch() -> bool:
    """
    Tests PyTorch installation by performing a simple tensor operation.
    
    Returns:
        bool: True if PyTorch is working correctly, False otherwise.
    """
    try:
        import torch
        
        # Create a simple tensor
        x = torch.rand(5, 3)
        logger.info(f"Created PyTorch tensor: {x.shape}")
        
        # Check if CUDA is available
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            logger.info("CUDA is available for PyTorch")
        else:
            logger.info("CUDA is not available, PyTorch will use CPU")
        
        return True
    except Exception as e:
        logger.error(f"PyTorch test failed: {str(e)}")
        return False

def test_transformers() -> bool:
    """
    Tests transformers library by loading a tokenizer.
    
    Returns:
        bool: True if transformers is working correctly, False otherwise.
    """
    try:
        from transformers import AutoTokenizer
        
        # Load a small tokenizer
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased", local_files_only=False)
        logger.info(f"Loaded tokenizer: {tokenizer.__class__.__name__}")
        
        # Test tokenization
        text = "Testing the transformers library for tax law queries."
        tokens = tokenizer(text, return_tensors="pt")
        logger.info(f"Tokenized input with {len(tokens['input_ids'][0])} tokens")
        
        return True
    except Exception as e:
        logger.error(f"Transformers test failed: {str(e)}")
        return False

def test_langchain() -> bool:
    """
    Tests langchain functionality with a basic LLMChain.
    
    Returns:
        bool: True if langchain is working correctly, False otherwise.
    """
    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_community.llms.fake import FakeListLLM
        from langchain.chains import LLMChain
        
        # Create a simple prompt template
        template = "What tax laws apply to {topic}?"
        prompt = PromptTemplate.from_template(template)
        
        # Use FakeListLLM to test without actual API calls
        responses = ["Tax laws related to small businesses include Section 179 deductions."]
        fake_llm = FakeListLLM(responses=responses)
        
        # Create and test the chain
        chain = LLMChain(llm=fake_llm, prompt=prompt)
        result = chain.invoke({"topic": "small businesses"})
        logger.info(f"LangChain test result: {result}")
        
        return True
    except Exception as e:
        logger.error(f"LangChain test failed: {str(e)}")
        return False

def test_vector_db() -> bool:
    """
    Tests vector database functionality (ChromaDB or FAISS).
    
    Returns:
        bool: True if vector database is working correctly, False otherwise.
    """
    try:
        # Test ChromaDB
        import chromadb
        client = chromadb.Client()
        collection = client.create_collection(name="test_collection")
        logger.info(f"Created ChromaDB collection: {collection.name}")
        
        # Add documents
        collection.add(
            documents=["Tax law document 1", "Tax law document 2"],
            metadatas=[{"source": "IRS"}, {"source": "Tax Court"}],
            ids=["doc1", "doc2"]
        )
        
        # Query
        results = collection.query(query_texts=["tax law"], n_results=2)
        logger.info(f"ChromaDB query returned {len(results['documents'][0])} documents")
        
        # Test FAISS
        import numpy as np
        import faiss
        
        # Create a simple index
        dimension = 128
        index = faiss.IndexFlatL2(dimension)
        
        # Add vectors
        vectors = np.random.random((10, dimension)).astype('float32')
        index.add(vectors)
        
        # Search
        query = np.random.random((1, dimension)).astype('float32')
        distances, indices = index.search(query, k=2)
        logger.info(f"FAISS search returned {len(indices[0])} results")
        
        return True
    except Exception as e:
        logger.error(f"Vector database test failed: {str(e)}")
        return False

def run_all_tests() -> Dict[str, bool]:
    """
    Runs all library tests and returns their status.
    
    Returns:
        Dict[str, bool]: A dictionary with test names as keys and their status as values.
    """
    test_results = {
        "library_imports": check_library_imports(),
        "pytorch": test_pytorch(),
        "transformers": test_transformers(),
        "langchain": test_langchain(),
        "vector_db": test_vector_db()
    }
    
    # Log overall results
    failures = [name for name, result in test_results.items() 
               if not result or (isinstance(result, dict) and not all(result.values()))]
    
    if not failures:
        logger.info("All AI/ML libraries are working correctly!")
    else:
        logger.warning(f"Some tests failed: {', '.join(failures)}")
    
    return test_results

if __name__ == "__main__":
    # Run tests when this module is executed directly
    run_all_tests()
