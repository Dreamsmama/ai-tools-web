from __future__ import annotations

import math
from typing import Any, Dict, List

from app.rag.embedding_service import embedding_service
from app.rag.repository import rag_repository
from app.rag.scope import RequestScope
from app.rag.vector_store import vector_store


def _cosine(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1)) or 1.0
    n2 = math.sqrt(sum(b * b for b in v2)) or 1.0
    return dot / (n1 * n2)


class RetrievalService:
    async def search(self, scope: RequestScope, kb_id: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        if not rag_repository.kb_exists_in_scope(scope, kb_id):
            raise ValueError("知识库不存在或不在当前作用域")
        q_vec = (await embedding_service.embed([query]))[0]
        rows = vector_store.query_kb_chunks(scope, kb_id)
        scored = []
        for row in rows:
            score = _cosine(q_vec, row["embedding_vector"])
            scored.append(
                {
                    "chunk_id": row["id"],
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "content": row["content"],
                    "score": float(score),
                }
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


retrieval_service = RetrievalService()
