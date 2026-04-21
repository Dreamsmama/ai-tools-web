from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class QueryPipelineResult:
    normalized_query: str
    top_k: int
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    retrieval_latency_ms: int = 0
    generation_latency_ms: int = 0
    total_latency_ms: int = 0


class QueryPipeline:
    """Composable query pipeline with extension slots.

    Future slots:
    - query rewrite
    - hybrid search (keyword + vector)
    - rerank
    - cache
    - audit policy
    """

    def start_timer(self) -> float:
        return time.perf_counter()

    def elapsed_ms(self, started_at: float) -> int:
        return int((time.perf_counter() - started_at) * 1000)

    def normalize_query(self, query: str) -> str:
        return " ".join(query.strip().split())

    def clamp_top_k(self, top_k: int, default_top_k: int) -> int:
        if top_k <= 0:
            return default_top_k
        return min(top_k, 20)

    def prepare_retrieval_result(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prepared = []
        for item in hits:
            prepared.append(
                {
                    "chunk_id": item["chunk_id"],
                    "document_id": item["document_id"],
                    "filename": item["filename"],
                    "score": float(item["score"]),
                    "content": item["content"],
                }
            )
        return prepared


query_pipeline = QueryPipeline()
