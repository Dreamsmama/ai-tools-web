"""
大模型输出常为「近似 JSON」：做清洗、宽松解析；仍失败则用原文做结构化兜底（不当作网络/服务错误）。
"""

from __future__ import annotations

import json
import logging
import re
from ast import literal_eval
from typing import Any, Dict, List, Optional

from app.schemas import (
    EveningLazyFallback,
    EveningPlanData,
    EveningPlanItem,
    InterestExplorerData,
    InterestExplorerItem,
    InterestExplorerLazyFallback,
    InterestExplorerPersonality,
    InterestExplorerWeekItem,
    OfferDecisionData,
    OfferOptionInsight,
    PrepareConsultData,
    SummaryData,
)

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


def dict_to_evening_plan_data(obj: Dict[str, Any]) -> EveningPlanData:
    def _list(key: str, limit: int) -> List[str]:
        raw = obj.get(key)
        return [str(x).strip() for x in raw if str(x).strip()][:limit] if isinstance(raw, list) else []

    plans_raw = obj.get("plans")
    plans: List[EveningPlanItem] = []
    if isinstance(plans_raw, list):
        for it in plans_raw:
            if not isinstance(it, dict):
                continue
            actions_raw = it.get("actions")
            actions = (
                [str(x).strip() for x in actions_raw if str(x).strip()]
                if isinstance(actions_raw, list)
                else []
            )
            fit_raw = it.get("fit_score", 3)
            try:
                fit_score = int(fit_raw)
            except (TypeError, ValueError):
                fit_score = 3
            plans.append(
                EveningPlanItem(
                    plan_type=str(it.get("plan_type") or "").strip(),
                    title=str(it.get("title") or "").strip(),
                    reason=str(it.get("reason") or "").strip(),
                    actions=actions[:5],
                    cost=str(it.get("cost") or "").strip(),
                    duration=str(it.get("duration") or "").strip(),
                    fit_score=fit_score,
                )
            )

    lazy_raw = obj.get("lazy_fallback")
    lazy = EveningLazyFallback()
    if isinstance(lazy_raw, dict):
        lazy = EveningLazyFallback(
            title=str(lazy_raw.get("title") or "").strip(),
            description=str(lazy_raw.get("description") or "").strip(),
        )

    return EveningPlanData(
        mode=str(obj.get("mode") or "").strip(),
        plans=plans[:3],
        avoid=_list("avoid", 3),
        lazy_fallback=lazy,
        tomorrow_tips=_list("tomorrow_tips", 2),
    )


def fallback_evening_plan_data(raw: str) -> EveningPlanData:
    text = (raw or "").strip()
    lines = lines_from_plain_text(text, max_lines=24)
    if not lines:
        lines = ["（未解析到模型正文，请重试）"]
    return EveningPlanData(
        mode=lines[0][:40] if lines else "低消耗恢复型",
        plans=[
            EveningPlanItem(
                plan_type="方案一：吃什么",
                title=lines[1] if len(lines) > 1 else "简单热食",
                reason=lines[2] if len(lines) > 2 else "先填饱肚子，别折腾。",
                actions=lines[3:5] or ["点一份外卖或下楼买热食"],
                cost="约 30-80 元",
                duration="约 30 分钟",
                fit_score=4,
            )
        ],
        avoid=lines[5:8] if len(lines) > 5 else ["别硬撑社交", "别熬太晚"],
        lazy_fallback=EveningLazyFallback(
            title="躺平也行",
            description=text[:300] if text else "今晚允许低电量模式。",
        ),
        tomorrow_tips=lines[8:10] if len(lines) > 8 else ["早点睡"],
    )


def parse_evening_plan_model_output(raw: str) -> EveningPlanData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_evening_plan_data(obj)
        if data.mode or data.plans:
            return data
    return fallback_evening_plan_data(raw)


def _norm_level(v: Any, default: str = "低") -> str:
    s = str(v or "").strip()
    if s in ("低", "中", "高"):
        return s
    low = s.lower()
    if low in ("low", "l"):
        return "低"
    if low in ("medium", "mid", "m", "中"):
        return "中"
    if low in ("high", "h"):
        return "高"
    return default


def dict_to_interest_explorer_data(obj: Dict[str, Any]) -> InterestExplorerData:
    def _list(key: str, limit: int) -> List[str]:
        raw = obj.get(key)
        return [str(x).strip() for x in raw if str(x).strip()][:limit] if isinstance(raw, list) else []

    personality_raw = obj.get("personality")
    personality = InterestExplorerPersonality()
    if isinstance(personality_raw, dict):
        personality = InterestExplorerPersonality(
            type_title=str(personality_raw.get("type_title") or "").strip(),
            analysis=str(personality_raw.get("analysis") or "").strip(),
            why_past_failed=str(personality_raw.get("why_past_failed") or "").strip(),
        )

    interests: List[InterestExplorerItem] = []
    interests_raw = obj.get("interests")
    if isinstance(interests_raw, list):
        for it in interests_raw:
            if not isinstance(it, dict):
                continue
            try:
                difficulty = int(it.get("difficulty", 3))
            except (TypeError, ValueError):
                difficulty = 3
            difficulty = min(5, max(1, difficulty))
            interests.append(
                InterestExplorerItem(
                    name=str(it.get("name") or "").strip(),
                    why_fit=str(it.get("why_fit") or "").strip(),
                    difficulty=difficulty,
                    cost_level=_norm_level(it.get("cost_level")),
                    social_level=_norm_level(it.get("social_level")),
                    long_term=str(it.get("long_term") or "").strip(),
                    best_time=str(it.get("best_time") or "").strip(),
                    starter_tip=str(it.get("starter_tip") or "").strip(),
                )
            )

    week_plan: List[InterestExplorerWeekItem] = []
    week_raw = obj.get("week_plan")
    if isinstance(week_raw, list):
        for it in week_raw:
            if not isinstance(it, dict):
                continue
            week_plan.append(
                InterestExplorerWeekItem(
                    day=str(it.get("day") or "").strip(),
                    activity=str(it.get("activity") or "").strip(),
                )
            )

    lazy_raw = obj.get("lazy_fallback")
    lazy = InterestExplorerLazyFallback()
    if isinstance(lazy_raw, dict):
        lazy = InterestExplorerLazyFallback(
            title=str(lazy_raw.get("title") or "").strip(),
            description=str(lazy_raw.get("description") or "").strip(),
        )

    return InterestExplorerData(
        personality=personality,
        interests=interests[:5],
        avoid=_list("avoid", 3),
        week_plan=week_plan[:4],
        lazy_fallback=lazy,
    )


def fallback_interest_explorer_data(raw: str) -> InterestExplorerData:
    text = (raw or "").strip()
    lines = lines_from_plain_text(text, max_lines=30)
    if not lines:
        lines = ["（未解析到模型正文，请重试）"]
    return InterestExplorerData(
        personality=InterestExplorerPersonality(
            type_title=lines[0][:30] if lines else "安静探索型",
            analysis=lines[1] if len(lines) > 1 else "你更适合低压力、能慢慢进入状态的兴趣。",
            why_past_failed=lines[2] if len(lines) > 2 else "以前可能选错了强度和社交成本。",
        ),
        interests=[
            InterestExplorerItem(
                name=lines[3] if len(lines) > 3 else "阅读",
                why_fit="门槛低，适合先找回节奏。",
                difficulty=2,
                cost_level="低",
                social_level="低",
                long_term="适合长期坚持",
                best_time="睡前或周末",
                starter_tip="从一本薄书或一篇短文开始，别定太高目标。",
            )
        ],
        avoid=lines[4:7] if len(lines) > 4 else ["高强度社交型俱乐部", "需要大量装备的极限运动"],
        week_plan=[
            InterestExplorerWeekItem(day="周末", activity="选一件最小的事试 30 分钟")
        ],
        lazy_fallback=InterestExplorerLazyFallback(
            title="今晚先别逼自己",
            description=text[:280] if text else "出门散步 15 分钟也算开始。",
        ),
    )


def parse_interest_explorer_model_output(raw: str) -> InterestExplorerData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_interest_explorer_data(obj)
        if data.personality.type_title or data.interests:
            return data
    return fallback_interest_explorer_data(raw)
