from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Tuple

RhythmKind = Literal["short", "normal", "emotional", "strong"]

_EMOTIONAL_EMOTIONS = frozenset(
    {"tired", "stressed", "angry", "shocked", "sad", "confused", "疲惫", "压抑", "崩溃"}
)

_STRONG_KEYWORDS = (
    "不是因为",
    "而是长期",
    "不是因为不",
    "长期被",
    "再也不",
    "并非不爱",
    "并非不热爱",
    "并非不热爱工作",
    "并非不热爱产品",
)

_EMOTIONAL_KEYWORDS = (
    "疲惫",
    "累",
    "压力",
    "崩溃",
    "委屈",
    "孤独",
    "越来越",
    "难受",
    "背锅",
    "拉扯",
    "熬",
    "失眠",
    "焦虑",
    "窒息",
    "麻木",
)

_SHORT_SUFFIX = re.compile(r"[：:]\s*$")
_SHORT_LEADERS = (
    "很多人觉得",
    "而是",
    "开发会说",
    "老板会说",
    "运营会说",
    "测试会说",
    "HR会说",
    "销售会说",
    "产品经理会说",
)


def classify_segment_rhythm(text: str, emotion: str = "") -> RhythmKind:
    """根据文案句式与情绪标签判定停留节奏类型。"""
    t = (text or "").strip()
    if not t:
        return "short"

    emo = (emotion or "").strip().lower()

    if _SHORT_SUFFIX.search(t) or len(t) <= 8:
        return "short"
    if any(t.startswith(p) for p in _SHORT_LEADERS) and len(t) <= 14:
        return "short"
    if t in ("而是：", "而是:", "很多人觉得："):
        return "short"

    if any(k in t for k in _EMOTIONAL_KEYWORDS) or emo in _EMOTIONAL_EMOTIONS:
        if any(k in t for k in _STRONG_KEYWORDS):
            return "strong"
        return "emotional" if len(t) >= 6 else "normal"
    if any(k in t for k in _STRONG_KEYWORDS):
        return "strong"

    if t.endswith("？") or t.endswith("?"):
        return "emotional"

    return "normal"


def duration_for_rhythm(kind: RhythmKind, text: str = "") -> int:
    """短句 1.5~2s / 普通 2~3s / 情绪 3~4s / 强情绪更久（秒，取整）。"""
    t = (text or "").strip()
    if kind == "short":
        return 2 if len(t) > 6 else 2
    if kind == "normal":
        return 3 if len(t) <= 18 else 3
    if kind == "emotional":
        return 4 if len(t) <= 22 else 4
    # strong
    if len(t) >= 20:
        return 5
    return 4


def apply_auto_rhythm(segments: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """为每段写入 duration / rhythmType，并返回预计成片总秒数。"""
    out: List[Dict[str, Any]] = []
    total = 0
    for seg in segments:
        text = str(seg.get("text") or "").strip()
        emotion = str(seg.get("emotion") or "")
        kind = classify_segment_rhythm(text, emotion)
        dur = duration_for_rhythm(kind, text)
        row = {**seg, "duration": dur, "rhythmType": kind}
        out.append(row)
        total += dur
    return out, total


def total_duration_seconds(segments: List[Dict[str, Any]]) -> int:
    return sum(int(s.get("duration") or 0) for s in segments)
