from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import uuid
from pathlib import Path, PurePosixPath
from typing import Literal

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

_ARK_EDIT_PATH = "/images/generations"

# 发型风格 → 编辑 Prompt（简洁但包含发型视觉特征描述）
_STYLE_PROMPTS: dict[str, str] = {
    # 男生
    "韩系碎盖": "将图中人物发型更改为韩系碎盖短发，刘海盖住额头、发尾碎层次感、两侧清爽贴头，只改发型其他不变",
    "清爽短发": "将图中人物发型更改为清爽男生短发，两侧推短、顶部短而有层次，只改发型其他不变",
    "三七分": "将图中人物发型更改为三七分偏分发型，头发向一侧梳理、露出额头、整齐干练，只改发型其他不变",
    "寸头": "将图中人物发型更改为寸头，头发极短约1厘米、贴合头皮、露出完整头型，只改发型其他不变",
    "商务背头": "将图中人物发型更改为商务背头，头发全部向后梳理、前额露出、发丝整齐有光泽，只改发型其他不变",
    "微分碎盖": "将图中人物发型更改为微分碎盖，刘海从中间微微分开、两边碎发自然垂落遮住额头、蓬松感强，只改发型其他不变",
    # 女生
    "锁骨发": "将图中人物发型更改为锁骨发，头发长度到锁骨位置、发尾轻微内扣、中分或偏分，只改发型其他不变",
    "空气刘海": "将图中人物发型更改为空气刘海，额前刘海轻薄透光、能看到额头、自然弧度，只改发型其他不变",
    "法式短发": "将图中人物发型更改为法式短发，头发到下巴长度、外翻卷翘、慵懒随性，只改发型其他不变",
    "韩系长卷发": "将图中人物发型更改为韩系长卷发，长发大波浪卷、卷度自然柔和、有空气感，只改发型其他不变",
    "高层次长发": "将图中人物发型更改为高层次长发，头发有明显层次、发尾轻盈、有流动感，只改发型其他不变",
    "温柔短发": "将图中人物发型更改为温柔短发，耳下短发、层次柔和贴脸、清爽减龄，只改发型其他不变",
}

# 发型风格 → AI 建议文案
_STYLE_SUGGESTIONS: dict[str, str] = {
    "韩系碎盖": "韩系碎盖让整体气质更年轻清爽，适合想提升精神感和形象辨识度的场景。",
    "清爽短发": "清爽短发给人干净利落的第一印象，适合日常通勤和职场场合。",
    "三七分": "三七分成熟干练，适合想展现稳重气质的职场或社交场合。",
    "寸头": "寸头线条简洁、精神感强，适合想让五官更立体的人群。",
    "商务背头": "商务背头气场十足，适合正式场合或想展现领导力的场景。",
    "微分碎盖": "微分碎盖兼具清新感与个性，日常搭配感强，不挑场合。",
    "锁骨发": "锁骨发温柔优雅，能很好地修饰脸型，日常和正式场合都适合。",
    "空气刘海": "空气刘海轻盈减龄，适合想遮掩额头或提升甜美感的人群。",
    "法式短发": "法式短发个性干练，适合想打造独特气质和时尚感的场景。",
    "韩系长卷发": "韩系长卷发增添浪漫女性气息，适合约会或想展现柔美一面的场合。",
    "高层次长发": "高层次长发轻盈飘逸，视觉上让人更高挑，日常通用度很高。",
    "温柔短发": "温柔短发清爽又减龄，打理方便，适合追求简单精致生活的人群。",
}

# 核心身份保留约束（所有 beautyLevel 共用）——保持简洁
_PRESERVE_BASE = ""

# 各美化强度追加指令——尽量简短，避免干扰模型对原图的保持
_BEAUTY_INSTRUCTIONS: dict[str, str] = {
    "natural": "",
    "light": "",
    "upgrade": "，同时轻微提升整体精神感和气质",
}

# 各美化强度对应的建议文案前缀
_BEAUTY_SUGGESTIONS: dict[str, str] = {
    "natural": "这个结果更接近真实剪发效果，适合想保守参考发型的人。",
    "light": "这个结果在保留本人特征的基础上做了轻微美化，看起来会更清爽自然。",
    "upgrade": "这个结果更偏整体形象提升，适合想尝试更明显风格变化的人。",
}

_VALID_BEAUTY_LEVELS = frozenset({"natural", "light", "upgrade"})

_EXT_CONTENT_TYPE: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


_MAX_ARK_IMAGE_BYTES = 4 * 1024 * 1024  # 压缩目标：4MB 以内（base64 后约 5.3MB）


def _compress_image(image_bytes: bytes, max_bytes: int = _MAX_ARK_IMAGE_BYTES) -> tuple[bytes, str]:
    """将图片压缩为 JPEG 格式，确保不超过 max_bytes。返回 (压缩后bytes, content_type)。"""
    if len(image_bytes) <= max_bytes:
        # 小图片尝试检测是否已经是 JPEG
        if image_bytes[:2] == b'\xff\xd8':
            return image_bytes, "image/jpeg"

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    quality = 85
    while quality >= 30:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        result = buf.getvalue()
        if len(result) <= max_bytes:
            return result, "image/jpeg"
        quality -= 10

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=30)
    return buf.getvalue(), "image/jpeg"


def _build_prompt(style: str, beauty_level: str) -> str:
    style_desc = _STYLE_PROMPTS.get(
        style, f"将图中人物发型更改为{style}，其他所有内容保持不变"
    )
    beauty_instruction = _BEAUTY_INSTRUCTIONS.get(
        beauty_level, _BEAUTY_INSTRUCTIONS["natural"]
    )
    return f"{style_desc}{beauty_instruction}"


def _get_generated_dir() -> Path:
    backend_root = Path(__file__).resolve().parent.parent.parent
    out_dir = backend_root / "generated" / "hairstyle"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


async def _download_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0), follow_redirects=True
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def _pick_output_size(image_bytes: bytes) -> str:
    """根据原图宽高比选择合适的 ARK 输出尺寸（使用官方支持的 2K 分辨率）。"""
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    ratio = w / h

    if ratio >= 1.3:
        return "2848x1600"  # 横图 16:9 (2K)
    elif ratio >= 0.9:
        return "2048x2048"  # 方图 1:1 (2K)
    elif ratio >= 0.7:
        return "1728x2304"  # 竖图 3:4 (2K)
    else:
        return "1600x2848"  # 长竖图 9:16 (2K)


async def _call_ark_image_edit(
    image_bytes: bytes,
    image_filename: str,
    prompt: str,
    model: str,
) -> tuple[bytes, str | None]:
    """
    调用火山方舟图生图接口（/api/v3/images/generations）。
    使用 JSON body，图片通过 base64 data URI 传递。
    """
    api_key = settings.jimeng_api_key.strip()
    base_url = settings.jimeng_api_base_url.rstrip("/")
    final_url = f"{base_url}{_ARK_EDIT_PATH}"

    output_size = _pick_output_size(image_bytes)
    compressed_bytes, file_ct = _compress_image(image_bytes)
    image_b64 = base64.b64encode(compressed_bytes).decode("utf-8")
    image_data_uri = f"data:{file_ct};base64,{image_b64}"

    logger.info(
        "[换发型] ARK 图生图请求 url=%s model=%s size=%s prompt=%.80s",
        final_url,
        model,
        output_size,
        prompt,
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "image": image_data_uri,
        "size": output_size,
        "response_format": "url",
        "watermark": False,
    }

    timeout = httpx.Timeout(settings.hairstyle_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            final_url, headers=headers, json=payload
        )
        body_text = resp.text
        logger.info(
            "[换发型] ARK 响应 status=%s body=%.600s",
            resp.status_code,
            body_text,
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"ARK 图生图失败 HTTP {resp.status_code}: {body_text[:400]}"
            )
        try:
            body = resp.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"ARK 返回非 JSON：{body_text[:200]}"
            ) from exc

    data_list = body.get("data") or []
    if not data_list:
        raise RuntimeError(
            f"ARK 返回无图片数据：{json.dumps(body, ensure_ascii=False)[:200]}"
        )

    item = data_list[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"]), None
    url = str(item.get("url") or "")
    if url:
        img_bytes = await _download_bytes(url)
        return img_bytes, url
    raise RuntimeError(
        f"ARK 返回结构无法解析：{json.dumps(body, ensure_ascii=False)[:200]}"
    )


class HairstyleResult:
    __slots__ = ("result_image_url", "suggestion")

    def __init__(self, result_image_url: str, suggestion: str) -> None:
        self.result_image_url = result_image_url
        self.suggestion = suggestion


async def generate_hairstyle(
    image_bytes: bytes,
    image_filename: str,
    style: str,
    gender: Literal["male", "female"],
    beauty_level: str = "light",
) -> HairstyleResult:
    model = (settings.hairstyle_model or settings.jimeng_model).strip()
    if not model:
        raise ValueError("未配置模型：请在 .env 中设置 HAIRSTYLE_MODEL 或 JIMENG_MODEL")
    if not settings.jimeng_api_key.strip():
        raise ValueError("未配置 JIMENG_API_KEY，无法调用 ARK 图片编辑接口")

    # 防御：beauty_level 不合法时回退到 light
    if beauty_level not in _VALID_BEAUTY_LEVELS:
        beauty_level = "light"

    prompt = _build_prompt(style, beauty_level)

    try:
        img_bytes, cloud_url = await asyncio.wait_for(
            _call_ark_image_edit(image_bytes, image_filename, prompt, model),
            timeout=settings.hairstyle_timeout_seconds,
        )
    except asyncio.TimeoutError:
        logger.error("[换发型] 生成超时（%.0fs）", settings.hairstyle_timeout_seconds)
        raise RuntimeError("生成超时，请稍后重试")

    generated_dir = _get_generated_dir()
    out_name = f"{uuid.uuid4().hex}.jpg"
    out_path = generated_dir / out_name
    out_path.write_bytes(img_bytes)
    logger.info(
        "[换发型] 生成完成 style=%s gender=%s beauty_level=%s path=%s bytes=%d",
        style,
        gender,
        beauty_level,
        out_path,
        len(img_bytes),
    )

    result_url = cloud_url if cloud_url else f"/generated/hairstyle/{out_name}"
    style_suggestion = _STYLE_SUGGESTIONS.get(
        style, "这个发型会让整体气质更清爽，适合想提升精神感和形象辨识度的场景。"
    )
    beauty_suggestion = _BEAUTY_SUGGESTIONS.get(beauty_level, _BEAUTY_SUGGESTIONS["light"])
    suggestion = f"{beauty_suggestion}{style_suggestion}"
    return HairstyleResult(result_image_url=result_url, suggestion=suggestion)
