from __future__ import annotations

import time
from typing import Dict, List

from app.config import settings
from app.rag.prompt_builder import build_prompt
from app.rag.query_pipeline import query_pipeline
from app.rag.repository import rag_repository
from app.rag.retrieval_service import retrieval_service
from app.rag.scope import RequestScope
from app.rag.schemas import AskResponse, Citation
from app.summarize_service import _call_dashscope


class RagQaService:
    def _fallback_answer(self, query: str, hits: List[Dict]) -> str:
        if not hits:
            return (
                "当前未检索到可用知识片段，暂时无法给出可靠答案。"
                "请先确认文档已入库，或换个问题再试。"
            )
        lines = [
            "外部模型连接暂时不可用，以下基于知识库检索结果给出简要答复：",
            f"问题：{query}",
            "",
            "参考要点：",
        ]
        for idx, item in enumerate(hits[:3], start=1):
            lines.append(f"{idx}. {item['content'][:200]}")
        lines.append("")
        lines.append("建议稍后重试，以获得更完整的自然语言回答。")
        return "\n".join(lines)

    async def ask(self, scope: RequestScope, kb_id: str, query: str, top_k: int) -> AskResponse:
        started_at = time.perf_counter()
        normalized_query = query_pipeline.normalize_query(query)
        final_top_k = query_pipeline.clamp_top_k(top_k, settings.rag_top_k)
        retrieval_latency_ms = 0
        generation_latency_ms = 0
        prepared_hits = []
        try:
            retrieval_started_at = query_pipeline.start_timer()
            hits = await retrieval_service.search(scope, kb_id, normalized_query, final_top_k)
            retrieval_latency_ms = query_pipeline.elapsed_ms(retrieval_started_at)
            prepared_hits = query_pipeline.prepare_retrieval_result(hits)

            citations = []
            for hit in prepared_hits:
                citations.append(
                    Citation(
                        document_id=hit["document_id"],
                        filename=hit["filename"],
                        chunk_id=hit["chunk_id"],
                        score=hit["score"],
                        content_snippet=hit["content"][:220],
                    )
                )
            system, user = build_prompt(normalized_query, prepared_hits)
            generation_started_at = query_pipeline.start_timer()
            generation_error = ""
            try:
                answer = await _call_dashscope([system, user])
            except Exception as model_err:
                generation_error = str(model_err)[:300]
                answer = self._fallback_answer(normalized_query, prepared_hits)
            generation_latency_ms = query_pipeline.elapsed_ms(generation_started_at)
            total_latency_ms = int((time.perf_counter() - started_at) * 1000)
            rag_repository.append_query_log(
                scope=scope,
                kb_id=kb_id,
                query_text=normalized_query,
                top_k=final_top_k,
                retrieved_chunk_ids=[c.chunk_id for c in citations],
                retrieved_chunks=prepared_hits,
                answer=answer,
                status="success" if not generation_error else "degraded",
                error_message=generation_error,
                trace_id=scope.trace_id,
                retrieval_latency_ms=retrieval_latency_ms,
                generation_latency_ms=generation_latency_ms,
                total_latency_ms=total_latency_ms,
            )
            return AskResponse(
                answer=answer,
                citations=citations,
                trace_id=scope.trace_id,
                retrieval_latency_ms=retrieval_latency_ms,
                generation_latency_ms=generation_latency_ms,
                total_latency_ms=total_latency_ms,
            )
        except Exception as err:
            total_latency_ms = int((time.perf_counter() - started_at) * 1000)
            rag_repository.append_query_log(
                scope=scope,
                kb_id=kb_id,
                query_text=normalized_query,
                top_k=final_top_k,
                retrieved_chunk_ids=[],
                retrieved_chunks=prepared_hits,
                answer="",
                status="failed",
                error_message=str(err)[:1000],
                trace_id=scope.trace_id,
                retrieval_latency_ms=retrieval_latency_ms,
                generation_latency_ms=generation_latency_ms,
                total_latency_ms=total_latency_ms,
            )
            raise


rag_qa_service = RagQaService()
