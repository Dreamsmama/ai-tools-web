"""SSE helpers for xiaohongshu agent progress (R8)."""

from __future__ import annotations

import json
from typing import Any

from app.agents.xiaohongshu.spec import pipeline_step_ids, step_labels

# Re-export for callers that imported STEP_LABELS historically.
STEP_LABELS = step_labels()


def format_sse_message(event: str, payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False)
    return f"event: {event}\ndata: {body}\n\n"
