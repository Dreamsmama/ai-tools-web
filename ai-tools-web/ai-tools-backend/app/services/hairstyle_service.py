from __future__ import annotations

import asyncio
import base64
import json
import logging
import uuid
from pathlib import Path, PurePosixPath
from typing import Literal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_ARK_EDIT_PATH = "/images/edits"

# 发型风格 → 编辑 Prompt（指令式，要求只改发型）
_STYLE_PROMPTS: dict[str, str] = {
    # 男生
    "韩系碎盖": "把人物发型改成自然男生韩系碎盖短发，顶部有轻微蓬松感，两侧清爽，整体年轻干净，发丝自然真实。",
    "清爽短发": "把人物发型改成清爽干净的男生短发，两侧修整，顶部轻微有层次，整体精神干净，发丝真实。",
    "三七分": "把人物发型改成自然三七分，成熟干净，发丝层次自然，适合商务场合。",
    "寸头": "把人物发型改成自然真实寸头，保留真实头型与发际线，不要改变脸型。",
    "商务背头": "把人物发型改成成熟商务背头，发丝整齐向后梳理，整体干练有质感。",
    "微分碎盖": "把人物发型改成男生微分碎盖，刘海轻微分开，发丝自然蓬松，清新年轻感。",
    # 女生
    "锁骨发": "把人物发型改成自然锁骨发，发尾轻微内扣，整体温柔自然，发量真实。",
    "空气刘海": "把人物发型改成自然空气刘海，刘海轻盈真实，不要厚重，整体清爽甜美。",
    "法式短发": "把人物发型改成法式短发，层次自然，整体干练有个性，不要过于厚重。",
    "韩系长卷发": "把人物发型改成自然韩系长卷发，卷度柔和，发量真实，整体温柔有女人味。",
    "高层次长发": "把人物发型改成高层次长发，发尾轻盈有流动感，整体自然飘逸。",
    "温柔短发": "把人物发型改成温柔短发，层次柔和，整体清爽减龄，发丝真实自然。",
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

# 固定附加约束：保留人物身份，只改发型
_PRESERVE_INSTRUCTION = (
    "保留人物的脸型、五官、表情、肤色和背景，不要改变人物身份，不要过度美颜，"
    "发际线要自然真实，光影与原图保持一致，不要贴图感，不要明显AI感。"
)

_EXT_CONTENT_TYPE: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _build_prompt(style: str) -> str:
    style_desc = _STYLE_PROMPTS.get(style, f"把人物发型改成{style}，发丝自然真实。")
    return f"{style_desc}{_PRESERVE_INSTRUCTION}"


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


async def _call_ark_image_edit(
    image_bytes: bytes,
    image_filename: str,
    prompt: str,
    model: str,
) -> bytes:
    """
    调用火山方舟 OpenAI 兼容图片编辑接口（/api/v3/images/edits）。
    复用 settings.jimeng_api_key / jimeng_api_base_url 配置。
    """
    api_key = settings.jimeng_api_key.strip()
    base_url = settings.jimeng_api_base_url.rstrip("/")
    final_url = f"{base_url}{_ARK_EDIT_PATH}"

    ext = PurePosixPath(image_filename).suffix.lower()
    file_ct = _EXT_CONTENT_TYPE.get(ext, "image/jpeg")

    logger.info(
        "[换发型] ARK 图片编辑请求 url=%s model=%s file_ct=%s prompt=%.80s",
        final_url,
        model,
        file_ct,
        prompt,
    )

    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"image": (image_filename, image_bytes, file_ct)}
    form_data = {"model": model, "prompt": prompt, "n": "1"}

    timeout = httpx.Timeout(settings.hairstyle_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            final_url, headers=headers, files=files, data=form_data
        )
        body_text = resp.text
        logger.info(
            "[换发型] ARK 响应 status=%s body=%.600s",
            resp.status_code,
            body_text,
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"ARK 图片编辑失败 HTTP {resp.status_code}: {body_text[:400]}"
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
        return base64.b64decode(item["b64_json"])
    url = str(item.get("url") or "")
    if url:
        return await _download_bytes(url)
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
) -> HairstyleResult:
    model = settings.hairstyle_model.strip()
    if not model:
        raise ValueError(
            "未配置 HAIRSTYLE_MODEL，请在 .env 中设置（参考 .env.example）"
        )
    if not settings.jimeng_api_key.strip():
        raise ValueError("未配置 JIMENG_API_KEY，无法调用 ARK 图片编辑接口")

    prompt = _build_prompt(style)

    try:
        img_bytes = await asyncio.wait_for(
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
        "[换发型] 生成完成 style=%s gender=%s path=%s bytes=%d",
        style,
        gender,
        out_path,
        len(img_bytes),
    )

    result_url = f"/generated/hairstyle/{out_name}"
    suggestion = _STYLE_SUGGESTIONS.get(
        style, "这个发型会让整体气质更清爽，适合想提升精神感和形象辨识度的场景。"
    )
    return HairstyleResult(result_image_url=result_url, suggestion=suggestion)
