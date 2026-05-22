"""
Xiaohongshu note images via Jimeng (R7).

Saves under ``generated/xiaohongshu/`` and returns public paths ``/generated/xiaohongshu/...``.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import List

from app.ai_short_drama.jimeng_image_provider import (
    ImageGenerationError,
    _generate_jimeng_openai,
)
from app.config import settings

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_OUTPUT_DIR = _BACKEND_ROOT / "generated" / "xiaohongshu"
_URL_PREFIX = "/generated/xiaohongshu"

# 小红书笔记常见 3:4 竖图（即梦 size 参数字符串）
XIAOHONGSHU_IMAGE_SIZE = "1080x1440"

XIAOHONGSHU_STYLE_HINT = (
    "小红书笔记配图，清新写实或轻插画，竖版3:4构图，主体清晰，"
    "适合信息流封面，无文字无水印，生活感"
)


def ensure_output_dir() -> Path:
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return _OUTPUT_DIR


async def _generate_one(prompt: str, index: int) -> str:
    text = (prompt or "").strip()
    if not text:
        return ""
    full_prompt = f"{text}。{XIAOHONGSHU_STYLE_HINT}"
    result = await asyncio.wait_for(
        _generate_jimeng_openai(full_prompt, XIAOHONGSHU_IMAGE_SIZE),
        timeout=float(settings.jimeng_timeout_seconds),
    )
    out_dir = ensure_output_dir()
    filename = f"{uuid.uuid4().hex}_{index}.png"
    path = out_dir / filename
    path.write_bytes(result.data)
    url = f"{_URL_PREFIX}/{filename}"
    logger.info(
        "xiaohongshu_image saved=%s bytes=%s provider=%s",
        url,
        len(result.data),
        result.provider,
    )
    return url


async def generate_xiaohongshu_images(
    prompts: List[str],
    *,
    max_parallel: int = 2,
) -> List[str]:
    """
    Generate one image per prompt (same order). Failed slots are empty strings.
    """
    if not settings.jimeng_api_key.strip():
        logger.info("xiaohongshu_image skip: no JIMENG_API_KEY")
        return []

    if not prompts:
        return []

    sem = asyncio.Semaphore(max(1, min(4, max_parallel)))
    results: List[str] = [""] * len(prompts)

    async def _run_at(pos: int, prompt: str) -> None:
        if not prompt:
            return
        async with sem:
            try:
                results[pos] = await _generate_one(prompt, pos)
            except ImageGenerationError as err:
                logger.warning("xiaohongshu_image failed pos=%s err=%s", pos, err)
            except Exception:
                logger.exception("xiaohongshu_image failed pos=%s", pos)

    await asyncio.gather(
        *[_run_at(i, (p or "").strip()) for i, p in enumerate(prompts)]
    )
    return results
