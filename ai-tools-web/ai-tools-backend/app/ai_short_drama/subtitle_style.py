from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

# 竖屏 1080x1920 短视频字幕参数
SUBTITLE_FONT_SIZE = 78
SUBTITLE_LINE_SPACING = 16
SUBTITLE_MAX_CHARS_PER_LINE = 14
SUBTITLE_MAX_LINES = 3
SUBTITLE_MAX_TOTAL_CHARS = 60
# 文字块中心约在画面 62% 高度（下方 1/3 区域内）
SUBTITLE_Y_EXPR = "h*0.62-text_h/2"
SUBTITLE_BOX_COLOR = "black@0.45"
SUBTITLE_BOX_BORDER = 28
SUBTITLE_MIN_DURATION = 2
SUBTITLE_MAX_DURATION = 6

# (fontfile, fontindex) — fontindex 用于 .ttc 粗体/半粗
FONT_CANDIDATES: List[Tuple[str, Optional[int]]] = [
    ("/System/Library/Fonts/PingFang.ttc", 2),  # PingFang SC Semibold
    ("/System/Library/Fonts/STHeiti Medium.ttc", None),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2),
    ("/Library/Fonts/Arial Unicode.ttf", None),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", None),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", None),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-SemiBold.ttc", None),
    ("/System/Library/Fonts/PingFang.ttc", 1),
    ("/System/Library/Fonts/STHeiti Light.ttc", None),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", None),
]

_BREAK_AFTER = frozenset("，。！？、：；…」』")


def pick_bold_font() -> Tuple[Optional[str], Optional[int]]:
    for path, index in FONT_CANDIDATES:
        if Path(path).is_file():
            return path, index
    return None, None


def wrap_subtitle_lines(text: str) -> str:
    """限制单行宽度，自动换行（最多 SUBTITLE_MAX_LINES 行）。"""
    raw = (text or "").strip()[:SUBTITLE_MAX_TOTAL_CHARS]
    if not raw:
        return "……"

    lines_out: List[str] = []
    for paragraph in raw.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= SUBTITLE_MAX_CHARS_PER_LINE:
            lines_out.append(paragraph)
            continue

        buf = ""
        for ch in paragraph:
            buf += ch
            if len(buf) >= SUBTITLE_MAX_CHARS_PER_LINE:
                if ch in _BREAK_AFTER:
                    lines_out.append(buf.strip())
                    buf = ""
                elif len(buf) >= SUBTITLE_MAX_CHARS_PER_LINE + 2:
                    lines_out.append(buf.strip())
                    buf = ""

        if buf.strip():
            lines_out.append(buf.strip())

    if not lines_out:
        return raw[:SUBTITLE_MAX_CHARS_PER_LINE]
    return "\n".join(lines_out[:SUBTITLE_MAX_LINES])


def split_subtitle_phrases(text: str) -> List[str]:
    """
    拆成逐句显示用的短语列表。
    优先按换行；否则按句号/问号等拆分，避免一整段挤在一条字幕里。
    """
    raw = (text or "").strip()
    if not raw:
        return ["……"]

    if "\n" in raw:
        parts = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if parts:
            return parts

    # 「很多人觉得：」「开发会说：」类 — 冒号后换句
    if "：" in raw:
        colon_parts = [p.strip() for p in re.split(r"(?<=[：])", raw) if p.strip()]
        if len(colon_parts) > 1:
            return colon_parts

    # 按标点拆句，保留标点
    chunks = re.split(r"([。！？；])", raw)
    phrases: List[str] = []
    buf = ""
    for chunk in chunks:
        if not chunk:
            continue
        buf += chunk
        if chunk in "。！？；" or len(buf) >= 18:
            phrase = buf.strip()
            if phrase:
                phrases.append(phrase)
            buf = ""
    if buf.strip():
        phrases.append(buf.strip())

    if not phrases:
        return [raw]
    if len(phrases) == 1 and len(phrases[0]) > SUBTITLE_MAX_CHARS_PER_LINE:
        return wrap_subtitle_lines(phrases[0]).splitlines() or phrases
    return phrases


def phrase_duration_seconds(phrase_count: int, segment_duration: int) -> int:
    """每句 2~4 秒；多句时平分原段落时长。"""
    base = max(SUBTITLE_MIN_DURATION, min(SUBTITLE_MAX_DURATION, int(segment_duration)))
    if phrase_count <= 1:
        return base
    per = max(SUBTITLE_MIN_DURATION, min(SUBTITLE_MAX_DURATION, int(segment_duration) // phrase_count))
    return max(SUBTITLE_MIN_DURATION, min(SUBTITLE_MAX_DURATION, per))


def build_drawtext_filter(text_file: Path, *, font_path: str, font_index: Optional[int]) -> str:
    font_esc = font_path.replace("'", "'\\''")
    text_esc = str(text_file).replace("'", "'\\''")
    font_part = f"fontfile='{font_esc}'"
    if font_index is not None:
        font_part += f":fontindex={font_index}"
    return (
        f"drawtext={font_part}:textfile='{text_esc}':"
        f"fontsize={SUBTITLE_FONT_SIZE}:fontcolor=white:"
        f"line_spacing={SUBTITLE_LINE_SPACING}:"
        f"borderw=0:"
        f"box=1:boxcolor={SUBTITLE_BOX_COLOR}:boxborderw={SUBTITLE_BOX_BORDER}:"
        f"x=(w-text_w)/2:y={SUBTITLE_Y_EXPR}"
    )
