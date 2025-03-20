"""
Defines the schema for tax law documents in the knowledge base.
This module contains the structure for metadata that accompanies document embeddings.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import date


class TaxLawMetadata(BaseModel):
    """Metadata for tax law documents stored in the knowledge base."""
    
    title: str = Field(..., description="Title of the tax law document")
    source: str = Field(..., description="Source of the document (e.g., IRS, Tax Court)")
    document_id: str = Field(..., description="Unique identifier for the document")
    publication_date: Optional[date] = Field(None, description="Publication date of the document")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction (e.g., Federal, State)")
    document_type: Optional[str] = Field(None, description="Type of document (e.g., Regulation, Ruling, Publication)")
    sections: Optional[List[str]] = Field(None, description="Relevant sections or chapters")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    url: Optional[str] = Field(None, description="URL to the original document")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary format for ChromaDB."""
        result = self.model_dump()
        # Convert date objects to string for ChromaDB compatibility
        if self.publication_date:
            result["publication_date"] = self.publication_date.isoformat()
        return result
