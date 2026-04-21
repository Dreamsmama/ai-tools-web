from __future__ import annotations

from app.rag.ingest_service import ingest_service
from app.rag.repository import rag_repository
from app.rag.scope import RequestScope
from app.rag.storage import storage_provider


class DocumentService:
    async def upload(
        self,
        scope: RequestScope,
        kb_id: str,
        filename: str,
        mime_type: str,
        file_bytes: bytes,
    ) -> dict:
        storage_path, file_hash = storage_provider.save(file_bytes, filename)
        doc = rag_repository.create_document(
            scope=scope,
            kb_id=kb_id,
            filename=filename,
            mime_type=mime_type or "application/octet-stream",
            file_size=len(file_bytes),
            file_hash=file_hash,
            storage_path=storage_path,
        )
        return doc

    async def ingest(self, scope: RequestScope, document_id: str) -> dict:
        return await ingest_service.process_document(scope, document_id)

    async def retry(self, scope: RequestScope, document_id: str) -> dict:
        return await ingest_service.process_document(scope, document_id)

    def get(self, scope: RequestScope, document_id: str) -> dict:
        return rag_repository.get_document(scope, document_id)


document_service = DocumentService()
