from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class QueryRequest(BaseModel):
    """Request model for RAG query"""
    question: str = Field(..., description="The question to answer")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")

class Source(BaseModel):
    """Source document metadata"""
    chunk_id: str
    doc_title: str
    content: str
    score: float

class QueryResponse(BaseModel):
    """Response model for RAG query"""
    question: str
    answer: str
    sources: List[Source]
    metadata: Dict = Field(default_factory=dict)

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    index_loaded: bool
    total_chunks: int

class StatsResponse(BaseModel):
    """System statistics"""
    total_queries: int
    avg_latency_ms: float
    total_tokens_used: int
    avg_tokens_per_query: float