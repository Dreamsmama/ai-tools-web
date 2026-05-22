"""AI 人生副本 — 每日副本 Prompt（GM 推进路线）。"""

from __future__ import annotations

import json
from typing import Any, Dict, List


def build_life_rpg_daily_messages(ctx: Dict[str, Any]) -> List[Dict[str, str]]:
    profile = ctx.get("profile") or {}
    attributes = ctx.get("attributes") or {}
    last_result = ctx.get("last_result") or {}
    completed_ids = ctx.get("completed_task_ids") or []

    today_snapshot = {
        "今天状态": ctx.get("energy_level") or "",
        "今天模式": ctx.get("daily_mode") or "",
        "是否想出门": ctx.get("go_out") or "",
        "今日自定义任务": (ctx.get("custom_tasks") or "").strip() or "无",
    }

    route_snapshot = {
        "路线名称": profile.get("routeTitle") or profile.get("route_title") or "",
        "路线说明": profile.get("routeSummary") or profile.get("route_summary") or "",
        "想成为的人": profile.get("targetPerson") or profile.get("target_person") or "",
        "长期方向": profile.get("longTermDirections") or profile.get("long_term_directions") or [],
        "长期目标": profile.get("customLongTermGoals") or profile.get("custom_long_term_goals") or "",
        "长期主线": profile.get("longTermMainLine") or profile.get("long_term_main_line") or "",
        "核心属性": profile.get("coreAttributes") or profile.get("core_attributes") or [],
        "人生阶段身份": profile.get("identityType")
        or profile.get("identity_type")
        or "未填写",
        "具体职业": profile.get("occupation") or "未填写",
    }

    history_snapshot = {
        "当前属性": attributes,
        "最近副本主线": (last_result.get("main_quest") or {}).get("title") if last_result else "",
        "最近已完成任务ID": completed_ids,
    }

    system_content = (
        "你是今日路线陪伴助手，不是表单推荐器。"
        "用户已在生成前填写今日状态（精力、模式、是否出门、可选事项），"
        "你须根据长期人生路线与今日状态，自动判断「今日状态模式」，不要让用户在结果页再次选择路线。"
        "生成今日可推进的轻量安排（主线与支线），不是待办清单；具体、可单独完成、可判断是否做完。"
        "用户填写的「今日自定义事项」必须优先编入；若与状态冲突则降难度而非忽略。"
        "以「人生阶段身份」为主要参考，「具体职业」仅辅助。"
        "语气温和、具体；不要太中二，不要心理咨询，不要鸡汤。"
        "只输出严格 JSON，不要 markdown。"
    )

    user_content = f"""
【人生路线】
{json.dumps(route_snapshot, ensure_ascii=False, indent=2)}

【推进历史】
{json.dumps(history_snapshot, ensure_ascii=False, indent=2)}

【今日状态（生成前已确认，勿要求用户再选路线）】
{json.dumps(today_snapshot, ensure_ascii=False, indent=2)}

只返回以下 JSON（camelCase），不要返回 optionalPaths、choices：
{{
  "routeContinuation": "1-2句，说明今日安排如何衔接其长期路线",
  "worldState": {{
    "title": "今日状态模式名称，如：低消耗恢复 / 正常推进 / 轻挑战 / 稳步成长",
    "description": "2-3句：综合长期路线 + 今天状态 + 今天模式 + 是否想出门，说明今天适合怎样推进（告知感，非让用户选择）"
  }},
  "mainQuest": {{
    "title": "今日主线标题",
    "goal": "今日主线目标",
    "estimatedTime": "预计总耗时",
    "tasks": [
      {{
        "id": "task_1",
        "title": "子任务标题",
        "action": "具体行动",
        "estimatedTime": "约 10 分钟",
        "reward": {{ "energy": 0, "explore": 0, "express": 0, "discipline": 0, "social": 0, "growth": 0 }}
      }}
    ]
  }},
  "sideQuests": [
    {{
      "id": "side_1",
      "title": "支线标题",
      "action": "具体行动",
      "reward": {{ "energy": 0, "explore": 0, "express": 0, "discipline": 0, "social": 0, "growth": 0 }},
      "rewardText": "奖励说明"
    }}
  ],
  "notRecommend": ["不建议1", "不建议2"],
  "ending": "一句温和、有陪伴感的结尾"
}}

要求：
- worldState 必须由「长期路线 + 今天状态 + 今天模式 + 是否想出门」共同决定，title 体现今日节奏
- 今天模式「降低难度」或状态「很累」→ 偏低消耗恢复；「想挑战一点」→ 轻挑战；「正常推进」→ 正常推进模式
- mainQuest.tasks 恰好 3 个，id 为 task_1/2/3；每项 reward 单项 0-3
- 若用户有自定义任务，至少 1 个 task 必须体现（可降难度）
- sideQuests 2-3 条
- 禁止 abstract 任务；不要返回 roleTitle、mainQuest.actions、optionalPaths
- 若用户不满意今日状态判断，应通过重新生成或修改今日状态解决，不在结果页二次选路
""".strip()

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]
