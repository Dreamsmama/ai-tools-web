from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import httpx

from app import user_messages as user_msg
from app.config import settings
from app.evening_plan_prompt import build_evening_plan_messages
from app.llm_json import parse_evening_plan_model_output
from app.schemas import (
    EveningLazyFallback,
    EveningPlanData,
    EveningPlanEnvelope,
    EveningPlanItem,
    EveningPlanRequest,
)

logger = logging.getLogger(__name__)

EVENING_PLAN_MAX_TOKENS = 1800


async def _call_dashscope(messages: List[Dict[str, str]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": settings.dashscope_model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": 0.7,
            "max_tokens": EVENING_PLAN_MAX_TOKENS,
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


def _normalize_evening_plan_data(data: EveningPlanData) -> EveningPlanData:
    plans = data.plans or []
    default_types = ["方案一：吃什么", "方案二：做什么", "方案三：回家后怎么收尾"]
    normalized_plans: List[EveningPlanItem] = []
    for idx, plan in enumerate(plans[:3]):
        fit = plan.fit_score
        try:
            fit = int(fit)
        except (TypeError, ValueError):
            fit = 3
        fit = min(5, max(1, fit))
        actions = [str(a).strip() for a in (plan.actions or []) if str(a).strip()][:5]
        normalized_plans.append(
            EveningPlanItem(
                plan_type=(plan.plan_type or default_types[idx]).strip(),
                title=(plan.title or "").strip(),
                reason=(plan.reason or "").strip(),
                actions=actions,
                cost=(plan.cost or "").strip(),
                duration=(plan.duration or "").strip(),
                fit_score=fit,
            )
        )
    while len(normalized_plans) < 3:
        idx = len(normalized_plans)
        normalized_plans.append(
            EveningPlanItem(
                plan_type=default_types[idx],
                title="按你的节奏来就好",
                reason="今晚先照顾好自己的状态。",
                actions=["选一件最小的事做完就收工"],
                cost="约 0-50 元",
                duration="约 30 分钟",
                fit_score=3,
            )
        )

    avoid = [str(x).strip() for x in (data.avoid or []) if str(x).strip()][:3]
    if len(avoid) < 2:
        avoid = (avoid + ["别为了「不辜负晚上」硬撑到很晚", "别在很累时还刷手机熬到更累"])[:3]

    lazy = data.lazy_fallback or EveningLazyFallback()
    if not (lazy.description or "").strip():
        lazy = EveningLazyFallback(
            title=lazy.title or "今晚允许自己低电量",
            description="洗个热水澡，点一份简单外卖或热饮，看一集短剧就关灯。这不叫浪费晚上，是在充电。",
        )

    tips = [str(x).strip() for x in (data.tomorrow_tips or []) if str(x).strip()][:2]
    if not tips:
        tips = ["尽量在固定时间躺下，睡前 30 分钟少刷刺激内容", "明早留 10 分钟吃早餐，别空腹硬扛"]

    mode = (data.mode or "").strip() or "低消耗恢复型"
    return EveningPlanData(
        mode=mode,
        plans=normalized_plans,
        avoid=avoid,
        lazy_fallback=lazy,
        tomorrow_tips=tips,
    )


async def evening_plan_recommend(body: EveningPlanRequest) -> EveningPlanEnvelope:
    city = (body.city or "").strip()
    if not city:
        return EveningPlanEnvelope(code=400, message="请填写当前城市")
    if not body.interests:
        return EveningPlanEnvelope(code=400, message="请至少选择一项「今天更想做什么」")

    form: Dict[str, Any] = {
        "city": city,
        "current_time": (body.current_time or "").strip(),
        "energy_level": (body.energy_level or "").strip(),
        "mood": (body.mood or "").strip(),
        "go_out": (body.go_out or "").strip(),
        "social": (body.social or "").strip(),
        "budget": (body.budget or "").strip(),
        "interests": list(body.interests or []),
        "extra_notes": (body.extra_notes or "").strip(),
    }

    messages = build_evening_plan_messages(form)

    try:
        raw = await _call_dashscope(messages)
        data = _normalize_evening_plan_data(parse_evening_plan_model_output(raw))
        if not data.mode and not data.plans:
            return EveningPlanEnvelope(code=500, message=user_msg.msg_model_empty())
        return EveningPlanEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("evening_plan timeout")
        return EveningPlanEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("evening_plan error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return EveningPlanEnvelope(code=504, message=user_msg.msg_timeout())
        return EveningPlanEnvelope(code=500, message=user_msg.from_exception(err))
