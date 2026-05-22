from __future__ import annotations

from typing import Any, Dict, List


def build_auto_tags(
    *,
    type: str = "",
    role: str = "",
    emotion: str = "",
    scene: str = "",
) -> List[str]:
    tags: List[str] = []

    def push(v: str) -> None:
        t = (v or "").strip().lower()
        if t and t != "none" and t not in tags:
            tags.append(t)

    push(type)
    push(role)
    push(emotion)
    push(scene)
    return tags


def merge_tags(manual: Any, auto: List[str]) -> List[str]:
    out: List[str] = []
    if isinstance(manual, list):
        for t in manual:
            n = str(t).strip().lower()
            if n and n not in out:
                out.append(n)
    for t in auto:
        if t not in out:
            out.append(t)
    return out


def ensure_material_tags(payload: Dict[str, Any], parsed_tags: List[str]) -> List[str]:
    auto = build_auto_tags(
        type=str(payload.get("type") or ""),
        role=str(payload.get("role") or ""),
        emotion=str(payload.get("emotion") or ""),
        scene=str(payload.get("scene") or ""),
    )
    return merge_tags(parsed_tags, auto)
