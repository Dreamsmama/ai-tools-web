"""AI 人生副本 — 创建人生路线 Prompt。"""

from __future__ import annotations

import json
from typing import Any, Dict, List

_TEMPLATE_LABELS = {
    "growth": "成长推进型",
    "recovery": "生活恢复型",
    "interest": "兴趣培养型",
    "journal": "人生记录型",
}


def build_life_rpg_route_messages(form: Dict[str, Any]) -> List[Dict[str, str]]:
    states = form.get("life_states") or []
    if not states:
        target = (form.get("target_person") or "").strip()
        if target == "自定义":
            target = (form.get("custom_target_person") or form.get("custom_life_state") or "").strip()
        if target:
            states = [target]

    template_id = (form.get("direction_template") or "").strip()
    template_label = _TEMPLATE_LABELS.get(template_id, "")
    directions = form.get("long_term_directions") or []
    if not template_label and directions:
        template_label = directions[0]

    keywords = form.get("life_keywords") or []

    user_snapshot = {
        "人生状态": states,
        "人生方向模板": template_label or "未选择",
        "人生关键词": keywords,
        "AI更了解你的补充": (form.get("status_notes") or form.get("custom_long_term_goals") or "").strip()
        or "无",
        "人生阶段身份": (form.get("identity_type") or form.get("identity") or "").strip() or "未填写",
        "具体职业": (form.get("occupation") or "").strip() or "未填写",
    }

    system_content = (
        "你是人生路线设计师，根据用户的人生状态、方向模板与关键词，"
        "帮其梳理一条可长期坚持的成长路线与角色气质。"
        "语气温和、具体、有陪伴感；不要中二、不要鸡汤、不要心理测试腔、不要 KPI 或 Todo 工具腔。"
        "输出人生角色与路线说明，不是任务清单或打卡计划。"
        "只输出严格 JSON，不要 markdown。"
    )

    user_content = f"""
根据用户的人生状态、方向模板与关键词，设计一条「人生路线」。

用户输入：
{json.dumps(user_snapshot, ensure_ascii=False, indent=2)}

只返回以下 JSON（camelCase）：
{{
  "routeTitle": "路线名称，如：探索成长者 / 生活恢复者",
  "routeSummary": "2-3句，说明 AI 理解到的用户正在塑造怎样的人生",
  "coreAttributes": ["energy", "explore", "growth"],
  "longTermMainLine": "一句话长期主线",
  "suggestedGrowthStyle": "适合你的推进方式，1-2句",
  "avoidStyle": "不适合你的方式，1-2句"
}}

要求：
- coreAttributes 从 energy/explore/express/discipline/social/growth 中选 2-3 个
- 必须尊重「人生关键词」与补充说明的原意
- 以人生状态与方向模板为主，职业仅作微调
- 不要生成具体今日任务或打卡项
""".strip()

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]
