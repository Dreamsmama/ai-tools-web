from __future__ import annotations

import logging
from pathlib import PurePosixPath

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from app.services.hairstyle_service import generate_hairstyle

logger = logging.getLogger(__name__)

router = APIRouter(tags=["hairstyle"])

_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB


class HairstyleGenerateResponse(BaseModel):
    success: bool
    resultImageUrl: str = ""
    suggestion: str = ""
    message: str = ""


_VALID_BEAUTY_LEVELS = {"natural", "light", "upgrade"}


@router.post(
    "/hairstyle/generate",
    response_model=HairstyleGenerateResponse,
    response_model_exclude_none=False,
)
async def hairstyle_generate(
    image: UploadFile = File(...),
    style: str = Form(...),
    gender: str = Form(...),
    beauty_level: str = Form("light"),
) -> HairstyleGenerateResponse:
    # --- 参数校验 ---
    filename = (image.filename or "").strip()
    if not filename:
        return HairstyleGenerateResponse(success=False, message="请上传图片文件")

    ext = PurePosixPath(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        return HairstyleGenerateResponse(
            success=False, message="请上传 JPG、PNG 或 WebP 格式的图片"
        )

    style = style.strip()
    if not style:
        return HairstyleGenerateResponse(success=False, message="请选择发型风格")

    gender = gender.strip()
    if gender not in ("male", "female"):
        return HairstyleGenerateResponse(
            success=False, message="参数错误：gender 必须为 male 或 female"
        )

    # beauty_level 非法时静默回退到 light（前端传错不影响生成）
    beauty_level = beauty_level.strip()
    if beauty_level not in _VALID_BEAUTY_LEVELS:
        beauty_level = "light"

    # --- 读取文件 ---
    content = await image.read()
    if not content:
        return HairstyleGenerateResponse(success=False, message="图片文件为空")
    if len(content) > _MAX_IMAGE_BYTES:
        return HairstyleGenerateResponse(success=False, message="图片不能超过 8MB")

    # --- 调用服务 ---
    try:
        result = await generate_hairstyle(
            content,
            filename,
            style,
            gender,  # type: ignore[arg-type]
            beauty_level,
        )
        return HairstyleGenerateResponse(
            success=True,
            resultImageUrl=result.result_image_url,
            suggestion=result.suggestion,
        )
    except ValueError as exc:
        # 配置缺失等已知问题，直接返回错误信息
        logger.warning("[换发型] 配置错误: %s", exc)
        return HairstyleGenerateResponse(success=False, message=str(exc))
    except RuntimeError as exc:
        # ARK 接口异常，记录详细日志，前端只返回友好提示
        logger.error("[换发型] 生成失败: %s", exc)
        return HairstyleGenerateResponse(
            success=False,
            message="生成失败，可能是照片不清晰或服务繁忙，请换一张正脸清晰照片再试。",
        )
    except Exception:
        logger.exception("[换发型] 未知错误")
        return HairstyleGenerateResponse(
            success=False,
            message="生成失败，可能是照片不清晰或服务繁忙，请换一张正脸清晰照片再试。",
        )
