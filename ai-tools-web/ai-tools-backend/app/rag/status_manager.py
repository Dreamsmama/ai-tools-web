from __future__ import annotations

from app.rag.constants import ALLOWED_TRANSITIONS


def ensure_transition(old_status: str, new_status: str) -> None:
    if old_status == new_status:
        return
    allowed = ALLOWED_TRANSITIONS.get(old_status, set())
    if new_status not in allowed:
        raise ValueError(f"非法状态流转: {old_status} -> {new_status}")
