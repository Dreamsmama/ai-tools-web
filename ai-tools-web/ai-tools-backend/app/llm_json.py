"""
大模型输出常为「近似 JSON」：做清洗、宽松解析；仍失败则用原文做结构化兜底（不当作网络/服务错误）。
"""

from __future__ import annotations

import json
import logging
import re
from ast import literal_eval
from typing import Any, Dict, List, Optional

from app.schemas import OfferDecisionData, OfferOptionInsight, PrepareConsultData, SummaryData

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
    """模型有输出但非合法 JSON 时，用原文拆行为沟通理解结果，并给出可复制回复。"""
    text = (raw or "").strip()
    logger.info("summary: using plain-text fallback (model output was not valid JSON)")
    if not text:
        return SummaryData(
            intent=["（未解析到模型正文，请重试）"],
            emotion=[],
            strategy=[],
            reply="",
        )
    lines = lines_from_plain_text(text)
    if not lines:
        lines = [text[:500]]
    intent = lines[:3]
    emotion = lines[3:6] if len(lines) > 3 else []
    strategy = lines[6:10] if len(lines) > 6 else []
    reply = text[:400] if len(text) > 400 else text
    return SummaryData(intent=intent, emotion=emotion, strategy=strategy, reply=reply)


def dict_to_summary_data(obj: Dict[str, Any]) -> SummaryData:
    intent_raw = obj.get("intent")
    emotion_raw = obj.get("emotion")
    strategy_raw = obj.get("strategy")
    reply_raw = obj.get("reply")

    intent = list(map(str, intent_raw)) if isinstance(intent_raw, list) else []
    emotion = list(map(str, emotion_raw)) if isinstance(emotion_raw, list) else []
    strategy = list(map(str, strategy_raw)) if isinstance(strategy_raw, list) else []
    reply = reply_raw if isinstance(reply_raw, str) else ""

    return SummaryData(
        intent=intent[:4],
        emotion=emotion[:4],
        strategy=strategy[:5],
        reply=reply.strip(),
    )


def parse_summary_model_output(raw: str) -> SummaryData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_summary_data(obj)
        if data.intent or data.emotion or data.strategy or data.reply:
            return data
    return fallback_summary_data(raw)


def dict_to_offer_decision_data(obj: Dict[str, Any]) -> OfferDecisionData:
    def _list(key: str, limit: int) -> List[str]:
        raw = obj.get(key)
        return list(map(str, raw))[:limit] if isinstance(raw, list) else []

    options_raw = obj.get("option_insights")
    option_insights: List[OfferOptionInsight] = []
    if isinstance(options_raw, list):
        for it in options_raw:
            if not isinstance(it, dict):
                continue
            option_insights.append(
                OfferOptionInsight(
                    option_name=str(it.get("option_name") or "").strip(),
                    stability=str(it.get("stability") or "").strip(),
                    growth=str(it.get("growth") or "").strip(),
                    risk=str(it.get("risk") or "").strip(),
                    long_term_space=str(it.get("long_term_space") or "").strip(),
                    tech_value=str(it.get("tech_value") or "").strip(),
                    team_industry_factor=str(it.get("team_industry_factor") or "").strip(),
                )
            )

    # Backward compatibility for previous schema keys.
    core_conflict = _list("core_conflict", 4) or _list("true_concerns", 4)
    blind_spots = _list("blind_spots", 4) or _list("biggest_risks", 4)
    fit_by_choice = _list("fit_by_choice", 6)
    if not fit_by_choice:
        growth = _list("growth_first", 3)
        stability = _list("stability_first", 3)
        fit_by_choice = [f"偏成长：{x}" for x in growth] + [f"偏稳定：{x}" for x in stability]

    recommendation_raw = obj.get("recommendation")
    recommendation = recommendation_raw if isinstance(recommendation_raw, str) else ""
    return OfferDecisionData(
        core_conflict=core_conflict,
        option_insights=option_insights[:5],
        blind_spots=blind_spots,
        regret_after_3_months=_list("regret_after_3_months", 4),
        fit_by_choice=fit_by_choice[:6],
        questions_to_confirm=_list("questions_to_confirm", 6),
        recommendation=recommendation.strip()[:500],
    )


def fallback_offer_decision_data(raw: str) -> OfferDecisionData:
    text = (raw or "").strip()
    lines = lines_from_plain_text(text, max_lines=20)
    if not lines:
        lines = ["（未解析到模型正文，请重试）"]
    return OfferDecisionData(
        core_conflict=lines[:2],
        blind_spots=lines[2:4],
        regret_after_3_months=lines[4:6],
        fit_by_choice=lines[6:10],
        questions_to_confirm=lines[10:15],
        recommendation=text[:500] if text else "",
    )


def parse_offer_decision_model_output(raw: str) -> OfferDecisionData:
    obj = try_parse_json_object(raw)
    if obj is None:
        obj = _extract_offer_decision_like_object(raw)
    if obj is not None:
        data = dict_to_offer_decision_data(obj)
        if (
            data.core_conflict
            or data.option_insights
            or data.blind_spots
            or data.regret_after_3_months
            or data.fit_by_choice
            or data.questions_to_confirm
            or data.recommendation
        ):
            return data
    return fallback_offer_decision_data(raw)


def _parse_list_like_text(v: str) -> List[str]:
    text = (v or "").strip()
    if not text:
        return []
    # First try strict JSON.
    try:
        arr = json.loads(text)
        if isinstance(arr, list):
            return [str(x).strip() for x in arr if str(x).strip()]
    except Exception:
        pass
    # Then try Python-style list literals.
    try:
        arr2 = literal_eval(text)
        if isinstance(arr2, list):
            return [str(x).strip() for x in arr2 if str(x).strip()]
    except Exception:
        pass
    # Try extracting quoted list items from malformed JSON-like strings.
    quoted = re.findall(r'"([^"\n]+)"|\'([^\'\n]+)\'', text)
    quoted_items = [a or b for a, b in quoted if (a or b)]
    if quoted_items:
        return [s.strip() for s in quoted_items if s.strip()]
    # Finally split plain text.
    cleaned = re.sub(r'^[\[\(\{\"\']+|[\]\)\}\",\']+$', "", text).strip()
    return [x.strip() for x in re.split(r"[；;，,\n]+", cleaned) if x.strip()]


def _extract_offer_decision_like_object(raw: str) -> Optional[Dict[str, Any]]:
    text = strip_code_fences(raw or "")
    if not text:
        return None
    fields = [
        "core_conflict",
        "option_insights",
        "blind_spots",
        "regret_after_3_months",
        "fit_by_choice",
        "questions_to_confirm",
        "recommendation",
    ]
    out: Dict[str, Any] = {}
    for idx, key in enumerate(fields):
        next_part = "|".join(re.escape(k) for k in fields[idx + 1 :]) or r"\Z"
        # Capture JSON-like value after key: ; tolerant to quote style and colon variants.
        pattern = rf"[\"']?{re.escape(key)}[\"']?\s*[:：]\s*(.+?)(?=,\s*[\"']?(?:{next_part})[\"']?\s*[:：]|\n\s*[\"']?(?:{next_part})[\"']?\s*[:：]|\Z)"
        m = re.search(pattern, text, flags=re.S)
        if not m:
            continue
        raw_value = m.group(1).strip().rstrip(",")
        if key == "recommendation":
            if raw_value.startswith(("'", '"')) and raw_value.endswith(("'", '"')):
                raw_value = raw_value[1:-1]
            out[key] = raw_value.strip()
        elif key == "option_insights":
            parsed_options: Any = None
            for candidate in (raw_value, fix_trailing_commas(raw_value)):
                try:
                    parsed_options = json.loads(candidate)
                    break
                except Exception:
                    pass
                try:
                    parsed_options = literal_eval(candidate)
                    break
                except Exception:
                    pass
            out[key] = parsed_options if isinstance(parsed_options, list) else []
        else:
            out[key] = _parse_list_like_text(raw_value)
    return out if out else None


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
