from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from app.llm.dashscope_client import call_dashscope
from app.utils import user_messages as user_msg
from app.prompts.life_rpg_daily_prompt import build_life_rpg_daily_messages
from app.prompts.life_rpg_route_prompt import build_life_rpg_route_messages
from app.utils.llm_json import (
    is_life_rpg_parse_degraded,
    parse_life_rpg_daily_output,
    parse_life_rpg_route_output,
)
from app.schemas import (
    LifeRpgCreateRouteRequest,
    LifeRpgDailyRequest,
    LifeRpgData,
    LifeRpgEnvelope,
    LifeRpgMainQuest,
    LifeRpgReward,
    LifeRpgRouteData,
    LifeRpgRouteEnvelope,
    LifeRpgSideQuest,
    LifeRpgTask,
    LifeRpgWorldState,
)

logger = logging.getLogger(__name__)

LIFE_RPG_ROUTE_MAX_TOKENS = 1200
LIFE_RPG_DAILY_MAX_TOKENS = 2400

def _clamp_reward(reward: LifeRpgReward) -> LifeRpgReward:
    def _n(v: Any) -> int:
        try:
            n = int(v)
        except (TypeError, ValueError):
            n = 0
        return min(3, max(0, n))

    return LifeRpgReward(
        energy=_n(reward.energy),
        explore=_n(reward.explore),
        express=_n(reward.express),
        discipline=_n(reward.discipline),
        social=_n(reward.social),
        growth=_n(reward.growth),
    )


def _normalize_tasks(main: LifeRpgMainQuest) -> List[LifeRpgTask]:
    tasks = list(main.tasks or [])
    if tasks:
        normalized: List[LifeRpgTask] = []
        for idx, t in enumerate(tasks[:4]):
            tid = (t.id or "").strip() or f"task_{idx + 1}"
            normalized.append(
                LifeRpgTask(
                    id=tid,
                    title=(t.title or f"子任务 {idx + 1}").strip(),
                    action=(t.action or "").strip() or "完成一件今天能做的小事",
                    estimated_time=(t.estimated_time or "").strip() or "约 10 分钟",
                    reward=_clamp_reward(t.reward or LifeRpgReward(growth=1)),
                )
            )
        while len(normalized) < 3:
            i = len(normalized)
            normalized.append(
                LifeRpgTask(
                    id=f"task_{i + 1}",
                    title=f"轻量行动 {i + 1}",
                    action="选一件最小的事做完",
                    estimated_time="约 10 分钟",
                    reward=LifeRpgReward(growth=1),
                )
            )
        return normalized[:3]

    return [
        LifeRpgTask(
            id="task_1",
            title="最小行动",
            action="完成一件今天能做的小事",
            estimated_time="约 10 分钟",
            reward=LifeRpgReward(growth=1),
        ),
        LifeRpgTask(
            id="task_2",
            title="记录进展",
            action="用一句话记下今天推进了什么",
            estimated_time="约 5 分钟",
            reward=LifeRpgReward(discipline=1),
        ),
        LifeRpgTask(
            id="task_3",
            title="收尾",
            action="整理桌面或准备明天要带的东西",
            estimated_time="约 10 分钟",
            reward=LifeRpgReward(energy=1),
        ),
    ]


def _normalize_side_quests(side_quests: List[LifeRpgSideQuest]) -> List[LifeRpgSideQuest]:
    side: List[LifeRpgSideQuest] = []
    for idx, sq in enumerate((side_quests or [])[:4]):
        if not (sq.title or sq.action or "").strip():
            continue
        sid = (sq.id or "").strip() or f"side_{idx + 1}"
        reward = _clamp_reward(sq.reward or LifeRpgReward())
        if not any(
            [
                reward.energy,
                reward.explore,
                reward.express,
                reward.discipline,
                reward.social,
                reward.growth,
            ]
        ):
            reward = LifeRpgReward(growth=1)
        side.append(
            LifeRpgSideQuest(
                id=sid,
                title=(sq.title or "支线").strip(),
                action=(sq.action or "").strip() or "按你的节奏完成一小步",
                reward=reward,
                reward_text=(sq.reward_text or "").strip() or "完成可得成长感",
            )
        )
    while len(side) < 2:
        i = len(side)
        side.append(
            LifeRpgSideQuest(
                id=f"side_{i + 1}",
                title="随手支线",
                action="整理桌面 5 分钟或喝一杯水",
                reward=LifeRpgReward(energy=1),
                reward_text="精力 +1",
            )
        )
    return side[:3]


def _normalize_life_rpg_data(data: LifeRpgData) -> LifeRpgData:
    main = data.main_quest or LifeRpgMainQuest()
    tasks = _normalize_tasks(main)

    not_rec = [str(x).strip() for x in (data.not_recommend or []) if str(x).strip()][:3]
    if len(not_rec) < 2:
        not_rec = (not_rec + ["别为「变强」硬撑到透支", "别用刷手机代替真正休息"])[:3]

    world = data.world_state or LifeRpgWorldState()
    if not (world.title or "").strip():
        world = LifeRpgWorldState(
            title="正常推进模式",
            description="按你的路线与今日状态，完成可执行的小步即可推进。",
        )
    if not (world.description or "").strip():
        world = LifeRpgWorldState(
            title=world.title,
            description="今天适合按你的节奏推进，不必硬撑。",
        )

    continuation = (data.route_continuation or "").strip()
    if not continuation:
        continuation = "今天继续在你的人生路线上推进一小步。"

    return LifeRpgData(
        route_continuation=continuation,
        role_title=(data.role_title or "").strip(),
        role_summary=(data.role_summary or "").strip(),
        world_state=world,
        main_quest=LifeRpgMainQuest(
            title=(main.title or "").strip() or "今日主线",
            goal=(main.goal or "").strip() or "完成具体小事，推进长期路线。",
            estimated_time=(main.estimated_time or "").strip() or "约 20-30 分钟",
            tasks=tasks,
        ),
        side_quests=_normalize_side_quests(data.side_quests or []),
        choices=[],
        optional_paths=[],
        not_recommend=not_rec,
        ending=(data.ending or "").strip() or "今日副本已就绪，完成一项就算推进。",
    )


def _normalize_route_data(data: LifeRpgRouteData) -> LifeRpgRouteData:
    core = [c for c in (data.core_attributes or []) if c][:3]
    if not core:
        core = ["growth", "energy"]
    return LifeRpgRouteData(
        route_title=(data.route_title or "").strip() or "成长探索者",
        route_summary=(data.route_summary or "").strip()
        or "你正在塑造一条可持续的人生成长路线。",
        core_attributes=core,
        long_term_main_line=(data.long_term_main_line or "").strip() or "每天推进一小步",
        suggested_growth_style=(data.suggested_growth_style or "").strip()
        or "用轻量、可完成的任务积累成长感",
        avoid_style=(data.avoid_style or "").strip() or "避免一次性硬撑大图景",
    )


async def life_rpg_create_route(body: LifeRpgCreateRouteRequest) -> LifeRpgRouteEnvelope:
    states = [s.strip() for s in (body.life_states or []) if (s or "").strip()]
    if not states:
        target = (body.target_person or "").strip()
        if target and target != "自定义":
            states = [target]
        elif (body.custom_target_person or body.custom_life_state or "").strip():
            states = [(body.custom_target_person or body.custom_life_state or "").strip()]
    if not states:
        return LifeRpgRouteEnvelope(code=400, message="请至少选择一项人生状态")
    if not (body.direction_template or "").strip() and not body.long_term_directions:
        return LifeRpgRouteEnvelope(code=400, message="请选择人生方向模板")
    keywords = [k.strip() for k in (body.life_keywords or []) if (k or "").strip()]
    if not keywords and not (body.custom_long_term_goals or "").strip():
        return LifeRpgRouteEnvelope(code=400, message="请至少添加一个人生关键词")

    identity_type = (body.identity_type or "").strip() or "暂不填写"

    form: Dict[str, Any] = {
        "life_states": states,
        "custom_life_state": (body.custom_life_state or body.custom_target_person or "").strip(),
        "direction_template": (body.direction_template or "").strip(),
        "life_keywords": keywords,
        "target_person": states[0] if states else (body.target_person or "").strip(),
        "custom_target_person": (body.custom_target_person or body.custom_life_state or "").strip(),
        "long_term_directions": list(body.long_term_directions or []),
        "custom_long_term_goals": (body.custom_long_term_goals or "").strip(),
        "identity_type": identity_type,
        "occupation": (body.occupation or "").strip(),
        "identity": (body.identity or "").strip(),
        "status_notes": (body.status_notes or "").strip(),
    }

    messages = build_life_rpg_route_messages(form)

    try:
        raw = await call_dashscope(
            messages,
            temperature=0.7,
            max_tokens=LIFE_RPG_ROUTE_MAX_TOKENS,
        )
        data = _normalize_route_data(parse_life_rpg_route_output(raw))
        if not data.route_title:
            return LifeRpgRouteEnvelope(code=500, message=user_msg.msg_model_empty())
        return LifeRpgRouteEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("life_rpg_create_route timeout")
        return LifeRpgRouteEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("life_rpg_create_route error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return LifeRpgRouteEnvelope(code=504, message=user_msg.msg_timeout())
        return LifeRpgRouteEnvelope(code=500, message=user_msg.from_exception(err))


async def life_rpg_daily_generate(body: LifeRpgDailyRequest) -> LifeRpgEnvelope:
    profile = body.profile or {}
    if not (profile.get("routeTitle") or profile.get("route_title")):
        return LifeRpgEnvelope(code=400, message="请先创建人生路线")

    if not (body.energy_level or "").strip():
        return LifeRpgEnvelope(code=400, message="请选择今天状态")
    if not (body.daily_mode or "").strip():
        return LifeRpgEnvelope(code=400, message="请选择今天模式")
    if not (body.go_out or "").strip():
        return LifeRpgEnvelope(code=400, message="请选择今天是否想出门")

    ctx: Dict[str, Any] = {
        "profile": profile,
        "attributes": body.attributes or {},
        "last_result": body.last_result,
        "completed_task_ids": list(body.completed_task_ids or []),
        "energy_level": (body.energy_level or "").strip(),
        "daily_mode": (body.daily_mode or "").strip(),
        "go_out": (body.go_out or "").strip(),
        "custom_tasks": (body.custom_tasks or "").strip(),
    }

    messages = build_life_rpg_daily_messages(ctx)

    try:
        raw = await call_dashscope(
            messages,
            temperature=0.75,
            max_tokens=LIFE_RPG_DAILY_MAX_TOKENS,
        )
        data = _normalize_life_rpg_data(parse_life_rpg_daily_output(raw, ctx))
        if not data.main_quest.title or is_life_rpg_parse_degraded(data):
            return LifeRpgEnvelope(code=500, message=user_msg.msg_model_empty())
        return LifeRpgEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("life_rpg_daily timeout")
        return LifeRpgEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("life_rpg_daily error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return LifeRpgEnvelope(code=504, message=user_msg.msg_timeout())
        return LifeRpgEnvelope(code=500, message=user_msg.from_exception(err))
