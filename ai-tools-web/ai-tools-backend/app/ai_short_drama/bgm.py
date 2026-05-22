from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai_short_drama.audio_export import BGM_FADE_OUT_SEC, BGM_VOLUME_DEFAULT
from app.ai_short_drama.material_infer import EMOTION_CN_TO_KEY

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_PUBLIC = BACKEND_ROOT.parent / "ai-tools-frontend" / "public"
BGM_DIR = FRONTEND_PUBLIC / "short-drama" / "bgm"

# 用户曲目（public/short-drama/bgm/）
BGM_PIANO = "atlasaudio-emotional-piano-510218.mp3"
BGM_AMBIENT = "atlasaudio-ambient-519913.mp3"
BGM_LOFI = "mondamusic-lofi-lofi-girl-lofi-music-529555.mp3"

DEFAULT_BGM = BGM_PIANO

# 情绪风格（中文）→ BGM
EMOTION_STYLE_CN_TO_BGM: Dict[str, str] = {
    "扎心": BGM_PIANO,
    "压抑": BGM_AMBIENT,
    "疲惫": BGM_LOFI,
    "真实": BGM_PIANO,
    "搞笑": BGM_LOFI,
    "反转": BGM_LOFI,
}

# 段落情绪（英文枚举）→ BGM
SEGMENT_EMOTION_TO_BGM: Dict[str, str] = {
    "tired": BGM_LOFI,
    "stressed": BGM_AMBIENT,
    "calm": BGM_PIANO,
    "normal": BGM_PIANO,
    "happy": BGM_LOFI,
    "confused": BGM_LOFI,
    "shocked": BGM_AMBIENT,
    "angry": BGM_AMBIENT,
}

SEGMENT_EMOTION_CN_TO_BGM: Dict[str, str] = {
    "疲惫": BGM_LOFI,
    "累": BGM_LOFI,
    "紧张": BGM_AMBIENT,
    "压力": BGM_AMBIENT,
    "压抑": BGM_AMBIENT,
    "平静": BGM_PIANO,
    "冷静": BGM_PIANO,
    "开心": BGM_LOFI,
    "震惊": BGM_AMBIENT,
    "愤怒": BGM_AMBIENT,
    "真实": BGM_PIANO,
    "扎心": BGM_PIANO,
    "搞笑": BGM_LOFI,
}

BGM_CATALOG: List[Dict[str, str]] = [
    {
        "file": BGM_PIANO,
        "label": "Emotional Piano · 扎心/真实",
        "mood": "扎心",
    },
    {
        "file": BGM_AMBIENT,
        "label": "Ambient · 压抑/紧张",
        "mood": "压抑",
    },
    {
        "file": BGM_LOFI,
        "label": "Lo-fi · 疲惫/搞笑/反转",
        "mood": "疲惫",
    },
]


def list_bgm_files() -> List[str]:
    if not BGM_DIR.is_dir():
        return [t["file"] for t in BGM_CATALOG]
    found = sorted(p.name for p in BGM_DIR.glob("*.mp3"))
    return found or [t["file"] for t in BGM_CATALOG]


def resolve_bgm_path(filename: str) -> Optional[Path]:
    name = (filename or "").strip()
    if not name:
        return None
    if "/" in name or "\\" in name:
        return None
    path = BGM_DIR / name
    if path.is_file():
        return path
    logger.warning("[bgm] file missing: %s", path)
    return None


def _first_available_bgm() -> Optional[str]:
    files = list_bgm_files()
    return files[0] if files else None


def _emotion_to_bgm(emotion: str) -> Optional[str]:
    em = (emotion or "").strip()
    if not em:
        return None
    low = em.lower()
    if low in SEGMENT_EMOTION_TO_BGM:
        return SEGMENT_EMOTION_TO_BGM[low]
    if em in SEGMENT_EMOTION_CN_TO_BGM:
        return SEGMENT_EMOTION_CN_TO_BGM[em]
    key = EMOTION_CN_TO_KEY.get(em)
    if key and key in SEGMENT_EMOTION_TO_BGM:
        return SEGMENT_EMOTION_TO_BGM[key]
    return None


def pick_bgm_from_segments(segments: List[Dict[str, Any]]) -> str:
    votes: Counter[str] = Counter()
    for seg in segments:
        bgm = _emotion_to_bgm(str(seg.get("emotion") or ""))
        if bgm:
            votes[bgm] += 1
    if votes:
        chosen = votes.most_common(1)[0][0]
        if resolve_bgm_path(chosen):
            return chosen
    fallback = _first_available_bgm()
    return fallback or DEFAULT_BGM


def pick_bgm_filename(
    *,
    bgm_mode: str,
    bgm_file: Optional[str],
    emotion_style: Optional[str],
    segments: Optional[List[Dict[str, Any]]] = None,
) -> Optional[str]:
    mode = (bgm_mode or "auto").strip().lower()
    if mode == "none":
        return None
    if mode == "manual":
        name = (bgm_file or "").strip()
        if name and resolve_bgm_path(name):
            return name
        return _first_available_bgm()
    style = (emotion_style or "").strip()
    if style and style in EMOTION_STYLE_CN_TO_BGM:
        candidate = EMOTION_STYLE_CN_TO_BGM[style]
        if resolve_bgm_path(candidate):
            return candidate
    if segments:
        return pick_bgm_from_segments(segments)
    if resolve_bgm_path(DEFAULT_BGM):
        return DEFAULT_BGM
    return _first_available_bgm()


def pick_bgm_path(
    *,
    bgm_mode: str,
    bgm_file: Optional[str],
    emotion_style: Optional[str],
    segments: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Path]:
    filename = pick_bgm_filename(
        bgm_mode=bgm_mode,
        bgm_file=bgm_file,
        emotion_style=emotion_style,
        segments=segments,
    )
    if not filename:
        return None
    path = resolve_bgm_path(filename)
    if path:
        return path
    for name in list_bgm_files():
        path = resolve_bgm_path(name)
        if path:
            logger.info("[bgm] fallback to available file %s", name)
            return path
    return None
