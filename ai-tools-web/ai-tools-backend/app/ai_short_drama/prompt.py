from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from app.ai_short_drama.prompt_scene_intent_block import (
    SCENE_INTENT_EXAMPLE_SEGMENT,
    SCENE_INTENT_PROMPT_BLOCK,
    VISUAL_DIRECTOR_PROMPT_APPENDIX,
)
from app.ai_short_drama.role_catalog import (
    prompt_role_catalog_block,
    prompt_user_career_instruction,
    resolve_from_user_selection,
)


def segment_count_for_duration(duration: str) -> Tuple[int, int]:
    """图文段落数量区间（每段约 2–4 秒）。"""
    if duration == "45秒":
        return 12, 16
    if duration == "60秒":
        return 16, 22
    return 8, 12


shot_count_for_duration = segment_count_for_duration


def _example_role_for_prompt(career: str) -> str:
    rk = resolve_from_user_selection(career) if career else ""
    if rk:
        return rk
    block = prompt_role_catalog_block()
    for line in block.splitlines():
        if "→ role=" in line:
            part = line.split('role="', 1)[-1]
            return part.rstrip('"').rstrip("）").rstrip(")")
    return "programmer"


def build_short_drama_messages(form: Dict[str, Any]) -> List[Dict[str, str]]:
    """生成「职业观察局」图文成片段落 Prompt。"""
    career = (form.get("career") or "").strip()
    theme = (form.get("theme") or "").strip()
    emotion_style = (form.get("emotion_style") or "").strip()
    example_role = _example_role_for_prompt(career)
    career_lock = prompt_user_career_instruction(career)

    user_snapshot = {
        "职业": career,
        "主题": theme,
        "情绪风格": emotion_style,
    }

    system_content = (
        "你是《职业观察局》的图文成片文案编辑，兼视觉导演。"
        "写打工人职业情绪独白，适合抖音/小红书/B站竖屏图文成片：一句文案配一张图。"
        "不要写短剧、不要连续对话、不要 speaker/dialogue/conflictLevel/reaction。"
        "文案要短句、分行感、有节奏、有共鸣、职业真实感；不要鸡汤、不要广告腔。"
        "结尾最后一段必须是向观众提问的互动句。"
        + VISUAL_DIRECTOR_PROMPT_APPENDIX
        + "只输出一个严格 JSON 对象，不要 markdown，不要解释。"
    )

    user_content = f"""
请根据以下设定，生成「职业观察局」风格图文成片段落：

{json.dumps(user_snapshot, ensure_ascii=False, indent=2)}

{career_lock}

系统当前注册的职业与 role 字段（必须使用表中的 role，不要臆造）：
{prompt_role_catalog_block()}

要求：
1. 按情绪节奏自然拆段，通常 10-20 段；每段一句或半句
2. 每段 text 不超过 28 个中文字符，适合底部字幕
3. 每段含 segmentNo, text, role, emotion, scene, sceneIntent, imageTags
4. 全片 role 与所选职业一致（role 值见上表）
5. emotion: calm/tired/stressed/normal/happy/confused/shocked/angry
{SCENE_INTENT_PROMPT_BLOCK}
10. 情绪风格：{emotion_style}

只返回 JSON：
{{
  "title": "标题",
  "segments": [
{SCENE_INTENT_EXAMPLE_SEGMENT}
  ]
}}
"""

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content.strip()},
    ]


def build_script_analysis_messages(
    form: Dict[str, Any],
    *,
    pre_split: List[str],
) -> List[Dict[str, str]]:
    """分析用户粘贴的完整文案：拆段并标注镜头元数据（职业以用户选择为准）。"""
    script = (form.get("script") or "").strip()
    career_hint = (form.get("career") or "").strip()
    role_catalog = prompt_role_catalog_block()
    example_role = _example_role_for_prompt(career_hint)

    if career_hint:
        hint_block = "\n" + prompt_user_career_instruction(career_hint)
    else:
        hint_block = (
            "\n用户未指定职业：请从下方职业表中选最接近的一项，"
            "detectedCareer 用中文名，detectedRole 用表中 role 值。"
        )

    pre_lines = "\n".join(f"- {i + 1}. {t}" for i, t in enumerate(pre_split[:40]))

    system_content = (
        "你是《职业观察局》图文成片编导，兼视觉导演。用户已写好完整文案，你的任务是："
        "按节奏拆成竖屏图文段落，并为每段标注 sceneIntent、sceneDescription、scene、emotion、imageTags。"
        "不要改写文案核心意思；不要写短剧对白格式。"
        + VISUAL_DIRECTOR_PROMPT_APPENDIX
        + "只输出一个严格 JSON 对象，不要 markdown，不要解释。"
    )

    user_content = f"""
用户完整文案：
\"\"\"
{script}
\"\"\"

{hint_block}

规则拆段参考：
{pre_lines or "（无）"}

系统注册职业（detectedCareer / detectedRole / 每段 role 必须来自此表）：
{role_catalog}

请输出 JSON：
{{
  "title": "一句吸引人的标题",
  "detectedCareer": "表中中文职业名",
  "detectedRole": "表中 role 字符串",
  "emotionStyle": "扎心|真实|压抑|搞笑|反转 之一",
  "segments": [
    {{
      "segmentNo": 1,
      "text": "保留用户原文，不超过 40 字",
      "role": "{example_role}",
      "emotion": "calm|tired|stressed|normal|happy|confused|shocked|angry",
      "sceneIntent": "opening|communication|work_pressure|fatigue|collapse|emotion|daily_life",
      "scene": "night_office|office_night|office_day|meeting_room|server_room|interview_room",
      "imageTags": ["opening", "empty_office", "calm"]
    }}
  ]
}}

要求：
1. 覆盖全文、顺序不变；按空行与语义拆段
2. 每段 text 来自用户原文
3. 若用户已指定职业，全片 role 必须与该职业 role 完全一致
4. 每段 sceneIntent 必须随文案变化；禁止写死「程序员工位/会议室/显示器」
5. imageTags 含 sceneIntent、emotion 与画面 tag；role 与职业一致即可
6. 未指定职业时，从职业表选最接近的一项，不要臆造 role
{SCENE_INTENT_PROMPT_BLOCK}
"""

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content.strip()},
    ]
