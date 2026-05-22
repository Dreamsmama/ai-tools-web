from __future__ import annotations

import re
from typing import List

# 单行更像独立镜头：以冒号结尾、引用对话、emoji 引导等
_STANDALONE_LINE = re.compile(
    r"^(?:[\u4e00-\u9fffA-Za-z0-9「『""].{0,36}[：:？?！!…]|👉|💬|📱|⚠️|🔥)"
)


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", (line or "").strip())


def split_script_paragraphs(script: str) -> List[str]:
    """
    规则拆段：空行优先，其次按单行节奏拆分。
    供 AI 失败时兜底，或作为 AI 提示中的段落参考。
    """
    raw = (script or "").strip()
    if not raw:
        return []

    blocks = [b.strip() for b in re.split(r"\n\s*\n+", raw) if b.strip()]
    if not blocks:
        return []

    segments: List[str] = []
    for block in blocks:
        lines = [_normalize_line(ln) for ln in block.splitlines() if _normalize_line(ln)]
        if not lines:
            continue
        if len(lines) == 1:
            segments.append(lines[0])
            continue
        # 多块合并成一段，或按行拆
        if all(_STANDALONE_LINE.match(ln) for ln in lines):
            segments.extend(lines)
        elif len("\n".join(lines)) <= 48:
            segments.append("\n".join(lines))
        else:
            for ln in lines:
                if _STANDALONE_LINE.match(ln) or len(ln) <= 22:
                    segments.append(ln)
                elif segments and len(segments[-1]) + len(ln) <= 40:
                    segments[-1] = f"{segments[-1]}\n{ln}"
                else:
                    segments.append(ln)

    return [s for s in segments if s.strip()]
