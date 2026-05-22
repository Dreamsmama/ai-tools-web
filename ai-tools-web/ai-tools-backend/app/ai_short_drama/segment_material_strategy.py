from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional, Tuple

from app.ai_short_drama.scene_intent import (
    SceneIntent,
    build_intent_tags,
    infer_scene_intent,
    strategy_for_scene_intent,
)

ContentType = Literal["monologue", "career", "dialogue", "crisis", "ending"]
MaterialType = Literal["character", "scene", "ui", "effects", "props"]

# 文案类型 → 优先素材类型（按顺序尝试）
PREFERRED_TYPES: Dict[ContentType, List[str]] = {
    "monologue": ["scene"],
    "career": ["character"],
    "dialogue": ["ui", "props"],
    "crisis": ["effects", "ui"],
    "ending": ["scene"],
}

# 不再写死工位/会议室；场景由 sceneIntent 决定
CONTENT_SCENE_HINTS: Dict[ContentType, List[str]] = {
    "monologue": [],
    "career": [],
    "dialogue": [],
    "crisis": [],
    "ending": [],
}

FORBID_CHARACTER = frozenset({"monologue", "dialogue", "crisis", "ending"})

_DIALOGUE_PATTERNS = (
    r"会说[：:]",
    r"说[：:]",
    r"老板",
    r"开发",
    r"运营",
    r"产品",
    r"测试",
    r"HR",
    r"用户要",
    r"「",
    r"『",
)
_CRISIS_PATTERNS = (
    r"报警",
    r"上线",
    r"崩溃",
    r"背锅",
    r"报错",
    r"故障",
    r"宕机",
    r"红色",
    r"系统",
    r"凌晨",
)
_CAREER_PATTERNS = (
    r"最重要的是",
    r"最累的",
    r"这个岗位",
    r"这个职业",
    r"程序员",
    r"产品经理",
    r"最累的不是",
)
_MONOLOGUE_PATTERNS = (
    r"很多人觉得",
    r"真正做过",
    r"才知道",
    r"👉",
    r"因为每天都在",
)
_ENDING_PATTERNS = (
    r"如果重新选",
    r"还会做",
    r"吗？",
    r"吗\?",
)


def classify_segment_content(
    text: str,
    *,
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
) -> ContentType:
    """根据段落文案推断内容类型，决定素材优先级。"""
    t = (text or "").strip()
    if not t:
        return "monologue"

    if segment_no >= total_segments or any(re.search(p, t) for p in _ENDING_PATTERNS):
        if re.search(r"如果重新|还会做|吗", t):
            return "ending"

    if any(re.search(p, t) for p in _CRISIS_PATTERNS):
        return "crisis"

    if any(re.search(p, t) for p in _DIALOGUE_PATTERNS):
        return "dialogue"

    # 开场独白优先于职业描述（避免「很多人觉得 + 程序员最累」被判成 career）
    if any(re.search(p, t) for p in _MONOLOGUE_PATTERNS):
        return "monologue"

    if any(re.search(p, t) for p in _CAREER_PATTERNS):
        return "career"

    if segment_no <= 2:
        return "monologue"

    if segment_no >= max(1, total_segments - 1):
        return "ending"

    return "monologue"


def strategy_for_content(content_type: ContentType) -> Dict[str, Any]:
    prefer = list(PREFERRED_TYPES.get(content_type, ["scene"]))
    scene_hints = list(CONTENT_SCENE_HINTS.get(content_type, []))
    forbid_character = content_type in FORBID_CHARACTER
    primary = prefer[0] if prefer else "scene"
    return {
        "contentType": content_type,
        "preferTypes": prefer,
        "primaryMaterialType": primary,
        "sceneHints": scene_hints,
        "forbidCharacter": forbid_character,
    }


def build_segment_tags(
    base_tags: List[str],
    content_type: ContentType,
    emotion: str,
    *,
    scene_intent: Optional[SceneIntent] = None,
    text: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    role_key: str = "",
    career_cn: str = "",
) -> List[str]:
    """为匹配追加内容类型 + sceneIntent + 职业视觉 tag。"""
    intent = scene_intent or infer_scene_intent(
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
    )
    tags = build_intent_tags(
        intent,
        base_tags,
        emotion,
        text=text,
        segment_no=segment_no,
        role_key=role_key,
        career_cn=career_cn,
    )
    strat = strategy_for_content(content_type)
    if content_type not in tags:
        tags.append(content_type)
    for hint in strat["sceneHints"]:
        if hint not in tags:
            tags.append(hint)
    if content_type == "dialogue":
        for ui in ("phone_message", "elevator", "headphones", "night_light"):
            if ui not in tags:
                tags.append(ui)
    if content_type == "crisis":
        for k in ("alert", "error_log", "terminal", "oncall"):
            if k not in tags:
                tags.append(k)
    return tags


def merged_material_strategy(
    content_type: ContentType,
    scene_intent: SceneIntent,
    *,
    text: str = "",
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    used_scene_keys: Optional[set] = None,
    role_key: str = "",
    career_cn: str = "",
) -> Dict[str, Any]:
    """合并文案类型与 sceneIntent：优先用语义镜头决定场景/UI。"""
    content_strat = strategy_for_content(content_type)
    intent_strat = strategy_for_scene_intent(
        scene_intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=role_key,
        career_cn=career_cn,
    )
    prefer = list(intent_strat["preferTypes"])
    for pt in content_strat["preferTypes"]:
        if pt not in prefer:
            prefer.append(pt)
    scene_hints = list(intent_strat["sceneHints"])
    for hint in content_strat.get("sceneHints") or []:
        if hint not in scene_hints:
            scene_hints.append(hint)
    forbid_character = content_strat["forbidCharacter"] and intent_strat["forbidCharacter"]
    primary = intent_strat["primaryMaterialType"]
    if content_type == "career":
        primary = "character"
        prefer = ["character"] + [p for p in prefer if p != "character"]
    return {
        "contentType": content_type,
        "sceneIntent": scene_intent,
        "preferTypes": prefer,
        "primaryMaterialType": primary,
        "sceneHints": scene_hints,
        "sceneKey": intent_strat["sceneKey"],
        "forbidCharacter": forbid_character,
    }
