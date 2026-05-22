from __future__ import annotations

import asyncio
import base64
import json
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

JIMENG_IMAGE_PATH = "/images/generations"

DEFAULT_STYLE_HINT = (
    "国产互联网动画感，半写实，蓝灰生活情绪氛围，轻电影感，"
    "9:16 vertical composition，portrait mobile video，"
    "竖屏中景中心构图，上下留白字幕区，生活感瞬间非职业PPT，"
    "禁止工位壁纸、禁止显示器占满画面、禁止横向会议室全景，无文字水印"
)

CHARACTER_STYLE_HINT = (
    "国产互联网动画感，半写实，职场角色设定图，竖构图，人物清晰，无文字水印"
)


class ImageGenerationError(RuntimeError):
    pass


@dataclass
class ImageGenerateResult:
    data: bytes
    provider: str
    image_url: str = ""
    prompt: str = ""


async def _download_bytes(url: str) -> bytes:
    timeout = httpx.Timeout(60.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def _build_jimeng_url() -> tuple[str, str, str]:
    """返回 (baseUrl, path, finalUrl)。"""
    base_url = settings.jimeng_api_base_url.rstrip("/")
    path = JIMENG_IMAGE_PATH
    final_url = f"{base_url}{path}"
    return base_url, path, final_url


async def _generate_jimeng_openai(prompt: str, size: str) -> ImageGenerateResult:
    api_key = settings.jimeng_api_key.strip()
    model = settings.jimeng_model.strip()
    if not api_key:
        raise ImageGenerationError("缺少 JIMENG_API_KEY")
    if not model:
        raise ImageGenerationError("缺少 JIMENG_MODEL")

    base_url, path, final_url = _build_jimeng_url()

    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "watermark": False,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    logger.info(
        "[即梦] 请求准备 baseUrl=%s path=%s finalUrl=%s model=%s prompt=%s",
        base_url,
        path,
        final_url,
        model,
        prompt[:500],
    )

    timeout = httpx.Timeout(60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(final_url, json=payload, headers=headers)
        body_text = resp.text
        logger.info(
            "[即梦] 响应 status=%s body=%s",
            resp.status_code,
            body_text[:2000],
        )
        if resp.status_code >= 400:
            raise ImageGenerationError(
                f"即梦图片生成失败 HTTP {resp.status_code}: {body_text[:500]}"
            )
        try:
            body = resp.json()
        except json.JSONDecodeError as err:
            raise ImageGenerationError(
                f"即梦返回非 JSON：{body_text[:300]}"
            ) from err

    data = body.get("data") or []
    if not data:
        raise ImageGenerationError(
            f"即梦返回无图片：{json.dumps(body, ensure_ascii=False)[:300]}"
        )

    item = data[0]
    image_url = str(item.get("url") or "")
    if item.get("b64_json"):
        raw = base64.b64decode(item["b64_json"])
        return ImageGenerateResult(
            data=raw, provider="jimeng", image_url=image_url or "(b64)", prompt=prompt
        )
    if image_url:
        raw = await _download_bytes(image_url)
        return ImageGenerateResult(
            data=raw, provider="jimeng", image_url=image_url, prompt=prompt
        )
    raise ImageGenerationError(
        f"即梦返回结构无法解析：{json.dumps(body, ensure_ascii=False)[:300]}"
    )


AI_IMAGE_TIMEOUT_SECONDS = 60.0
AI_IMAGE_FAILED_MSG = "AI图片生成失败"


async def generate_dynamic_image(
    prompt: str,
    *,
    size: Optional[str] = None,
    for_character: bool = False,
) -> ImageGenerateResult:
    """仅使用即梦生成；失败时返回明确错误（暂不启用万相回退）。"""
    style_hint = CHARACTER_STYLE_HINT if for_character else DEFAULT_STYLE_HINT
    full_prompt = f"{prompt.strip()}。{style_hint}"
    img_size = size or settings.jimeng_image_size
    if not for_character and img_size != "1080x1920":
        img_size = "1080x1920"

    if not settings.jimeng_api_key.strip():
        raise ImageGenerationError("未配置 JIMENG_API_KEY，无法生成图片")

    try:
        result = await asyncio.wait_for(
            _generate_jimeng_openai(full_prompt, img_size),
            timeout=AI_IMAGE_TIMEOUT_SECONDS,
        )
        logger.info(
            "[AI生成] provider=%s 成功=True image_url=%s bytes=%s",
            result.provider,
            result.image_url[:120] if result.image_url else "",
            len(result.data),
        )
        return result
    except asyncio.TimeoutError:
        logger.error("[即梦] 生成超时（%ss）", AI_IMAGE_TIMEOUT_SECONDS)
        raise ImageGenerationError(AI_IMAGE_FAILED_MSG)
    except ImageGenerationError:
        raise
    except httpx.HTTPError as err:
        logger.exception("[即梦] HTTP 请求异常")
        raise ImageGenerationError(f"即梦图片生成请求失败：{err}") from err
    except Exception as err:
        logger.exception("[即梦] 未知异常")
        raise ImageGenerationError(f"即梦图片生成失败：{err}") from err
