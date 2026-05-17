from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import httpx

from app import user_messages as user_msg
from app.config import settings
from app.interest_explorer_prompt import build_interest_explorer_messages
from app.llm_json import parse_interest_explorer_model_output
from app.schemas import (
    InterestExplorerData,
    InterestExplorerEnvelope,
    InterestExplorerItem,
    InterestExplorerLazyFallback,
    InterestExplorerPersonality,
    InterestExplorerRequest,
    InterestExplorerWeekItem,
)

logger = logging.getLogger(__name__)

INTEREST_EXPLORER_MAX_TOKENS = 2200


async def _call_dashscope(messages: List[Dict[str, str]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": settings.dashscope_model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": 0.75,
            "max_tokens": INTEREST_EXPLORER_MAX_TOKENS,
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


def _normalize_interest_explorer_data(data: InterestExplorerData) -> InterestExplorerData:
    p = data.personality or InterestExplorerPersonality()
    if not (p.type_title or "").strip():
        p = p.model_copy(update={"type_title": "安静探索型"})
    if not (p.analysis or "").strip():
        p = p.model_copy(
            update={"analysis": "你更适合能自己掌控节奏、社交成本可控的兴趣。"}
        )
    if not (p.why_past_failed or "").strip():
        p = p.model_copy(
            update={
                "why_past_failed": "以前可能一上来就选了难度或社交成本太高的方向，还没建立习惯就放弃了。"
            }
        )

    interests = list(data.interests or [])
    while len(interests) < 5:
        interests.append(
            InterestExplorerItem(
                name=["阅读", "City Walk", "摄影", "羽毛球", "写作"][len(interests) % 5],
                why_fit="门槛低，适合先找回生活的节奏感。",
                difficulty=2,
                cost_level="低",
                social_level="低",
                long_term="适合长期坚持",
                best_time="周末或下班后",
                starter_tip="先体验 30 分钟，不办卡、不买装备。",
            )
        )
    normalized_interests: List[InterestExplorerItem] = []
    for it in interests[:5]:
        try:
            diff = int(it.difficulty)
        except (TypeError, ValueError):
            diff = 3
        normalized_interests.append(
            it.model_copy(
                update={
                    "difficulty": min(5, max(1, diff)),
                    "cost_level": it.cost_level if it.cost_level in ("低", "中", "高") else "低",
                    "social_level": it.social_level if it.social_level in ("低", "中", "高") else "低",
                }
            )
        )

    avoid = [str(x).strip() for x in (data.avoid or []) if str(x).strip()][:3]
    if len(avoid) < 2:
        avoid = (avoid + ["高强度社交型兴趣（目前精力可能撑不住）", "一上来就要大量装备的爱好"])[:3]

    week_plan = [w for w in (data.week_plan or []) if (w.day or w.activity)][:4]
    if len(week_plan) < 2:
        week_plan = [
            InterestExplorerWeekItem(day="周三", activity="选一项兴趣，低成本试 30 分钟"),
            InterestExplorerWeekItem(day="周末", activity="再试一项，对比感受哪个更舒服"),
        ]

    lazy = data.lazy_fallback or InterestExplorerLazyFallback()
    if not (lazy.description or "").strip():
        lazy = InterestExplorerLazyFallback(
            title=lazy.title or "最低门槛也算开始",
            description="不要逼自己一下改变人生。今晚出门散步 15 分钟，或者听一集播客，都算给生活留一点缝。",
        )

    return InterestExplorerData(
        personality=p,
        interests=normalized_interests,
        avoid=avoid,
        week_plan=week_plan,
        lazy_fallback=lazy,
    )


async def interest_explorer_recommend(body: InterestExplorerRequest) -> InterestExplorerEnvelope:
    if not (body.life_stage or "").strip():
        return InterestExplorerEnvelope(code=400, message="请选择当前阶段")
    if not (body.work_state or "").strip():
        return InterestExplorerEnvelope(code=400, message="请选择工作/学习状态")
    if not (body.social_style or "").strip():
        return InterestExplorerEnvelope(code=400, message="请选择社交倾向")
    if not body.preferences:
        return InterestExplorerEnvelope(code=400, message="请至少选一项「更喜欢」")
    if not (body.budget or "").strip():
        return InterestExplorerEnvelope(code=400, message="请选择预算")
    if not (body.weekend_state or "").strip():
        return InterestExplorerEnvelope(code=400, message="请选择周末一般状态")
    if not body.goals:
        return InterestExplorerEnvelope(code=400, message="请至少选一项「你最想获得什么」")

    form: Dict[str, Any] = {
        "life_stage": (body.life_stage or "").strip(),
        "work_state": (body.work_state or "").strip(),
        "social_style": (body.social_style or "").strip(),
        "preferences": list(body.preferences or []),
        "budget": (body.budget or "").strip(),
        "weekend_state": (body.weekend_state or "").strip(),
        "goals": list(body.goals or []),
        "extra_notes": (body.extra_notes or "").strip(),
    }

    messages = build_interest_explorer_messages(form)

    try:
        raw = await _call_dashscope(messages)
        data = _normalize_interest_explorer_data(parse_interest_explorer_model_output(raw))
        if not data.personality.type_title and not data.interests:
            return InterestExplorerEnvelope(code=500, message=user_msg.msg_model_empty())
        return InterestExplorerEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("interest_explorer timeout")
        return InterestExplorerEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("interest_explorer error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return InterestExplorerEnvelope(code=504, message=user_msg.msg_timeout())
        return InterestExplorerEnvelope(code=500, message=user_msg.from_exception(err))
