from __future__ import annotations

from typing import Any, Dict, List

from app.config import settings
from app.rag.repository import rag_repository
from app.rag.scope import RequestScope


class VectorStore:
    """Vector storage abstraction boundary."""

    def upsert_document_chunks(
        self,
        scope: RequestScope,
        kb_id: str,
        document_id: str,
        chunks: List[Dict[str, Any]],
    ) -> None:
        raise NotImplementedError

    def query_kb_chunks(self, scope: RequestScope, kb_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class PostgresVectorStore(VectorStore):
    """Current default: persists vectors in PostgreSQL pgvector."""

    def upsert_document_chunks(
        self,
        scope: RequestScope,
        kb_id: str,
        document_id: str,
        chunks: List[Dict[str, Any]],
    ) -> None:
        rag_repository.replace_chunks_with_vectors(scope, kb_id, document_id, chunks)

    def query_kb_chunks(self, scope: RequestScope, kb_id: str) -> List[Dict[str, Any]]:
        return rag_repository.list_vectors_by_kb(scope, kb_id)


class ExternalVectorStore(VectorStore):
    """Placeholder for future pgvector/milvus/elasticsearch adapters."""

    def upsert_document_chunks(
        self,
        scope: RequestScope,
        kb_id: str,
        document_id: str,
        chunks: List[Dict[str, Any]],
    ) -> None:
        raise NotImplementedError("external vector store adapter is not implemented yet")

    def query_kb_chunks(self, scope: RequestScope, kb_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError("external vector store adapter is not implemented yet")


def build_vector_store() -> VectorStore:
    backend = settings.rag_vector_store_backend.strip().lower()
    if backend in {"pgvector", "postgres"}:
        return PostgresVectorStore()
    if backend in {"milvus", "es"}:
        return ExternalVectorStore()
    raise ValueError(f"unsupported rag_vector_store_backend: {backend}")


vector_store = build_vector_store()
