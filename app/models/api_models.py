from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class QueryRequest(BaseModel):
    """
    Model for tax law query requests
    """
    query: str = Field(description="The tax law query to process")


class Citation(BaseModel):
    """
    Model for citations in the response
    """
    source: str = Field(description="Citation source (e.g., IRS Section)")
    url: Optional[str] = Field(default=None, description="URL to the source document")
    text: Optional[str] = Field(default=None, description="Cited text")


class QueryResponse(BaseModel):
    """
    Model for tax law query responses
    """
    response: str = Field(description="AI-generated response to the query")
    citations: Optional[List[Citation]] = Field(default=None, description="Source citations for the response")
    confidence_score: Optional[float] = Field(default=None, description="Confidence score for the response (0-1)")
