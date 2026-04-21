from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Envelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[Any] = None


class KnowledgeBaseCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)


class KnowledgeBaseItem(BaseModel):
    id: str
    name: str
    description: str
    created_at: str


class DocumentItem(BaseModel):
    id: str
    kb_id: str
    filename: str
    mime_type: str
    file_size: int
    file_hash: str
    status: str
    content_summary: str
    error_message: str
    created_at: str
    updated_at: str


class RetryRequest(BaseModel):
    document_id: str


class AskRequest(BaseModel):
    kb_id: str
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    score: float
    content_snippet: str


class AskResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    trace_id: str
    retrieval_latency_ms: int = 0
    generation_latency_ms: int = 0
    total_latency_ms: int = 0
