"""AI 人生副本 — Prompt 封装。"""

from __future__ import annotations

import json
from typing import Any, Dict, List


def build_life_rpg_messages(form: Dict[str, Any]) -> List[Dict[str, str]]:
    user_snapshot = {
        "想成为怎样的人": form.get("target_persona") or "",
        "今天状态": form.get("energy_level") or "",
        "当前心情": form.get("mood") or "",
        "今天想投入的方向": form.get("focus_directions") or [],
        "今天是否想出门": form.get("go_out") or "",
        "当前身份/职业": form.get("occupation") or "未填写",
        "补充描述": (form.get("extra_notes") or "").strip() or "无",
    }

    system_content = (
        "你是「人生副本」成长向导，帮用户把现实生活轻量游戏化。"
        "语气像 RPG 任务面板里的靠谱队友：具体、有画面感、带一点游戏感，"
        "但不要中二、不要心理咨询腔、不要鸡汤。"
        "你不是命令用户，而是给出可选成长路线和可执行任务。"
        "每个子任务必须可单独完成、可判断是否做完，不要抽象空话。"
        "只输出严格 JSON，不要 markdown，不要多余解释。"
    )

    user_content = f"""
根据用户选择，生成今日人生副本。

用户输入：
{json.dumps(user_snapshot, ensure_ascii=False, indent=2)}

只返回以下 JSON（字段名必须一致，使用 camelCase）：
{{
  "roleTitle": "角色路线名称",
  "roleSummary": "2-3句，分析用户正在塑造什么样的人",
  "worldState": {{
    "title": "今日世界状态标题",
    "description": "1-2句氛围描述"
  }},
  "mainQuest": {{
    "title": "今日主线任务标题",
    "goal": "任务目标，1句",
    "estimatedTime": "预计总耗时，如：约 30 分钟",
    "tasks": [
      {{
        "id": "task_1",
        "title": "子任务标题",
        "action": "具体行动，必须可执行、可判断是否完成",
        "estimatedTime": "预计耗时，如：约 10 分钟",
        "reward": {{
          "energy": 0,
          "explore": 0,
          "express": 0,
          "discipline": 0,
          "social": 0,
          "growth": 0
        }}
      }}
    ]
  }},
  "sideQuests": [
    {{
      "id": "side_1",
      "title": "支线标题",
      "action": "具体行动",
      "reward": {{
        "energy": 0,
        "explore": 0,
        "express": 0,
        "discipline": 0,
        "social": 0,
        "growth": 0
      }},
      "rewardText": "奖励说明"
    }}
  ],
  "choices": [
    {{ "name": "恢复路线", "description": "适合低能量状态", "suggestion": "具体建议" }},
    {{ "name": "成长路线", "description": "适合想变强一点", "suggestion": "具体建议" }},
    {{ "name": "探索路线", "description": "适合想找回生活感", "suggestion": "具体建议" }}
  ],
  "notRecommend": ["不建议1", "不建议2"],
  "ending": "一句游戏感结尾，不要鸡汤"
}}

要求：
- mainQuest.tasks 必须恰好 3 个，id 分别为 task_1、task_2、task_3
- 每个子任务独立 reward，单项属性 0-3，不要夸张
- 子任务必须轻量具体，例如：散步 15 分钟、写 100 字、看 10 分钟课程、做 10 个深蹲、给朋友发一句消息、整理桌面 5 分钟
- 禁止抽象任务：不要「提升自己」「保持积极」「多思考人生」等
- sideQuests 2-3 条，id 为 side_1、side_2…，每条含 reward 与 rewardText
- 不要返回 mainQuest.actions
- choices 恰好 3 条：恢复路线、成长路线、探索路线
- 用户很累/焦虑时，任务要低消耗、可在家完成
""".strip()

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]
