from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.ai_short_drama.material_infer import normalize_scene_key
from app.ai_short_drama.scene_intent import enrich_segment_with_scene_intent

logger = logging.getLogger(__name__)

_CODE_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_TRAILING_COMMA = re.compile(r",(\s*[}\]])")


def strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    m = _CODE_FENCE.search(t)
    if m:
        return m.group(1).strip()
    return t


def fix_trailing_commas(s: str) -> str:
    prev = None
    cur = s
    while prev != cur:
        prev = cur
        cur = _TRAILING_COMMA.sub(r"\1", cur)
    return cur


def try_parse_json_array(raw: str) -> Optional[List[Any]]:
    candidates = [strip_code_fences(raw), (raw or "").strip()]
    seen = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        for attempt in (c, fix_trailing_commas(c)):
            try:
                obj = json.loads(attempt)
                if isinstance(obj, list):
                    return obj
                if isinstance(obj, dict):
                    for key in ("segments", "shots", "storyboard", "data", "items"):
                        inner = obj.get(key)
                        if isinstance(inner, list):
                            return inner
            except json.JSONDecodeError:
                pass
            s = attempt.find("[")
            e = attempt.rfind("]")
            if s >= 0 and e > s:
                chunk = attempt[s : e + 1]
                for ch in (chunk, fix_trailing_commas(chunk)):
                    try:
                        obj = json.loads(ch)
                        if isinstance(obj, list):
                            return obj
                    except json.JSONDecodeError:
                        continue
    return None


def try_parse_json_object(raw: str) -> Optional[Dict[str, Any]]:
    candidates = [strip_code_fences(raw), (raw or "").strip()]
    seen = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        for attempt in (c, fix_trailing_commas(c)):
            try:
                obj = json.loads(attempt)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                pass
            s = attempt.find("{")
            e = attempt.rfind("}")
            if s >= 0 and e > s:
                chunk = attempt[s : e + 1]
                for ch in (chunk, fix_trailing_commas(chunk)):
                    try:
                        obj = json.loads(ch)
                        if isinstance(obj, dict):
                            return obj
                    except json.JSONDecodeError:
                        continue
    return None


def try_parse_segment_payload(raw: str) -> Optional[Dict[str, Any]]:
    """
    解析 AI 返回：优先 {{ title, segments }} 对象，兼容纯 segments 数组。
    """
    obj = try_parse_json_object(raw)
    if obj and isinstance(obj.get("segments"), list):
        return _segment_payload_from_obj(obj)

    arr = try_parse_json_array(raw)
    if arr:
        return {"title": "", "segments": arr}

    if obj:
        for key in ("segments", "shots", "items"):
            inner = obj.get(key)
            if isinstance(inner, list):
                return _segment_payload_from_obj({**obj, "segments": inner})
    return None


def _segment_payload_from_obj(obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": str(obj.get("title") or "").strip(),
        "segments": obj["segments"],
        "detectedCareer": str(obj.get("detectedCareer") or obj.get("detected_career") or "").strip(),
        "detectedRole": str(obj.get("detectedRole") or obj.get("detected_role") or "").strip(),
        "emotionStyle": str(obj.get("emotionStyle") or obj.get("emotion_style") or "").strip(),
    }


def normalize_segment_dict(
    item: Dict[str, Any],
    index: int,
    default_role: str,
    *,
    max_text_len: int = 40,
) -> Dict[str, Any]:
    tags_raw = item.get("imageTags") or item.get("image_tags") or []
    tags = (
        [str(t).strip().lower() for t in tags_raw if str(t).strip()]
        if isinstance(tags_raw, list)
        else []
    )

    text = str(item.get("text") or item.get("subtitle") or "").strip()
    if max_text_len > 0 and len(text) > max_text_len:
        text = text[:max_text_len]

    try:
        duration = int(item.get("duration", 3))
    except (TypeError, ValueError):
        duration = 3
    duration = min(8, max(2, duration))

    try:
        segment_no = int(item.get("segmentNo", item.get("segment_no", item.get("shotNo", index + 1))))
    except (TypeError, ValueError):
        segment_no = index + 1

    props_raw = item.get("props") or []
    props = (
        [str(p).strip().lower() for p in props_raw if str(p).strip()]
        if isinstance(props_raw, list)
        else []
    )

    seg = {
        "segmentNo": segment_no,
        "duration": duration,
        "text": text or "……",
        "scene": normalize_scene_key(str(item.get("scene") or "office_day")),
        "role": str(item.get("role") or default_role).strip(),
        "emotion": str(item.get("emotion") or "平静").strip(),
        "imageTags": tags,
        "props": props,
        "sceneIntent": str(item.get("sceneIntent") or item.get("scene_intent") or "").strip(),
        "sceneDescription": str(
            item.get("sceneDescription") or item.get("scene_description") or ""
        ).strip(),
    }
    return enrich_segment_with_scene_intent(seg, segment_no=segment_no)


def normalize_shot_dict(item: Dict[str, Any], index: int, default_role: str) -> Dict[str, Any]:
    tags_raw = item.get("imageTags") or item.get("image_tags") or []
    tags = [str(t).strip().lower() for t in tags_raw if str(t).strip()] if isinstance(tags_raw, list) else []

    subtitle = str(item.get("subtitle") or "").strip()
    if len(subtitle) > 25:
        subtitle = subtitle[:25]

    try:
        duration = int(item.get("duration", 4))
    except (TypeError, ValueError):
        duration = 4
    duration = min(15, max(2, duration))

    try:
        shot_no = int(item.get("shotNo", item.get("shot_no", index + 1)))
    except (TypeError, ValueError):
        shot_no = index + 1

    props_raw = item.get("props") or []
    props = (
        [str(p).strip().lower() for p in props_raw if str(p).strip()]
        if isinstance(props_raw, list)
        else []
    )

    seg = normalize_segment_dict(
        {
            **item,
            "text": subtitle,
            "segmentNo": shot_no,
        },
        index,
        default_role,
    )
    return {
        "shotNo": seg["segmentNo"],
        "duration": seg["duration"],
        "scene": seg["scene"],
        "role": seg["role"],
        "emotion": seg["emotion"],
        "subtitle": seg["text"],
        "imageTags": seg["imageTags"],
        "props": seg["props"],
    }
