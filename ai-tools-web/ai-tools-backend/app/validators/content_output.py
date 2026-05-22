"""
Rule-based sanitization for xiaohongshu agent results (R5).

Uses ``app.skills.content_compliance.code`` as single source of truth (R6).
"""

from __future__ import annotations

import logging
from typing import List

from app.schemas import XiaohongshuAgentData
from app.skills.content_compliance.code import (
    DEFAULT_PUBLISH_TIPS,
    DEFAULT_RISKS,
    contains_sensitive,
    normalize_whitespace,
    strip_sensitive_phrases,
)

logger = logging.getLogger(__name__)

TITLE_MAX_LEN = 30
CONTENT_MAX_LEN = 1200
IMAGE_PROMPT_MAX_LEN = 500
LIST_ITEM_MAX_LEN = 120


def _sanitize_string_list(
    items: List[str],
    *,
    max_items: int,
    item_max_len: int,
    drop_sensitive: bool,
) -> tuple[List[str], List[str]]:
    fixes: List[str] = []
    seen: set[str] = set()
    out: List[str] = []
    for raw in items or []:
        line = normalize_whitespace(str(raw), item_max_len)
        if not line or line in seen:
            continue
        if drop_sensitive and contains_sensitive(line):
            fixes.append(f"dropped_sensitive:{line[:24]}")
            continue
        seen.add(line)
        out.append(line)
        if len(out) >= max_items:
            break
    return out, fixes


def validate_xiaohongshu_output(
    data: XiaohongshuAgentData,
    expected_count: int,
) -> tuple[XiaohongshuAgentData, List[str]]:
    """
    Sanitize model output in-place semantics; returns (new_data, fix_descriptions for logs).
    """
    fixes: List[str] = []
    count = max(1, min(10, int(expected_count)))

    titles, title_fixes = _sanitize_string_list(
        data.titles,
        max_items=count,
        item_max_len=TITLE_MAX_LEN,
        drop_sensitive=True,
    )
    fixes.extend(title_fixes)
    if not titles and data.titles:
        fixes.append("all_titles_removed_by_rules")

    content = normalize_whitespace(data.content, CONTENT_MAX_LEN)
    if content and contains_sensitive(content):
        content = strip_sensitive_phrases(content, max_len=CONTENT_MAX_LEN)
        fixes.append("content_stripped_sensitive")

    image_prompts, img_fixes = _sanitize_string_list(
        data.image_prompts,
        max_items=count,
        item_max_len=IMAGE_PROMPT_MAX_LEN,
        drop_sensitive=False,
    )
    fixes.extend(img_fixes)

    publish_tips, tip_fixes = _sanitize_string_list(
        data.publish_tips,
        max_items=5,
        item_max_len=LIST_ITEM_MAX_LEN,
        drop_sensitive=False,
    )
    fixes.extend(tip_fixes)
    if not publish_tips:
        publish_tips = list(DEFAULT_PUBLISH_TIPS)
        fixes.append("default_publish_tips")

    risks, risk_fixes = _sanitize_string_list(
        data.risks,
        max_items=5,
        item_max_len=LIST_ITEM_MAX_LEN,
        drop_sensitive=False,
    )
    fixes.extend(risk_fixes)
    if not risks:
        risks = list(DEFAULT_RISKS)
        fixes.append("default_risks")

    if content and len(content) < 80:
        fixes.append("content_short")

    sanitized = XiaohongshuAgentData(
        titles=titles,
        content=content,
        image_prompts=image_prompts,
        publish_tips=publish_tips,
        risks=risks,
    )
    if fixes:
        logger.info("xiaohongshu_validator fixes=%s", ",".join(fixes))
    return sanitized, fixes
