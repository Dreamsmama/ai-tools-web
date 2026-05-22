from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.ai_short_drama.material_infer import normalize_scene_key, scene_match_keys

# 场景 → 占位图（使用 public 已有 PNG，保证始终可显示）
PLACEHOLDER_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "placeholder_night_office",
        "name": "深夜工位默认图",
        "type": "placeholder",
        "url": "/short-drama/placeholders/default-night-office.png",
        "scene": "night_office",
        "tags": ["night_office", "office_night", "late", "night"],
    },
    {
        "id": "placeholder_office_day",
        "name": "办公室默认图",
        "type": "placeholder",
        "url": "/short-drama/placeholders/default-office.png",
        "scene": "office_day",
        "tags": ["office", "office_day", "workplace"],
    },
    {
        "id": "placeholder_meeting_room",
        "name": "会议室默认图",
        "type": "placeholder",
        "url": "/short-drama/placeholders/default-meeting.png",
        "scene": "meeting_room",
        "tags": ["meeting_room", "meeting"],
    },
    {
        "id": "placeholder_desk",
        "name": "工位默认图",
        "type": "placeholder",
        "url": "/short-drama/placeholders/default-desk.png",
        "scene": "desk",
        "tags": ["desk", "workstation", "工位"],
    },
    {
        "id": "placeholder_feishu",
        "name": "飞书消息默认图",
        "type": "placeholder",
        "url": "/short-drama/placeholders/default-feishu.png",
        "scene": "desk",
        "tags": ["feishu", "messages", "chat", "ui"],
    },
    {
        "id": "placeholder_server",
        "name": "机房报警默认图",
        "type": "placeholder",
        "url": "/short-drama/ops_alert_001.png",
        "scene": "server_room",
        "tags": ["server_room", "alert", "ops"],
    },
    {
        "id": "placeholder_interview",
        "name": "面试间默认图",
        "type": "placeholder",
        "url": "/short-drama/hr_interview_001.png",
        "scene": "interview_room",
        "tags": ["interview_room", "interview", "hr"],
    },
]

DEFAULT_PLACEHOLDER_URL = "/short-drama/placeholders/default-office.png"


def get_placeholder_for_scene(
    scene: str = "",
    *,
    tags: Optional[List[str]] = None,
    emotion: str = "",
) -> Dict[str, Any]:
    """按场景/标签选择占位图，保证 url 非空。"""
    scene_key = normalize_scene_key(scene)
    tag_set = {str(t).strip().lower() for t in (tags or []) if str(t).strip()}

    if tag_set & {"feishu", "messages", "chat", "jira"}:
        for item in PLACEHOLDER_CATALOG:
            if item["id"] == "placeholder_feishu":
                return _placeholder_result(item)

    if emotion in ("tired", "stressed") and scene_key in ("office", "office_day", "desk", "none"):
        scene_key = "night_office"

    match_keys = set(scene_match_keys(scene_key))
    best: Optional[Dict[str, Any]] = None
    best_score = 0

    for item in PLACEHOLDER_CATALOG:
        item_scene = str(item.get("scene") or "")
        item_keys = set(scene_match_keys(item_scene))
        score = len(match_keys & item_keys)
        item_tags = set(item.get("tags") or [])
        score += len(match_keys & item_tags) * 2
        if score > best_score:
            best_score = score
            best = item

    if best is None:
        best = PLACEHOLDER_CATALOG[1]  # default-office

    return _placeholder_result(best)


def _placeholder_result(item: Dict[str, Any]) -> Dict[str, Any]:
    url = (item.get("url") or "").strip() or DEFAULT_PLACEHOLDER_URL
    return {
        "id": item["id"],
        "name": item.get("name", "场景占位图"),
        "url": url,
        "tags": list(item.get("tags") or []),
        "aiGenerated": False,
        "cacheHit": False,
        "source": "placeholder",
    }
