"""
Workplace communication understanding + reply generation service.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import httpx

from app.config import settings
from app.llm_json import parse_summary_model_output
from app.schemas import SummaryEnvelope
from app import user_messages as user_msg

logger = logging.getLogger(__name__)


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


async def _call_dashscope(messages: List[Dict[str, str]], model: str | None = None) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": model or settings.dashscope_model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": settings.dashscope_temperature,
            "max_tokens": settings.dashscope_max_tokens,
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(settings.dashscope_timeout_seconds)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(settings.dashscope_url, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()

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

    if not content:
        snippet = json.dumps(body, ensure_ascii=False)[:500]
        raise RuntimeError(f"DashScope 返回为空或结构不匹配：{snippet}")

    return content if isinstance(content, str) else str(content)


async def summarize_chat(input_text: str) -> SummaryEnvelope:
    text = _safe_trim(input_text)
    if not text:
        return SummaryEnvelope(code=400, message=user_msg.msg_input_empty())

    system_message = {
        "role": "system",
        "content": (
            "你是“职场沟通理解与回复助手”。帮用户看懂对方真实意图，并给出能直接发送的回复。"
            "只输出严格 JSON，不要 markdown，不要多余文本。"
        ),
    }
    user_message = {
        "role": "user",
        "content": f"""
请把下面聊天内容输出为严格 JSON（不要markdown、不要多余文本）：
{{
  "intent": ["...","..."],
  "emotion": ["...","..."],
  "strategy": ["...","...","..."],
  "reply": "一段可直接复制发送的回复"
}}

规则：
- intent：2~4条，判断对方真实诉求（显性+隐性），短句，贴近职场场景
- emotion：2~4条，判断对方沟通情绪和压力状态（如着急、担心风险、想要确定性）
- strategy：3~5条，给用户可执行的应对策略，强调如何减少扯皮、推进事情
- reply：1段可直接发送的话术，语气专业不僵硬，给出边界和下一步；避免空话和学术表达

聊天内容：
{text}
""".strip(),
    }

    try:
        raw = await _call_dashscope([system_message, user_message])
        data = parse_summary_model_output(raw)

        if (
            not data.intent
            and not data.emotion
            and not data.strategy
            and not data.reply
        ):
            return SummaryEnvelope(code=500, message=user_msg.msg_model_empty())

        if data.reply and len(data.reply) > 400:
            data = data.model_copy(update={"reply": data.reply[:400]})

        return SummaryEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("dashscope timeout")
        return SummaryEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("summarize error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return SummaryEnvelope(code=504, message=user_msg.msg_timeout())
        return SummaryEnvelope(code=500, message=user_msg.from_exception(err))
