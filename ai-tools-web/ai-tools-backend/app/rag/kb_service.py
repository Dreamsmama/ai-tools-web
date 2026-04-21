from __future__ import annotations

from app.rag.repository import rag_repository
from app.rag.scope import RequestScope


class KbService:
    def create(self, scope: RequestScope, name: str, description: str) -> dict:
        return rag_repository.create_kb(scope, name=name, description=description)

    def list(self, scope: RequestScope) -> list[dict]:
        return rag_repository.list_kbs(scope)


kb_service = KbService()
