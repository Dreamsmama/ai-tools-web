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
    LifeRpgChoice,
    LifeRpgData,
    LifeRpgMainQuest,
    LifeRpgReward,
    LifeRpgRouteData,
    LifeRpgSideQuest,
    LifeRpgTask,
    LifeRpgWorldState,
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
    依次尝试：去代码块 → json.loads → 平衡大括号提取 → 修尾逗号后再解析。
    成功返回 dict，失败返回 None。
    """
    candidates: List[str] = []
    t = strip_code_fences(raw)
    candidates.append(t)
    if t != raw.strip():
        candidates.append(raw.strip())

    best: Optional[Dict[str, Any]] = None
    best_score = -1

    def _life_rpg_top_level_score(obj: Dict[str, Any]) -> int:
        keys = set(obj.keys())
        score = 0
        for k in (
            "worldState",
            "world_state",
            "mainQuest",
            "main_quest",
            "routeContinuation",
            "route_continuation",
            "sideQuests",
            "side_quests",
        ):
            if k in keys:
                score += 10
        return score + min(len(keys), 5)

    def _consider(obj: Any) -> None:
        nonlocal best, best_score
        if not isinstance(obj, dict):
            return
        score = _life_rpg_top_level_score(obj)
        if score > best_score or (score == best_score and len(obj) > len(best or {})):
            best = obj
            best_score = score

    seen = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        for attempt in (c, fix_trailing_commas(c)):
            try:
                _consider(json.loads(attempt))
            except json.JSONDecodeError:
                pass
            for chunk in _iter_balanced_json_chunks(attempt):
                for ch in (chunk, fix_trailing_commas(chunk)):
                    try:
                        _consider(json.loads(ch))
                    except json.JSONDecodeError:
                        try:
                            obj = literal_eval(ch)
                            if isinstance(obj, dict):
                                _consider(obj)
                        except (SyntaxError, ValueError):
                            continue
    return best


def _iter_balanced_json_chunks(text: str) -> List[str]:
    """提取文本中所有平衡 {{}} 片段，优先长的。"""
    chunks: List[str] = []
    if not text:
        return chunks
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        depth = 0
        for j in range(i, len(text)):
            cj = text[j]
            if cj == "{":
                depth += 1
            elif cj == "}":
                depth -= 1
                if depth == 0:
                    chunks.append(text[i : j + 1])
                    break
    chunks.sort(key=len, reverse=True)
    return chunks


_JSON_KV_LINE = re.compile(
    r'^[\s"]*([A-Za-z_][\w]*)[\s"]*\s*:\s*(.+?)[\s,]*$',
    re.DOTALL,
)
_JSON_ARTIFACT = re.compile(r'^\s*"[\w]+"\s*:\s*[\{\[]?\s*$')


def _clean_life_rpg_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if _JSON_ARTIFACT.match(text):
        return ""
    m = _JSON_KV_LINE.match(text)
    if m:
        inner = m.group(2).strip().strip('"').strip("'").strip(",").strip()
        if inner.endswith("{") or inner.endswith("["):
            return ""
        return inner
    if text.startswith("{") or text.startswith("["):
        return ""
    return text


def _looks_like_json_artifact(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if t in ("原始输出模式", "主线（待解析）"):
        return True
    if _JSON_ARTIFACT.match(t):
        return True
    if re.search(r'"[\w]+"\s*:\s*', t) and len(t) < 120:
        return True
    return False


def _meaningful_plain_lines(text: str, max_lines: int = 20) -> List[str]:
    lines: List[str] = []
    for ln in lines_from_plain_text(text, max_lines=max_lines * 2):
        cleaned = _clean_life_rpg_text(ln)
        if cleaned and not _looks_like_json_artifact(cleaned):
            lines.append(cleaned)
        if len(lines) >= max_lines:
            break
    return lines


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


def _pick(obj: Dict[str, Any], *keys: str, default: Any = "") -> Any:
    for k in keys:
        if k in obj and obj[k] is not None:
            return obj[k]
    return default


def _reward_from_dict(raw: Any) -> LifeRpgReward:
    if not isinstance(raw, dict):
        return LifeRpgReward()

    def _n(key: str) -> int:
        try:
            return int(_pick(raw, key, default=0))
        except (TypeError, ValueError):
            return 0

    return LifeRpgReward(
        energy=_n("energy"),
        explore=_n("explore"),
        express=_n("express"),
        discipline=_n("discipline"),
        social=_n("social"),
        growth=_n("growth"),
    )


def _tasks_from_main_raw(main_raw: Dict[str, Any]) -> List[LifeRpgTask]:
    tasks_raw = _pick(main_raw, "tasks", default=[])
    tasks: List[LifeRpgTask] = []
    if isinstance(tasks_raw, list):
        for idx, it in enumerate(tasks_raw):
            if not isinstance(it, dict):
                continue
            tid = str(_pick(it, "id", default="")).strip() or f"task_{idx + 1}"
            tasks.append(
                LifeRpgTask(
                    id=tid,
                    title=_clean_life_rpg_text(_pick(it, "title", default="")),
                    action=_clean_life_rpg_text(_pick(it, "action", default="")),
                    estimated_time=_clean_life_rpg_text(
                        _pick(it, "estimatedTime", "estimated_time", default="")
                    ),
                    reward=_reward_from_dict(_pick(it, "reward", default={})),
                )
            )
    if tasks:
        return tasks

    actions_raw = _pick(main_raw, "actions", default=[])
    if isinstance(actions_raw, list):
        for idx, act in enumerate(actions_raw):
            text = _clean_life_rpg_text(act)
            if not text:
                continue
            tasks.append(
                LifeRpgTask(
                    id=f"task_{idx + 1}",
                    title=text[:24],
                    action=text,
                    estimated_time="约 10 分钟",
                    reward=LifeRpgReward(growth=1),
                )
            )
    return tasks


def _hoist_life_rpg_root(obj: Dict[str, Any]) -> Dict[str, Any]:
    """若误解析为内层 worldState 对象，提升为顶层结构。"""
    if not isinstance(obj, dict):
        return {}
    if any(
        k in obj
        for k in (
            "worldState",
            "world_state",
            "mainQuest",
            "main_quest",
            "routeContinuation",
            "route_continuation",
        )
    ):
        return obj
    if "title" in obj and "description" in obj and "tasks" not in obj:
        return {"worldState": obj}
    return obj


def dict_to_life_rpg_data(obj: Dict[str, Any]) -> LifeRpgData:
    obj = _hoist_life_rpg_root(obj)
    def _list(key: str, alt: str, limit: int) -> List[str]:
        raw = _pick(obj, key, alt, default=[])
        return [str(x).strip() for x in raw if str(x).strip()][:limit] if isinstance(raw, list) else []

    world_raw = _pick(obj, "worldState", "world_state", default={})
    world = LifeRpgWorldState()
    if isinstance(world_raw, dict):
        world = LifeRpgWorldState(
            title=_clean_life_rpg_text(_pick(world_raw, "title", default="")),
            description=_clean_life_rpg_text(_pick(world_raw, "description", default="")),
        )

    main_raw = _pick(obj, "mainQuest", "main_quest", default={})
    main = LifeRpgMainQuest()
    if isinstance(main_raw, dict):
        main = LifeRpgMainQuest(
            title=_clean_life_rpg_text(_pick(main_raw, "title", default="")),
            goal=_clean_life_rpg_text(_pick(main_raw, "goal", default="")),
            estimated_time=_clean_life_rpg_text(
                _pick(main_raw, "estimatedTime", "estimated_time", default="")
            ),
            tasks=_tasks_from_main_raw(main_raw),
        )

    side_quests: List[LifeRpgSideQuest] = []
    side_raw = _pick(obj, "sideQuests", "side_quests", default=[])
    if isinstance(side_raw, list):
        for idx, it in enumerate(side_raw):
            if not isinstance(it, dict):
                continue
            sid = str(_pick(it, "id", default="")).strip() or f"side_{idx + 1}"
            reward = _reward_from_dict(_pick(it, "reward", default={}))
            side_quests.append(
                LifeRpgSideQuest(
                    id=sid,
                    title=_clean_life_rpg_text(_pick(it, "title", default="")),
                    action=_clean_life_rpg_text(_pick(it, "action", default="")),
                    reward=reward,
                    reward_text=_clean_life_rpg_text(
                        _pick(it, "rewardText", "reward_text", default="")
                    ),
                )
            )

    def _parse_paths(raw_list: Any) -> List[LifeRpgChoice]:
        paths: List[LifeRpgChoice] = []
        if isinstance(raw_list, list):
            for it in raw_list:
                if not isinstance(it, dict):
                    continue
                paths.append(
                    LifeRpgChoice(
                        name=str(_pick(it, "name", default="")).strip(),
                        description=str(_pick(it, "description", default="")).strip(),
                        suggestion=str(_pick(it, "suggestion", default="")).strip(),
                    )
                )
        return paths

    optional_paths = _parse_paths(_pick(obj, "optionalPaths", "optional_paths", default=[]))
    choices = _parse_paths(_pick(obj, "choices", default=[]))
    if not optional_paths:
        optional_paths = choices

    return LifeRpgData(
        route_continuation=_clean_life_rpg_text(
            _pick(obj, "routeContinuation", "route_continuation", default="")
        ),
        role_title=_clean_life_rpg_text(_pick(obj, "roleTitle", "role_title", default="")),
        role_summary=_clean_life_rpg_text(_pick(obj, "roleSummary", "role_summary", default="")),
        world_state=world,
        main_quest=main,
        side_quests=side_quests[:4],
        choices=optional_paths[:3] if optional_paths else choices[:3],
        optional_paths=optional_paths[:3],
        not_recommend=_list("notRecommend", "not_recommend", 3),
        ending=str(_pick(obj, "ending", default="")).strip(),
    )


def dict_to_life_rpg_route_data(obj: Dict[str, Any]) -> LifeRpgRouteData:
    core_raw = _pick(obj, "coreAttributes", "core_attributes", default=[])
    core: List[str] = []
    if isinstance(core_raw, list):
        allowed = {"energy", "explore", "express", "discipline", "social", "growth"}
        core = [str(x).strip() for x in core_raw if str(x).strip() in allowed][:3]
    if not core:
        core = ["growth", "energy"]

    return LifeRpgRouteData(
        route_title=str(_pick(obj, "routeTitle", "route_title", default="")).strip(),
        route_summary=str(_pick(obj, "routeSummary", "route_summary", default="")).strip(),
        core_attributes=core,
        long_term_main_line=str(
            _pick(obj, "longTermMainLine", "long_term_main_line", default="")
        ).strip(),
        suggested_growth_style=str(
            _pick(obj, "suggestedGrowthStyle", "suggested_growth_style", default="")
        ).strip(),
        avoid_style=str(_pick(obj, "avoidStyle", "avoid_style", default="")).strip(),
    )


def parse_life_rpg_route_output(raw: str) -> LifeRpgRouteData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_life_rpg_route_data(obj)
        if data.route_title:
            return data
    return LifeRpgRouteData(
        route_title="成长探索者",
        route_summary=(raw or "")[:200] or "你正在走出一条属于自己的成长路线。",
        core_attributes=["growth", "energy"],
        long_term_main_line="每天推进一小步",
        suggested_growth_style="轻量、可完成的小任务",
        avoid_style="一次性硬撑大图景",
    )


def is_life_rpg_parse_degraded(data: LifeRpgData) -> bool:
    world = data.world_state or LifeRpgWorldState()
    if _looks_like_json_artifact(world.title) or _looks_like_json_artifact(world.description):
        return True
    main = data.main_quest or LifeRpgMainQuest()
    if _looks_like_json_artifact(main.title) or _looks_like_json_artifact(main.goal):
        return True
    tasks = main.tasks or []
    if not tasks:
        return True
    valid = [t for t in tasks if not _looks_like_json_artifact(t.action) and (t.action or "").strip()]
    return len(valid) < 2


def build_life_rpg_context_fallback(ctx: Dict[str, Any], raw: str = "") -> LifeRpgData:
    """模型 JSON 解析失败时，用用户今日状态生成可读的默认安排。"""
    profile = ctx.get("profile") or {}
    energy = (ctx.get("energy_level") or "一般").strip()
    mode = (ctx.get("daily_mode") or "正常推进").strip()
    go_out = (ctx.get("go_out") or "").strip()
    custom = (ctx.get("custom_tasks") or "").strip()
    route_name = (
        profile.get("routeTitle") or profile.get("route_title") or "你的成长路线"
    ).strip()

    if mode == "今天只想恢复" or energy == "很累":
        state_title = "低消耗恢复"
        state_desc = "今天更适合慢下来，完成小事即可，不必硬撑。"
    elif mode == "想挑战一点":
        state_title = "轻挑战推进"
        state_desc = "今天可以比平时多迈一小步，但仍保持可完成。"
    else:
        state_title = "正常推进"
        state_desc = "按你的长期路线，今天适合稳定、具体地推进。"

    if go_out == "不想出门":
        state_desc += " 优先室内或原地可完成的事。"

    tasks: List[LifeRpgTask] = []
    if custom:
        tasks.append(
            LifeRpgTask(
                id="task_1",
                title=custom[:20],
                action=custom,
                estimated_time="约 15 分钟",
                reward=LifeRpgReward(growth=1),
            )
        )
    defaults = [
        ("整理一件小事", "收拾桌面、洗碗或整理背包中的一样", "约 10 分钟"),
        ("推进 10 分钟", "阅读、学习或复盘一件与路线相关的小事", "约 10 分钟"),
        ("照顾状态", "散步、拉伸、早睡准备或喝杯水", "约 10 分钟"),
    ]
    for i, (title, action, est) in enumerate(defaults):
        if len(tasks) >= 3:
            break
        tasks.append(
            LifeRpgTask(
                id=f"task_{len(tasks) + 1}",
                title=title,
                action=action,
                estimated_time=est,
                reward=LifeRpgReward(growth=1),
            )
        )

    snippet = (raw or "")[:400].strip()
    return LifeRpgData(
        route_continuation=f"今天继续在「{route_name}」上轻量推进。",
        world_state=LifeRpgWorldState(title=state_title, description=state_desc),
        main_quest=LifeRpgMainQuest(
            title="今日主线",
            goal="完成下面几件具体小事，就算今天的推进。",
            estimated_time="约 20–30 分钟",
            tasks=tasks[:3],
        ),
        side_quests=[
            LifeRpgSideQuest(
                id="side_1",
                title="随手小事",
                action="做一件 5 分钟内能完成的事，例如整理或走动",
                reward=LifeRpgReward(energy=1),
                reward_text="精力 +1",
            ),
            LifeRpgSideQuest(
                id="side_2",
                title="留白",
                action="留 10 分钟不安排事，让大脑缓一缓",
                reward=LifeRpgReward(energy=1),
                reward_text="精力 +1",
            ),
        ],
        not_recommend=["不要为「变强」硬撑到透支", "不要用刷手机代替真正休息"],
        ending="今天完成一件小事就算推进，按你的节奏来。",
        role_summary=snippet,
    )


def fallback_life_rpg_data(raw: str) -> LifeRpgData:
    """无上下文时的最简兜底（优先使用 build_life_rpg_context_fallback）。"""
    return build_life_rpg_context_fallback({}, raw)


def parse_life_rpg_model_output(raw: str) -> LifeRpgData:
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_life_rpg_data(obj)
        if not is_life_rpg_parse_degraded(data):
            return data
        logger.info("life_rpg: parsed JSON but fields look degraded, will try fallback")
    return fallback_life_rpg_data(raw)


def parse_life_rpg_daily_output(raw: str, ctx: Dict[str, Any]) -> LifeRpgData:
    """解析每日安排；失败或字段异常时用用户状态生成结构化兜底。"""
    obj = try_parse_json_object(raw)
    if obj is not None:
        data = dict_to_life_rpg_data(obj)
        if not is_life_rpg_parse_degraded(data):
            return data
        logger.warning("life_rpg daily: degraded parse, using context fallback")
    return build_life_rpg_context_fallback(ctx, raw)
