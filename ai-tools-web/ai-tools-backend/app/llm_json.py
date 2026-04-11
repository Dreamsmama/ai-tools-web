"""
大模型输出常为「近似 JSON」：做清洗、宽松解析；仍失败则用原文做结构化兜底（不当作网络/服务错误）。
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.schemas import PrepareConsultData, SummaryData, SummaryTodo

logger = logging.getLogger(__name__)

_CODE_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_TRAILING_COMMA = re.compile(r",(\s*[}\]])")


def strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    m = _CODE_FENCE.search(t)
    if m:
        return m.group(1).strip()
    return t


def fix_trailing_commas(s: str) -> str:
    """去掉 JSON 里非法的尾逗号，可多轮收敛。"""
    prev = None
    cur = s
    while prev != cur:
        prev = cur
        cur = _TRAILING_COMMA.sub(r"\1", cur)
    return cur


def try_parse_json_object(raw: str) -> Optional[Dict[str, Any]]:
    """
    依次尝试：去代码块 → json.loads → 首尾大括号切片 → 修尾逗号后再解析。
    成功返回 dict，失败返回 None。
    """
    candidates: List[str] = []
    t = strip_code_fences(raw)
    candidates.append(t)
    if t != raw.strip():
        candidates.append(raw.strip())

    seen = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        for attempt in (c, fix_trailing_commas(c)):
            try:
                obj = json.loads(attempt)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                pass
            s = attempt.find("{")
            e2 = attempt.rfind("}")
            if s >= 0 and e2 > s:
                chunk = attempt[s : e2 + 1]
                for ch in (chunk, fix_trailing_commas(chunk)):
                    try:
                        obj = json.loads(ch)
                        if isinstance(obj, dict):
                            return obj
                    except json.JSONDecodeError:
                        continue
    return None


def lines_from_plain_text(text: str, max_lines: int = 20) -> List[str]:
    lines: List[str] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        ln = re.sub(r"^\s*(?:[•\-*＊]|\d+[\.、．])\s*", "", ln).strip()
        if ln:
            lines.append(ln[:800])
        if len(lines) >= max_lines:
            break
    return lines


def fallback_summary_data(raw: str) -> SummaryData:
    """模型有输出但非合法 JSON 时，用原文拆行作为要点，并给出可复制的回复段。"""
    text = (raw or "").strip()
    logger.info("summary: using plain-text fallback (model output was not valid JSON)")
    if not text:
        return SummaryData(
            summary=["（未解析到模型正文，请重试）"],
            todos=[],
            risks=[],
            reply="",
        )
    lines = lines_from_plain_text(text)
    if not lines:
        lines = [text[:500]]
    summary = lines[:5]
    reply = text[:400] if len(text) > 400 else text
    return SummaryData(summary=summary, todos=[], risks=[], reply=reply)


def dict_to_summary_data(obj: Dict[str, Any]) -> SummaryData:
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

    return SummaryData(
        summary=summary[:5],
        todos=norm_todos,
        risks=risks[:5],
        reply=reply.strip(),
    )


def parse_summary_model_output(raw: str) -> SummaryData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_summary_data(obj)
        if data.summary or data.todos or data.risks or data.reply:
            return data
    return fallback_summary_data(raw)


def dict_to_prepare_data(obj: Dict[str, Any]) -> PrepareConsultData:
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


def fallback_prepare_data(raw: str) -> PrepareConsultData:
    text = (raw or "").strip()
    logger.info("prepare_consult: using plain-text fallback (model output was not valid JSON)")
    if not text:
        return PrepareConsultData(
            summary=["（未解析到模型正文，请重试）"],
            questions=["请向医生说明当前主要不适与持续时间。"],
            notes=["请携带既往检查资料（如有）。"],
        )
    lines = lines_from_plain_text(text)
    if len(lines) >= 3:
        summary = lines[:3]
    elif lines:
        summary = (lines + [lines[-1]] * 3)[:3]
    else:
        summary = [text[:400]]
        if len(text) > 400:
            summary.append(text[400:800])
        if len(text) > 800:
            summary.append(text[800:1200])
        summary = [s for s in summary if s][:3]
    questions = [
        "根据我描述的情况，需要做哪些检查或随访？",
        "日常生活中有哪些需要注意或观察的事项？",
        "什么情况需要尽快复诊或急诊？",
    ]
    notes = [
        "以下为模型原文整理（未解析为 JSON 结构），仅供参考。",
        "请以医生面诊意见为准。",
    ]
    return PrepareConsultData(
        summary=summary[:3],
        questions=questions[:3],
        notes=notes[:2],
    )


def parse_prepare_model_output(raw: str) -> PrepareConsultData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_prepare_data(obj)
        if data.summary or data.questions or data.notes:
            return data
    return fallback_prepare_data(raw)
