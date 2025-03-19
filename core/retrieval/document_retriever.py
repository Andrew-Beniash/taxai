import chromadb
from sentence_transformers import SentenceTransformer
import re
from typing import List, Dict, Any

class TaxLawRetriever:
    """Class for retrieving relevant tax law documents based on user queries."""
    
    def __init__(self, collection_name: str = "tax_laws", embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the tax law retriever with ChromaDB and embedding model.
        
        Args:
            collection_name: Name of the ChromaDB collection containing tax law documents
            embedding_model_name: Name of the sentence transformer model for embeddings
        """
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path="./db")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(collection_name)
        
        # Load the embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)
    
    def retrieve_tax_laws(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Searches tax law knowledge base for relevant references using hybrid search.
        
        Args:
            query: The user's tax-related query
            n_results: Number of results to retrieve
            
        Returns:
            List of dictionaries containing relevant tax law documents with their metadata
        """
        # Extract keywords for potential filtering
        keywords = self._extract_keywords(query)
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Perform semantic search using ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results * 2  # Get more results than needed for filtering
        )
        
        # Process results
        documents = []
        for i, (doc_id, doc_content, metadata) in enumerate(zip(
            results["ids"][0], results["documents"][0], results["metadatas"][0]
        )):
            # Calculate keyword match score
            keyword_score = self._calculate_keyword_score(doc_content, keywords)
            
            documents.append({
                "id": doc_id,
                "content": doc_content,
                "metadata": metadata,
                "relevance_score": results["distances"][0][i] if "distances" in results else 0,
                "keyword_score": keyword_score
            })
        
        # Sort by combined score (semantic + keyword)
        documents.sort(key=lambda x: x["relevance_score"] + x["keyword_score"], reverse=True)
        
        # Return the top n results
        return documents[:n_results]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract potential tax-related keywords from the query.
        
        Args:
            query: The user's tax-related query
            
        Returns:
            List of extracted keywords
        """
        # Simple keyword extraction - could be enhanced with NLP or tax-specific terms
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out common stopwords
        stopwords = {"the", "and", "or", "a", "an", "in", "on", "at", "to", "for", "with", "by"}
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords
    
    def _calculate_keyword_score(self, document: str, keywords: List[str]) -> float:
        """
        Calculate a score based on keyword matches in the document.
        
        Args:
            document: Tax law document content
            keywords: List of extracted keywords from the query
            
        Returns:
            Keyword match score
        """
        if not keywords:
            return 0.0
        
        # Count keyword occurrences
        document_lower = document.lower()
        matches = sum(1 for keyword in keywords if keyword in document_lower)
        
        # Normalize score based on document length and number of keywords
        score = matches / (len(keywords) * (len(document.split()) / 100))
        
        return min(score, 1.0)  # Cap at 1.0
