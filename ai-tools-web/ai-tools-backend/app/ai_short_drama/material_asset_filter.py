from __future__ import annotations

from typing import Any, Dict, List

PLACEHOLDER_URL_MARKERS = (
    "/placeholders/",
    "/short-drama/placeholders/",
    "default-office.png",
    "default-night-office",
    "default-desk",
    "default-feishu",
    "default-meeting",
)


def is_placeholder_material_record(item: Dict[str, Any]) -> bool:
    """占位/纯色素材不得参与正式匹配。"""
    if bool(item.get("isPlaceholder") or item.get("is_placeholder")):
        return True
    if (item.get("type") or "") == "placeholder":
        return True
    src = str(item.get("source") or "").lower()
    if src == "placeholder":
        return True
    tags = item.get("tags") or []
    if isinstance(tags, list):
        tag_set = {str(t).strip().lower() for t in tags if str(t).strip()}
        if "placeholder" in tag_set or "solid_color" in tag_set:
            return True
    url = (item.get("url") or "").lower()
    if any(m in url for m in PLACEHOLDER_URL_MARKERS):
        return True
    name = (item.get("name") or "").lower()
    if "占位" in name or "placeholder" in name:
        return True
    return False


def is_landscape_material_record(item: Dict[str, Any]) -> bool:
    """scene/ui/effect 横图不得参与匹配。"""
    mtype = (item.get("type") or "scene").lower()
    if mtype in ("character", "placeholder"):
        return False
    if item.get("isVertical") is False:
        return True
    w = int(item.get("imageWidth") or 0)
    h = int(item.get("imageHeight") or 0)
    if w > 0 and h > 0 and w > h:
        return True
    return False


def filter_matchable_materials(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        i
        for i in items
        if not is_placeholder_material_record(i) and not is_landscape_material_record(i)
    ]
