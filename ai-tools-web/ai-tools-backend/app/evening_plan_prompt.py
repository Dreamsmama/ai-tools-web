"""下班后不知道干什么 — AI Prompt 封装。"""

from __future__ import annotations

import json
from typing import Any, Dict, List


def build_evening_plan_messages(form: Dict[str, Any]) -> List[Dict[str, str]]:
    """根据用户表单构建 DashScope messages。"""
    city = (form.get("city") or "").strip()
    interests = form.get("interests") or []
    extra = (form.get("extra_notes") or "").strip()

    city_hint = (
        f"用户所在城市：{city}。推荐「附近可搜索的类型」（如附近拉面店、附近公园、附近清吧、附近羽毛球馆），"
        "不要编造具体店名或地址。"
        if city
        else "用户未填城市，不要写具体地点名，用「家附近」「楼下」等泛指即可。"
    )

    user_snapshot = {
        "当前城市": city or "未填写",
        "现在时间": form.get("current_time") or "",
        "今天状态": form.get("energy_level") or "",
        "今天心情": form.get("mood") or "",
        "是否想出门": form.get("go_out") or "",
        "是否想社交": form.get("social") or "",
        "预算": form.get("budget") or "",
        "今天更想做什么": interests,
        "额外补充": extra or "无",
    }

    system_content = (
        "你是帮朋友安排下班晚上的生活顾问。语气像靠谱的朋友：具体、轻松、有生活感，"
        "不要油腻，不要鸡汤，不要空泛套话（例如「做自己喜欢的事」「听从内心」）。"
        "建议必须可执行：说清楚吃什么类型、做什么、大概花多久多少钱。"
        "尊重用户精力与预算，累的时候别硬推高强度社交或远途。"
        "只输出严格 JSON，不要 markdown，不要多余解释。"
    )

    user_content = f"""
请根据用户当前状态，安排今晚。{city_hint}

用户状态：
{json.dumps(user_snapshot, ensure_ascii=False, indent=2)}

只返回以下 JSON 结构（字段名必须一致）：
{{
  "mode": "今晚推荐模式，如：低消耗恢复型 / 轻社交放松型 / 出门探索型 / 运动回血型",
  "plans": [
    {{
      "plan_type": "方案一：吃什么",
      "title": "简短标题",
      "reason": "1-2句推荐理由，贴合用户状态",
      "actions": ["具体行动1", "具体行动2"],
      "cost": "预计花费，如：约 60 元",
      "duration": "预计耗时，如：约 45 分钟",
      "fit_score": 5
    }},
    {{
      "plan_type": "方案二：做什么",
      "title": "...",
      "reason": "...",
      "actions": ["..."],
      "cost": "...",
      "duration": "...",
      "fit_score": 4
    }},
    {{
      "plan_type": "方案三：回家后怎么收尾",
      "title": "...",
      "reason": "...",
      "actions": ["..."],
      "cost": "...",
      "duration": "...",
      "fit_score": 5
    }}
  ],
  "avoid": ["避坑建议1", "避坑建议2"],
  "lazy_fallback": {{
    "title": "最低成本躺平方案标题",
    "description": "不自责、能立刻做的替代，2-3句"
  }},
  "tomorrow_tips": ["明天状态保护建议1", "明天状态保护建议2"]
}}

要求：
- plans 必须恰好 3 条，分别对应吃、做、回家收尾
- fit_score 为 1-5 的整数，表示适合程度
- avoid 2-3 条，根据用户状态提醒今晚别踩的坑
- lazy_fallback 要给「只想躺平」时的零压力方案
- tomorrow_tips 1-2 条，帮助保护明天状态（睡眠、饮食、节奏）
- 方案要与用户「更想做什么」多选项、预算、出门/社交意愿一致
- 若用户说累/焦虑/不想社交，不要推荐高强度聚会或远途折腾
""".strip()

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]
