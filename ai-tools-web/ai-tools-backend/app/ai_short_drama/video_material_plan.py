from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Optional

from app.ai_short_drama.scene_intent import normalize_scene_intent
from app.ai_short_drama.segment_material_strategy import classify_segment_content

logger = logging.getLogger(__name__)

SlotType = Literal["scene", "character", "ui", "effects"]

# 目标比例（图文成片，非连续动画）
TARGET_SCENE_RATIO = 0.55
TARGET_CHARACTER_RATIO = 0.30
TARGET_UI_RATIO = 0.15

MIN_CHARACTER_SLOTS = 2
MAX_CHARACTER_SLOTS = 4


def _seg_key(item: Dict[str, Any], fallback: int) -> int:
    return int(item.get("segmentNo") or fallback)


def _emotion_suggests_character(emotion: str) -> bool:
    em = (emotion or "").strip().lower()
    return em in (
        "疲惫",
        "累",
        "压力",
        "压抑",
        "紧张",
        "震惊",
        "懵",
        "愤怒",
        "生气",
        "tired",
        "stressed",
        "shocked",
        "angry",
        "confused",
    )


def _pick_character_indices(
    items: List[Dict[str, Any]],
    *,
    min_slots: int,
    max_slots: int,
) -> List[int]:
    """挑选应使用角色 IP 的段落序号（segmentNo）。"""
    n = len(items)
    if n == 0:
        return []

    scored: List[tuple[int, int, int]] = []
    for i, item in enumerate(items):
        seg_no = _seg_key(item, i + 1)
        text = item.get("text") or ""
        emotion = item.get("emotion") or ""
        ct = classify_segment_content(
            text,
            emotion=emotion,
            segment_no=seg_no,
            total_segments=n,
        )
        intent = normalize_scene_intent(
            item.get("sceneIntent"),
            text,
            emotion=emotion,
            segment_no=seg_no,
            total_segments=n,
        )
        score = 0
        if ct == "career":
            score += 100
        if ct == "crisis":
            score += 90
        if intent == "emotion":
            score += 70
        if intent == "fatigue":
            score += 45
        if _emotion_suggests_character(emotion):
            score += 50
        if ct == "ending" and i >= n - 2:
            score += 40
        if ct == "monologue" and i > 0 and i < n - 1:
            score += 15
        # 压力/崩溃/沟通段优先 UI，不用人物占坑
        if intent in ("work_pressure", "collapse", "communication", "opening"):
            score -= 120
        if i == 0:
            score -= 80
        if ct == "dialogue":
            score -= 30
        scored.append((score, seg_no, i))

    scored.sort(key=lambda x: (-x[0], x[2]))

    chosen: List[int] = []
    used_idx: set = set()

    no_character_intents = frozenset(
        {"opening", "communication", "work_pressure", "collapse", "daily_life"}
    )

    for score, seg_no, idx in scored:
        if score < 10 and len(chosen) >= min_slots:
            break
        if len(chosen) >= max_slots:
            break
        if idx in used_idx:
            continue
        item = items[idx]
        intent = normalize_scene_intent(
            item.get("sceneIntent"),
            item.get("text") or "",
            emotion=item.get("emotion") or "",
            segment_no=seg_no,
            total_segments=n,
        )
        if intent in no_character_intents:
            continue
        # 避免连续两段都是人物
        if chosen and abs(idx - max(used_idx)) < 2:
            continue
        chosen.append(seg_no)
        used_idx.add(idx)

    # 补足最少人物镜头（优先中间段，避免贴在一起）
    if len(chosen) < min_slots:
        for idx in range(1, max(1, n - 1)):
            if len(chosen) >= min_slots:
                break
            if idx in used_idx:
                continue
            intent = normalize_scene_intent(
                items[idx].get("sceneIntent"),
                items[idx].get("text") or "",
                emotion=items[idx].get("emotion") or "",
                segment_no=_seg_key(items[idx], idx + 1),
                total_segments=n,
            )
            if intent in no_character_intents:
                continue
            if any(abs(idx - u) < 2 for u in used_idx):
                continue
            seg_no = _seg_key(items[idx], idx + 1)
            chosen.append(seg_no)
            used_idx.add(idx)

    if len(chosen) < min_slots:
        for i, item in enumerate(items):
            if len(chosen) >= min_slots:
                break
            intent = normalize_scene_intent(
                item.get("sceneIntent"),
                item.get("text") or "",
                emotion=item.get("emotion") or "",
                segment_no=_seg_key(item, i + 1),
                total_segments=n,
            )
            if intent in no_character_intents:
                continue
            seg_no = _seg_key(item, i + 1)
            if seg_no not in chosen:
                chosen.append(seg_no)

    chosen.sort(
        key=lambda s: next(
            (j for j, it in enumerate(items) if _seg_key(it, j + 1) == s),
            s,
        )
    )
    return chosen[:max_slots]


def _pick_ui_indices(items: List[Dict[str, Any]], character_seg_nos: set) -> List[int]:
    """工作沟通 / 压力 / 崩溃 → UI / 特效镜头（按语义优先级）。"""
    n = len(items)
    ranked: List[tuple[int, int]] = []
    intent_weight = {
        "collapse": 100,
        "work_pressure": 90,
        "communication": 50,
        "fatigue": 20,
        "daily_life": 30,
    }
    for i, item in enumerate(items):
        seg_no = _seg_key(item, i + 1)
        if seg_no in character_seg_nos:
            continue
        text = item.get("text") or ""
        emotion = item.get("emotion") or ""
        intent = normalize_scene_intent(
            item.get("sceneIntent"),
            text,
            emotion=emotion,
            segment_no=seg_no,
            total_segments=n,
        )
        ct = classify_segment_content(text, segment_no=seg_no, total_segments=n)
        score = intent_weight.get(intent, 0)
        if ct in ("dialogue", "crisis"):
            score += 30
        if score < 1:
            continue
        ranked.append((score, seg_no))
    ranked.sort(key=lambda x: -x[0])
    max_ui = max(1, int(n * 0.30))
    return [seg for _, seg in ranked[:max_ui]]


def plan_video_material_slots(
    raw_segments: List[Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """
    为整条视频规划每段素材类型，保证角色存在感 + 场景为主节奏。

    返回 segmentNo -> { slotType, contentType, reason }
    """
    items = sorted(raw_segments, key=lambda x: _seg_key(x, 0))
    n = len(items)
    if n == 0:
        return {}

    min_char = min(MAX_CHARACTER_SLOTS, max(MIN_CHARACTER_SLOTS, 2 if n >= 4 else 1))
    max_char = max(min_char, min(MAX_CHARACTER_SLOTS, max(2, round(n * TARGET_CHARACTER_RATIO))))

    char_segs = set(_pick_character_indices(items, min_slots=min_char, max_slots=max_char))
    ui_segs = set(_pick_ui_indices(items, char_segs))

    plan: Dict[int, Dict[str, Any]] = {}

    for i, item in enumerate(items):
        seg_no = _seg_key(item, i + 1)
        text = item.get("text") or ""
        emotion = item.get("emotion") or ""
        content_type = classify_segment_content(
            text,
            emotion=emotion,
            segment_no=seg_no,
            total_segments=n,
        )
        scene_intent = normalize_scene_intent(
            item.get("sceneIntent"),
            text,
            emotion=emotion,
            segment_no=seg_no,
            total_segments=n,
        )

        if seg_no in char_segs:
            slot: SlotType = "character"
            reason = "视频节奏：固定角色IP镜头"
        elif seg_no in ui_segs:
            slot = "effects" if scene_intent == "collapse" else "ui"
            reason = f"视频节奏：{scene_intent} 界面/告警镜头"
        elif scene_intent == "collapse":
            slot = "effects"
            reason = "语义：系统崩溃/报警"
        elif scene_intent == "work_pressure":
            slot = "ui"
            reason = "语义：工作压力/催办消息"
        elif scene_intent in ("opening", "fatigue", "emotion", "daily_life"):
            slot = "scene"
            reason = f"语义：{scene_intent} 氛围场景"
        elif scene_intent == "communication":
            slot = "ui" if seg_no in ui_segs else "scene"
            reason = "语义：沟通协作"
        elif i == 0:
            slot = "scene"
            reason = "视频节奏：开场场景"
        else:
            slot = "scene"
            reason = "视频节奏：默认场景"

        plan[seg_no] = {
            "slotType": slot,
            "contentType": content_type,
            "sceneIntent": scene_intent,
            "reason": reason,
        }

    # 统计校验
    types = [plan[_seg_key(it, i + 1)]["slotType"] for i, it in enumerate(items)]
    char_count = sum(1 for t in types if t == "character")
    scene_count = sum(1 for t in types if t == "scene")
    ui_count = sum(1 for t in types if t in ("ui", "effects"))
    logger.info(
        "[视频节奏] segments=%s character=%s scene=%s ui/effect=%s plan=%s",
        n,
        char_count,
        scene_count,
        ui_count,
        {k: v["slotType"] for k, v in plan.items()},
    )
    return plan


def slot_to_prefer_types(slot: SlotType) -> List[str]:
    if slot == "character":
        return ["character"]
    if slot == "ui":
        return ["ui", "props"]
    if slot == "effects":
        return ["effects", "ui"]
    return ["scene"]
