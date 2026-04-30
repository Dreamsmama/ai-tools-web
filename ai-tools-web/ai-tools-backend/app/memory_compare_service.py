from __future__ import annotations

import logging
from typing import Any

import httpx

from app import user_messages as user_msg
from app.llm_json import try_parse_json_object
from app.schemas import MemoryCompareData, MemoryCompareEnvelope, StructuredMemory
from app.summarize_service import _call_dashscope

logger = logging.getLogger(__name__)

MEMORY_FALLBACK = "当前聊天信息不足，建议补充更多背景"


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


def _normalize_memory(obj: dict[str, Any] | None) -> StructuredMemory:
    src = obj or {}
    events = src.get("关键事件")
    event_list = []
    if isinstance(events, list):
        event_list = [str(item).strip() for item in events if str(item).strip()]

    return StructuredMemory(
        职业=_safe_trim(src.get("职业")),
        目标=_safe_trim(src.get("目标")),
        情绪=_safe_trim(src.get("情绪") or src.get("当前情绪")),
        风险倾向=_safe_trim(src.get("风险倾向")),
        关键事件=event_list[:6],
    )


def _has_memory(memory: StructuredMemory) -> bool:
    return bool(
        memory.职业
        or memory.目标
        or memory.情绪
        or memory.风险倾向
        or memory.关键事件
    )


async def extract_memory(chat_content: str) -> StructuredMemory:
    system_message = {
        "role": "system",
        "content": "你是一个信息抽取助手，只返回严格 JSON，不要解释。",
    }
    user_message = {
        "role": "user",
        "content": f"""
你是一个信息抽取助手，请从以下聊天记录中提取用户的关键信息，输出JSON：

字段包括：
- 职业
- 目标
- 当前情绪
- 风险倾向（保守/中等/激进）
- 关键事件（数组）

抽取要求：
- 优先保留可验证的事实（例如薪资、年限、岗位、时间点、城市、家庭压力等）
- 如果出现数字信息（如 18k、3年），尽量放入“关键事件”

只返回JSON，不要解释

聊天记录：
{chat_content}
""".strip(),
    }
    raw = await _call_dashscope([system_message, user_message])
    parsed = try_parse_json_object(raw)
    return _normalize_memory(parsed)


async def generate_normal_answer(question: str) -> str:
    system_message = {
        "role": "system",
        "content": (
            "你是一个通用问题助手。"
            "回答自然清晰，提供可执行建议。"
            "严格基于当前问题，不使用任何历史聊天背景、用户画像或外部记忆。"
        ),
    }
    user_message = {
        "role": "user",
        "content": f"""
请回答用户问题，并严格遵守：
- 只能基于“当前问题”作答，不要使用任何历史聊天背景、用户画像或外部记忆
- 不要只反问用户；必须先给出可执行的初步建议（至少3条）
- 建议要通用、清晰、可落地，避免空话
- 回答结构：
  1) 一句话判断框架（先做什么）
  2) 3~5条行动建议
  3) 一个简短收尾：说明如果补充背景，可进一步细化
- 不要输出 JSON

问题：{question}
""".strip(),
    }
    raw = await _call_dashscope([system_message, user_message])
    return _safe_trim(raw)


async def generate_memory_answer(question: str, memory: StructuredMemory) -> str:
    if not _has_memory(memory):
        return MEMORY_FALLBACK

    key_events = "；".join(memory.关键事件) if memory.关键事件 else "暂无"
    system_message = {
        "role": "system",
        "content": "你是一个理性且有分析能力的AI助手。必须结合用户背景给出有针对性的建议。",
    }
    user_message = {
        "role": "user",
        "content": f"""
你是一个理性且有分析能力的AI助手，请结合用户的历史情况回答问题。

【用户背景】
职业：{memory.职业 or "未知"}
目标：{memory.目标 or "未知"}
情绪：{memory.情绪 or "未知"}
风险倾向：{memory.风险倾向 or "未知"}
关键事件：{key_events}

【用户问题】
{question}

要求：
- 必须结合用户背景
- 给出更有针对性的建议
- 可以指出风险和机会
- 语气更像“了解用户的人”
- 必须明确引用至少2条背景信息（优先引用数字或具体事实）
- 输出中请先写“你当前的情况是：...”，再给建议
""".strip(),
    }
    raw = await _call_dashscope([system_message, user_message])
    return _safe_trim(raw)


async def memory_compare(chat_content: str, question: str) -> MemoryCompareEnvelope:
    normalized_chat = _safe_trim(chat_content)
    normalized_question = _safe_trim(question)
    if not normalized_chat:
        return MemoryCompareEnvelope(code=400, message="请先填写聊天记录。")
    if not normalized_question:
        return MemoryCompareEnvelope(code=400, message="请先填写用户问题。")

    try:
        memory = await extract_memory(normalized_chat)
        normal_answer = await generate_normal_answer(normalized_question)
        memory_answer = await generate_memory_answer(normalized_question, memory)
        return MemoryCompareEnvelope(
            code=0,
            data=MemoryCompareData(
                normal_answer=normal_answer,
                memory_answer=memory_answer,
                structured_memory=memory,
            ),
        )
    except httpx.TimeoutException:
        logger.exception("memory_compare timeout")
        return MemoryCompareEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("memory_compare error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return MemoryCompareEnvelope(code=504, message=user_msg.msg_timeout())
        return MemoryCompareEnvelope(code=500, message=user_msg.from_exception(err))
