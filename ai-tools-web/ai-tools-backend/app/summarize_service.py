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
from app.schemas import SummaryData, SummaryEnvelope, SummaryTodo

logger = logging.getLogger(__name__)


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


def _parse_strict_json(content: str) -> SummaryData:
    obj: Dict[str, Any]
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as e1:
        logger.warning(
            "summary model JSON first parse failed: %s; snippet=%r",
            e1,
            (content or "")[:400],
        )
        s = content.find("{")
        e2 = content.rfind("}")
        if s >= 0 and e2 > s:
            try:
                obj = json.loads(content[s : e2 + 1])
            except json.JSONDecodeError as e2:
                logger.warning(
                    "summary model JSON brace-slice parse failed: %s",
                    e2,
                )
                raise ValueError("模型返回格式异常，请稍后重试") from None
        else:
            raise ValueError("模型返回格式异常，请稍后重试") from None

    summary_raw = obj.get("summary")
    todos_raw = obj.get("todos")
    risks_raw = obj.get("risks")
    reply_raw = obj.get("reply")

    summary = list(map(str, summary_raw)) if isinstance(summary_raw, list) else []
    todos_in = todos_raw if isinstance(todos_raw, list) else []
    risks = list(map(str, risks_raw)) if isinstance(risks_raw, list) else []
    reply = reply_raw if isinstance(reply_raw, str) else ""

    norm_todos: List[SummaryTodo] = []
    for t in todos_in:
        if isinstance(t, dict):
            owner = t.get("owner")
            task = t.get("task")
            due = t.get("due")
            item = SummaryTodo(
                owner=owner if isinstance(owner, str) else "未明确",
                task=task if isinstance(task, str) else str(t or ""),
                due=due if isinstance(due, str) else "",
            )
        else:
            item = SummaryTodo(owner="未明确", task=str(t or ""), due="")
        if item.task and item.task.strip():
            norm_todos.append(item)
    norm_todos = norm_todos[:6]

    data = SummaryData(
        summary=summary[:5],
        todos=norm_todos,
        risks=risks[:5],
        reply=reply.strip(),
    )
    return data


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
        return SummaryEnvelope(code=400, message="inputText 不能为空")

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
        data = _parse_strict_json(raw)

        if (
            not data.summary
            and not data.todos
            and not data.risks
            and not data.reply
        ):
            return SummaryEnvelope(code=500, message="模型输出为空/不符合格式")

        if data.reply and len(data.reply) > 400:
            data = data.model_copy(update={"reply": data.reply[:400]})

        return SummaryEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("dashscope timeout")
        return SummaryEnvelope(
            code=504, message="生成超时，请重试（网络或模型响应较慢）"
        )
    except json.JSONDecodeError as err:
        logger.warning("summarize unexpected JSONDecodeError: %s", err)
        return SummaryEnvelope(code=500, message="模型返回格式异常，请稍后重试")
    except Exception as err:
        logger.exception("summarize error")
        msg = str(err) if err else "server error"
        if "timeout" in msg.lower():
            return SummaryEnvelope(
                code=504, message="生成超时，请重试（网络或模型响应较慢）"
            )
        if isinstance(err, ValueError) and "模型返回格式异常" in msg:
            return SummaryEnvelope(code=500, message=msg)
        if isinstance(err, json.JSONDecodeError):
            return SummaryEnvelope(code=500, message="模型返回格式异常，请稍后重试")
        if "Expecting" in msg and "delimiter" in msg:
            return SummaryEnvelope(code=500, message="模型返回格式异常，请稍后重试")
        return SummaryEnvelope(code=500, message=msg)
