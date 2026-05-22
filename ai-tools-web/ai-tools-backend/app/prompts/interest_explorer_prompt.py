"""AI 兴趣推荐 / 兴趣探索器 — Prompt 封装。"""

from __future__ import annotations

import json
from typing import Any, Dict, List


def build_interest_explorer_messages(form: Dict[str, Any]) -> List[Dict[str, str]]:
    user_snapshot = {
        "当前阶段": form.get("life_stage") or "",
        "工作/学习状态": form.get("work_state") or "",
        "社交倾向": form.get("social_style") or "",
        "更喜欢": form.get("preferences") or [],
        "预算": form.get("budget") or "",
        "周末一般状态": form.get("weekend_state") or "",
        "最想获得什么": form.get("goals") or [],
        "最近的状态/想法": (form.get("extra_notes") or "").strip() or "无",
    }

    system_content = (
        "你是帮年轻人找兴趣的生活顾问，不是心理咨询师，也不是职业测评师。"
        "语气轻松、有生活感，像懂用户的朋友：具体、可执行，不要鸡汤，不要空泛套话"
        "（例如「做自己喜欢的事」「找到真正的自己」）。"
        "根据用户的精力、社交倾向、预算推荐真正适合的兴趣，解释为什么以前容易坚持不下去。"
        "不要推荐具体商家、店名或地图地址。新手入门要写低成本可执行步骤。"
        "只输出严格 JSON，不要 markdown，不要多余解释。"
    )

    user_content = f"""
请根据用户状态，推荐适合的兴趣方向。

用户状态：
{json.dumps(user_snapshot, ensure_ascii=False, indent=2)}

只返回以下 JSON 结构（字段名必须一致）：
{{
  "personality": {{
    "type_title": "兴趣人格类型，如：低消耗恢复型 / 安静探索型 / 轻社交体验型 / 表达创造型 / 成长驱动型 / 情绪回血型",
    "analysis": "2-3句简短分析，贴合用户",
    "why_past_failed": "1-2句：为什么以前容易坚持不下去（要具体，不要指责用户）"
  }},
  "interests": [
    {{
      "name": "兴趣名称，如：羽毛球、摄影、City Walk",
      "why_fit": "为什么适合你，1-2句",
      "difficulty": 2,
      "cost_level": "低",
      "social_level": "中",
      "long_term": "适合长期坚持 / 适合阶段性尝试",
      "best_time": "适合什么时候开始，如：工作日晚上 / 周末上午",
      "starter_tip": "新手如何低成本开始，要具体可执行"
    }}
  ],
  "avoid": ["不建议尝试的兴趣及原因1", "原因2"],
  "week_plan": [
    {{ "day": "周三", "activity": "下班后去附近羽毛球馆体验一次" }},
    {{ "day": "周五", "activity": "一个人去咖啡店待1小时" }},
    {{ "day": "周末", "activity": "尝试一次 City Walk" }}
  ],
  "lazy_fallback": {{
    "title": "最低门槛版本标题",
    "description": "完全不想动时的方案，2-3句，不自责"
  }}
}}

要求：
- interests 必须恰好 5 个，从羽毛球、健身、夜骑、摄影、City Walk、AI绘画、吉他、阅读、咖啡探店、徒步、游泳、舞蹈、写作、桌游、攀岩、烘焙、自媒体、配音、演讲表达、书法、手工、拼图、露营、电影、宠物相关等方向中选，要贴合用户状态
- difficulty 为 1-5 整数（入门难度）
- cost_level、social_level 只能是：低、中、高
- avoid 2-3 条，说明目前不适合的兴趣类型及原因
- week_plan 3-4 条，轻量一周体验，具体到哪天做什么
- 用户社恐/很累时，不要推高强度社交型兴趣为主
- 用户预算低时，优先推荐低成本入门方式
""".strip()

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]
