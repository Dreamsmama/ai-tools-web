"""朗读时长估算，供 TTS 校验与视频对齐共用。"""
from __future__ import annotations

import re

# 实测 CosyVoice 对「很多人觉得：」等短开口会返回 20s+ 异常 MP3
TTS_DURATION_MAX_RATIO = 2.2


def estimate_speech_seconds(text: str) -> float:
    """按字数估算中文朗读时长（秒）。"""
    t = re.sub(r"\s+", "", (text or "").strip())
    if not t:
        return 2.0
    return max(2.0, min(50.0, len(t) / 3.8 + 0.6))


def is_plausible_tts_duration(text: str, seconds: float, *, ratio: float = TTS_DURATION_MAX_RATIO) -> bool:
    est = estimate_speech_seconds(text)
    return seconds <= est * ratio + 0.5
