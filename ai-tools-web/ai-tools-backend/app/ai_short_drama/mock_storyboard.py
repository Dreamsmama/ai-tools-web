from __future__ import annotations

from typing import Any, Dict, List

from app.ai_short_drama.materials import CAREER_TAG_HINTS
from app.ai_short_drama.prompt import segment_count_for_duration
from app.ai_short_drama.role_catalog import resolve_role_key

ROLE_KEY_MAP = {
    "程序员": "programmer",
    "产品经理": "product_manager",
    "HR": "hr",
    "测试": "tester",
    "运维": "devops",
    "销售": "sales",
}


def _role_key(career: str) -> str:
    return resolve_role_key(career, "")


def _tags(career: str, *extra: str) -> List[str]:
    key = _role_key(career)
    base = list(CAREER_TAG_HINTS.get(career, ["office"]))
    if key not in base:
        base.insert(0, key)
    for t in extra:
        if t not in base:
            base.append(t)
    return base


def build_mock_segments(
    career: str, theme: str, emotion_style: str, duration: str
) -> List[Dict[str, Any]]:
    """职业观察局风格图文段落 mock。"""
    min_seg, max_seg = segment_count_for_duration(duration)
    rk = _role_key(career)
    theme_short = (theme or "打工人的一天").strip()[:12]

    lines: List[Dict[str, Any]] = [
        {"text": "很多人觉得：", "emotion": "calm", "scene": "office_day", "duration": 3},
        {
            "text": f"{career}最重要的是：",
            "emotion": "calm",
            "scene": "office_day",
            "duration": 3,
        },
        {"text": "把事推进下去。", "emotion": "calm", "scene": "desk", "duration": 3},
        {"text": "但真正做过的人都知道。", "emotion": "normal", "scene": "office_day", "duration": 3},
        {
            "text": f"这个岗位最累的，很多时候不是{theme_short}。",
            "emotion": "stressed",
            "scene": "meeting_room",
            "duration": 4,
        },
        {"text": "而是：", "emotion": "calm", "scene": "meeting_room", "duration": 2},
        {"text": "👉 谁都要沟通。", "emotion": "stressed", "scene": "meeting_room", "duration": 3},
        {"text": "开发会说：", "emotion": "normal", "scene": "workstation", "duration": 2},
        {"text": "「这个做不了。」", "emotion": "stressed", "scene": "desk", "duration": 3},
        {"text": "老板会说：", "emotion": "normal", "scene": "meeting_room", "duration": 2},
        {"text": "「为什么还没上线？」", "emotion": "stressed", "scene": "meeting_room", "duration": 3},
        {"text": "很多人做久了以后，", "emotion": "tired", "scene": "office_night", "duration": 3},
        {"text": "会越来越像：", "emotion": "tired", "scene": "office_night", "duration": 2},
        {"text": "「夹在中间的人。」", "emotion": "tired", "scene": "night_office", "duration": 4},
        {"text": "因为每天都在：", "emotion": "tired", "scene": "night_office", "duration": 3},
        {"text": "协调、推进、解释、背压力。", "emotion": "tired", "scene": "night_office", "duration": 4},
        {"text": "很多人后来越来越疲惫。", "emotion": "tired", "scene": "night_office", "duration": 3},
        {"text": "不是因为不热爱工作。", "emotion": "normal", "scene": "office_day", "duration": 3},
        {"text": "而是长期被各种节奏拉扯。", "emotion": "tired", "scene": "night_office", "duration": 4},
        {
            "text": f"如果重新选一次，你还会做{career}吗？",
            "emotion": "calm",
            "scene": "office_day",
            "duration": 4,
        },
    ]

    picked = lines[:max_seg]
    while len(picked) < min_seg:
        picked.append(lines[len(picked) % len(lines)])

    segments: List[Dict[str, Any]] = []
    for idx, item in enumerate(picked):
        emotion = item.get("emotion") or "normal"
        scene = item.get("scene") or "office"
        segments.append(
            {
                "segmentNo": idx + 1,
                "duration": item.get("duration", 3),
                "text": str(item["text"])[:40],
                "role": rk,
                "emotion": emotion,
                "scene": scene,
                "imageTags": _tags(career, rk, scene.replace("_", " "), emotion),
                "props": [],
            }
        )
    return segments


def build_mock_shots(career: str, theme: str, emotion_style: str, duration: str) -> List[Dict[str, Any]]:
    """兼容旧接口：返回 shot 形状数据。"""
    segments = build_mock_segments(career, theme, emotion_style, duration)
    shots: List[Dict[str, Any]] = []
    for s in segments:
        shots.append(
            {
                "shotNo": s["segmentNo"],
                "duration": s["duration"],
                "scene": s["scene"],
                "role": career,
                "emotion": s["emotion"],
                "subtitle": s["text"],
                "imageTags": s["imageTags"],
                "props": s.get("props") or [],
            }
        )
    return shots


def build_mock_title(career: str, theme: str) -> str:
    theme_short = theme.strip()[:20] or "打工人的一天"
    if "产品经理" in career or career == "产品经理":
        return f"{career}最累的不是需求"
    return f"{career}：{theme_short}"
