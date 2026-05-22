from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from app.ai_short_drama.material_store import material_store

STYLE_DEFAULT = "cn_internet_anime"
MIN_REUSE_SCORE = 4


def normalize_style(style: str) -> str:
    s = (style or "").strip().lower()
    return s or STYLE_DEFAULT


def build_cache_key(
    *,
    material_type: str,
    scene: str,
    emotion: str,
    style: str,
    tags: List[str],
) -> str:
    tag_part = ",".join(sorted({str(t).strip().lower() for t in tags if str(t).strip()}))
    raw = "|".join(
        [
            material_type.strip().lower(),
            scene.strip().lower(),
            emotion.strip().lower(),
            normalize_style(style),
            tag_part,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def find_cached_dynamic_material(
    *,
    material_type: str,
    scene: str,
    emotion: str,
    style: str,
    tags: List[str],
) -> Optional[Dict[str, Any]]:
    """
    缓存规则：scene + emotion + style + type 一致，且 tags 重合足够。
  仅匹配 ai_generated=true 的动态素材。
    """
    cache_key = build_cache_key(
        material_type=material_type,
        scene=scene,
        emotion=emotion,
        style=style,
        tags=tags,
    )
    tag_set = {str(t).strip().lower() for t in tags if str(t).strip()}

    try:
        items = material_store.list_materials(type_filter=material_type)
    except Exception:
        return None

    best: Optional[Dict[str, Any]] = None
    best_score = 0

    for item in items:
        if not item.get("aiGenerated"):
            continue
        item_tags = {str(t).strip().lower() for t in (item.get("tags") or [])}
        item_ck = item.get("cacheKey") or ""
        if item_ck and item_ck != cache_key:
            continue

        score = 0
        if (item.get("scene") or "none").lower() == (scene or "none").lower():
            score += 3
        if (item.get("emotion") or "none").lower() == (emotion or "none").lower():
            score += 2
        if normalize_style(item.get("style") or "") == normalize_style(style):
            score += 2
        overlap = len(tag_set & item_tags)
        score += overlap * 2
        if item.get("cacheKey") == cache_key:
            score += 5

        if score > best_score:
            best_score = score
            best = item

    if best and best_score >= MIN_REUSE_SCORE:
        return {**best, "cacheHit": True}
    return None
