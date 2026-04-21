from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from fastapi import Header

from app.config import settings


@dataclass(frozen=True)
class RequestScope:
    user_id: str
    workspace_id: str
    trace_id: str


def build_default_scope() -> RequestScope:
    return RequestScope(
        user_id=settings.rag_default_user_id,
        workspace_id=settings.rag_default_workspace_id,
        trace_id=uuid.uuid4().hex,
    )


def get_request_scope(
    x_user_id: Optional[str] = Header(default=None),
    x_workspace_id: Optional[str] = Header(default=None),
    x_trace_id: Optional[str] = Header(default=None),
) -> RequestScope:
    return RequestScope(
        user_id=(x_user_id or settings.rag_default_user_id).strip(),
        workspace_id=(x_workspace_id or settings.rag_default_workspace_id).strip(),
        trace_id=(x_trace_id or uuid.uuid4().hex).strip(),
    )
