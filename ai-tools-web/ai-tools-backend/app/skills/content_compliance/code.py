"""
Deterministic content compliance helpers (shared by validator + agents).
"""

from __future__ import annotations

import re
from typing import List, Sequence, Tuple

# Substrings that often trigger platform / advertising issues (CN).
SENSITIVE_SUBSTRINGS: Tuple[str, ...] = (
    "最好",
    "第一",
    "100%",
    "百分百",
    "绝对",
    "保证赚",
    "稳赚",
    "根治",
    "治愈",
    "国家级",
    "最强",
)

DEFAULT_PUBLISH_TIPS: Tuple[str, ...] = (
    "发布前请核对事实与数据来源",
    "避免绝对化、夸大表述，必要时加体验免责声明",
)

DEFAULT_RISKS: Tuple[str, ...] = (
    "请注意广告法与平台社区规范，避免绝对化用语",
    "涉及医疗、金融、功效类表述需格外谨慎",
)

_WS_RE = re.compile(r"\s+")


def normalize_whitespace(text: str, max_len: int | None = None) -> str:
    t = _WS_RE.sub(" ", (text or "").strip())
    if max_len is not None and len(t) > max_len:
        return t[: max_len - 1] + "…"
    return t


def find_sensitive_hits(text: str) -> List[str]:
    """Return matched sensitive substrings (deduped, stable order)."""
    hits: List[str] = []
    for phrase in SENSITIVE_SUBSTRINGS:
        if phrase in (text or "") and phrase not in hits:
            hits.append(phrase)
    return hits


def contains_sensitive(text: str) -> bool:
    return bool(find_sensitive_hits(text))


def strip_sensitive_phrases(text: str, *, max_len: int = 1200) -> str:
    out = text or ""
    for phrase in SENSITIVE_SUBSTRINGS:
        out = out.replace(phrase, "")
    return normalize_whitespace(out, max_len)


def scan_copywriting(copywriting: dict) -> dict:
    """
    Scan titles + content from copywriter JSON for compliance tooling.

    Returns dict with hits and flags (for logs or prompt hints).
    """
    titles = copywriting.get("titles") if isinstance(copywriting.get("titles"), list) else []
    content = copywriting.get("content") if isinstance(copywriting.get("content"), str) else ""
    title_hits: List[str] = []
    for t in titles:
        title_hits.extend(find_sensitive_hits(str(t)))
    content_hits = find_sensitive_hits(content)
    # dedupe preserve order
    seen: set[str] = set()
    all_hits: List[str] = []
    for h in title_hits + content_hits:
        if h not in seen:
            seen.add(h)
            all_hits.append(h)
    return {
        "sensitive_hits": all_hits,
        "title_has_sensitive": bool(title_hits),
        "content_has_sensitive": bool(content_hits),
    }
