"""
Workplace communication understanding + reply generation service.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from app.llm.dashscope_client import call_dashscope
from app.utils.llm_json import parse_summary_model_output
from app.schemas import SummaryEnvelope
from app.utils import user_messages as user_msg

logger = logging.getLogger(__name__)


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


async def _call_dashscope(messages: List[Dict[str, str]], model: str | None = None) -> str:
    """Backward-compatible alias; prefer ``app.llm.dashscope_client.call_dashscope``."""
    return await call_dashscope(messages, model=model)


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
