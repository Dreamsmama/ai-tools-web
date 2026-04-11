"""
就医前问诊准备，逻辑对齐 miniprogram-2/cloudfunctions/prepareConsult/index.js。
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import httpx

from app.config import settings
from app.schemas import PrepareConsultData, PrepareConsultEnvelope

logger = logging.getLogger(__name__)


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


def _parse_strict_json(content: str) -> PrepareConsultData:
    obj: Dict[str, Any]
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        s = content.find("{")
        e2 = content.rfind("}")
        if s >= 0 and e2 > s:
            obj = json.loads(content[s : e2 + 1])
        else:
            raise ValueError("模型返回非JSON") from None

    summary_raw = obj.get("summary")
    questions_raw = obj.get("questions")
    notes_raw = obj.get("notes")

    summary = list(map(str, summary_raw)) if isinstance(summary_raw, list) else []
    questions = list(map(str, questions_raw)) if isinstance(questions_raw, list) else []
    notes = list(map(str, notes_raw)) if isinstance(notes_raw, list) else []

    return PrepareConsultData(
        summary=summary[:3],
        questions=questions[:3],
        notes=notes[:2],
    )


async def _call_dashscope_prepare(messages: List[Dict[str, str]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": settings.dashscope_model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": settings.dashscope_temperature,
            "max_tokens": settings.dashscope_prepare_max_tokens,
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(settings.dashscope_prepare_timeout_seconds)

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


async def prepare_consult(symptom: str, report: str, target: str) -> PrepareConsultEnvelope:
    symptom = _safe_trim(symptom)
    report = _safe_trim(report)
    target = _safe_trim(target)

    if not symptom:
        return PrepareConsultEnvelope(code=400, message="symptom 不能为空")

    system_message = {
        "role": "system",
        "content": (
            "你是“就医前问诊准备助手”。严格禁止：诊断、治疗/用药建议、判断严重程度。"
            "只做：信息整理、提问准备、注意点提醒（中性）。"
            "只输出严格 JSON，不要 markdown，不要多余文本。"
        ),
    }
    user_message = {
        "role": "user",
        "content": f"""
症状：{symptom or "无"}
检查/报告：{report or "无"}
关注点：{target or "无"}

只返回 JSON（不要markdown、不要多余文本）：
{{"summary":["...","...","..."],"questions":["...","...","..."],"notes":["...","..."]}}

规则：
- summary：3条，事实性整理/复述
- questions：3条，必须是“问医生的问题句”
- notes：2条，中性提醒，不含诊断/治疗建议
""".strip(),
    }

    try:
        raw = await _call_dashscope_prepare([system_message, user_message])
        data = _parse_strict_json(raw)

        if not data.summary and not data.questions and not data.notes:
            return PrepareConsultEnvelope(code=500, message="模型输出为空/不符合格式")

        return PrepareConsultEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("prepare_consult dashscope timeout")
        return PrepareConsultEnvelope(
            code=504, message="生成超时，请重试（网络或模型响应较慢）"
        )
    except Exception as err:
        logger.exception("prepare_consult error")
        msg = str(err) if err else "server error"
        if "timeout" in msg.lower():
            return PrepareConsultEnvelope(
                code=504, message="生成超时，请重试（网络或模型响应较慢）"
            )
        return PrepareConsultEnvelope(code=500, message=msg)
