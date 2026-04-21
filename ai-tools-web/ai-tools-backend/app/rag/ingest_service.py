from __future__ import annotations

from app.rag.chunk_service import chunk_service
from app.rag.constants import (
    DOC_STATUS_EMBEDDING,
    DOC_STATUS_FAILED,
    DOC_STATUS_INDEXED,
    DOC_STATUS_PARSED,
    DOC_STATUS_PARSING,
)
from app.rag.embedding_service import embedding_service
from app.rag.parser_service import parser_service
from app.rag.repository import rag_repository
from app.rag.scope import RequestScope
from app.rag.status_manager import ensure_transition
from app.rag.text_cleaner import clean_text
from app.rag.storage import storage_provider
from app.rag.vector_store import vector_store


class IngestService:
    async def process_document(self, scope: RequestScope, document_id: str) -> dict:
        doc = rag_repository.get_document(scope, document_id)
        try:
            ensure_transition(doc["status"], DOC_STATUS_PARSING)
            rag_repository.update_document_status(scope, document_id, DOC_STATUS_PARSING)

            file_bytes = storage_provider.load(doc["storage_path"])
            parsed_text = parser_service.parse(file_bytes, doc["mime_type"], doc["filename"])
            cleaned = clean_text(parsed_text)
            if not cleaned:
                raise ValueError("文档解析后无有效文本")

            ensure_transition(DOC_STATUS_PARSING, DOC_STATUS_PARSED)
            summary = cleaned[:280]
            rag_repository.update_document_status(
                scope, document_id, DOC_STATUS_PARSED, content_summary=summary
            )

            ensure_transition(DOC_STATUS_PARSED, DOC_STATUS_EMBEDDING)
            rag_repository.update_document_status(scope, document_id, DOC_STATUS_EMBEDDING)

            split_chunks = chunk_service.split(cleaned)
            embeddings = await embedding_service.embed([c.content for c in split_chunks])
            chunk_rows = []
            for c, emb in zip(split_chunks, embeddings):
                chunk_rows.append(
                    {
                        "chunk_index": c.index,
                        "content": c.content,
                        "metadata": c.metadata,
                        "embedding": emb,
                    }
                )
            vector_store.upsert_document_chunks(scope, doc["kb_id"], document_id, chunk_rows)
            ensure_transition(DOC_STATUS_EMBEDDING, DOC_STATUS_INDEXED)
            rag_repository.update_document_status(scope, document_id, DOC_STATUS_INDEXED)
        except Exception as err:
            rag_repository.update_document_status(
                scope,
                document_id,
                DOC_STATUS_FAILED,
                error_message=str(err)[:1000],
                increase_retry=True,
            )
            raise
        return rag_repository.get_document(scope, document_id)


ingest_service = IngestService()
