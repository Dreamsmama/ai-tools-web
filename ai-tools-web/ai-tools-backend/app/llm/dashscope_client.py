"""
Unified DashScope text-generation HTTP client (R3).

All services should call ``call_dashscope`` instead of duplicating httpx payload logic.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

import httpx

from app.config import settings

Message = Dict[str, str]


def _extract_content(body: dict) -> Optional[str]:
    content = None
    try:
        choices = body.get("output", {}).get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content")
        if content is None:
            content = body.get("output", {}).get("text")
        if content is None and choices:
            content = choices[0].get("text")
    except (TypeError, IndexError, AttributeError):
        content = None
    return content if content is None or isinstance(content, str) else str(content)


async def call_dashscope(
    messages: List[Message],
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout_seconds: float | None = None,
    connect_timeout_seconds: float | None = None,
) -> str:
    """
    Call DashScope generation API and return assistant text content.

    Per-call kwargs override ``settings`` defaults (temperature, max_tokens, timeout).
    """
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    resolved_model = model or settings.dashscope_model
    resolved_temperature = (
        settings.dashscope_temperature if temperature is None else temperature
    )
    resolved_max_tokens = (
        settings.dashscope_max_tokens if max_tokens is None else max_tokens
    )
    limit = (
        settings.dashscope_timeout_seconds
        if timeout_seconds is None
        else timeout_seconds
    )

    payload = {
        "model": resolved_model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": resolved_temperature,
            "max_tokens": resolved_max_tokens,
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if connect_timeout_seconds is not None:
        timeout = httpx.Timeout(limit, connect=connect_timeout_seconds)
    else:
        timeout = httpx.Timeout(limit)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            settings.dashscope_url,
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        body = resp.json()

    content = _extract_content(body)
    if not content:
        snippet = json.dumps(body, ensure_ascii=False)[:500]
        raise RuntimeError(f"DashScope 返回为空或结构不匹配：{snippet}")

    return content
