"""
Chat summary logic ported from miniprogram-2/cloudfunctions/summarize/index.js.
Not migrated: WeChat-specific env; local usage quota (summary_used_count) stays on client.
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


async def _call_dashscope(messages: List[Dict[str, str]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": settings.dashscope_model,
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
            "你是“聊天重点总结器”。只做信息提炼与行动整理，不编造事实。"
            "只输出严格 JSON，不要 markdown，不要多余文本。"
        ),
    }
    user_message = {
        "role": "user",
        "content": f"""
请把下面聊天内容整理为严格 JSON（不要markdown、不要多余文本）：
{{
  "summary": ["...","...","..."],
  "todos": [{{"owner":"我/对方/未明确","task":"...","due":""}}],
  "risks": ["...","..."],
  "reply": "一段可直接复制发送的确认话术"
}}

规则：
- summary：3~5条，短句，提炼结论/共识/决定
- todos：2~6条，能执行的动作，owner 尽量判断（我/对方/未明确），due 没有就空字符串
- risks：2~5条，没说清/容易扯皮/需要确认的点
- reply：1段，可直接发群/私聊的确认话术（简洁、不强势）

聊天内容：
{text}
""".strip(),
    }

    try:
        raw = await _call_dashscope([system_message, user_message])
        data = parse_summary_model_output(raw)

        if (
            not data.summary
            and not data.todos
            and not data.risks
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
