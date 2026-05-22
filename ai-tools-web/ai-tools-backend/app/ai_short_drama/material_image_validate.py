from __future__ import annotations

import logging
import struct
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from app.ai_short_drama.vertical_image import (
    ImageOrientationInfo,
    VerticalImageError,
    analyze_image_bytes,
    normalize_image_bytes_for_storage,
    validate_vertical_image_path,
)

logger = logging.getLogger(__name__)

MIN_IMAGE_BYTES = 20_000
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 200
SOLID_COLOR_CHANNEL_SPREAD = 14

AI_GENERATION_FAILED_MSG = "AI图片生成失败，请检查即梦API配置或手动上传素材。"
LANDSCAPE_REJECT_MSG = "图片为横图，不符合9:16竖屏要求，已拒绝保存。请重新生成或上传竖屏素材。"

VERTICAL_REQUIRED_TYPES = frozenset({"scene", "ui", "props", "effects"})


class ImageValidationError(ValueError):
    pass


def _png_dimensions(data: bytes) -> Tuple[int, int]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0
    try:
        w, h = struct.unpack(">II", data[16:24])
        return int(w), int(h)
    except struct.error:
        return 0, 0


def _is_solid_color_pil(data: bytes) -> bool:
    from PIL import Image

    im = Image.open(BytesIO(data)).convert("RGB")
    im.thumbnail((48, 48))
    pixels = list(im.getdata())
    if not pixels:
        return True
    rs = [p[0] for p in pixels]
    gs = [p[1] for p in pixels]
    bs = [p[2] for p in pixels]
    spread = max(max(rs) - min(rs), max(gs) - min(gs), max(bs) - min(bs))
    if spread < SOLID_COLOR_CHANNEL_SPREAD:
        return True
    colors = im.getcolors(maxcolors=64 * 64)
    if colors is not None and len(colors) <= 4:
        return True
    return False


def _is_solid_color_heuristic(data: bytes) -> bool:
    w, h = _png_dimensions(data)
    if w < MIN_IMAGE_WIDTH or h < MIN_IMAGE_HEIGHT:
        return True
    if w * h > 200_000 and len(data) < MIN_IMAGE_BYTES:
        return True
    return False


def is_solid_color_image(data: bytes) -> bool:
    try:
        return _is_solid_color_pil(data)
    except ImportError:
        return _is_solid_color_heuristic(data)
    except Exception as err:
        logger.warning("solid color check failed: %s", err)
        return _is_solid_color_heuristic(data)


def validate_image_bytes(
    data: bytes,
    *,
    material_type: str = "",
    require_vertical: bool = False,
) -> Optional[ImageOrientationInfo]:
    if not data or len(data) < 512:
        raise ImageValidationError("图片文件过小或为空")

    if len(data) < MIN_IMAGE_BYTES:
        raise ImageValidationError(f"图片体积过小（{len(data)} bytes），疑似无效占位图")

    w, h = _png_dimensions(data)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        if w < MIN_IMAGE_WIDTH or h < MIN_IMAGE_HEIGHT:
            raise ImageValidationError(f"图片尺寸无效：{w}x{h}")
    else:
        try:
            from PIL import Image

            im = Image.open(BytesIO(data))
            w, h = im.size
            if w < MIN_IMAGE_WIDTH or h < MIN_IMAGE_HEIGHT:
                raise ImageValidationError(f"图片尺寸无效：{w}x{h}")
        except ImportError:
            pass

    if is_solid_color_image(data):
        raise ImageValidationError("图片为单一纯色块，不能作为正式素材")

    mtype = (material_type or "").strip().lower()
    need_vertical = require_vertical or mtype in VERTICAL_REQUIRED_TYPES
    if need_vertical:
        try:
            info = analyze_image_bytes(data)
            if not info.is_vertical:
                raise ImageValidationError(LANDSCAPE_REJECT_MSG)
            return info
        except VerticalImageError as err:
            raise ImageValidationError(str(err)) from err

    return analyze_image_bytes(data) if data else None


def normalize_material_image_bytes(
    data: bytes,
    *,
    material_type: str,
) -> Tuple[bytes, ImageOrientationInfo]:
    """竖屏素材：EXIF 纠正后重编码；横图拒绝。"""
    mtype = (material_type or "scene").strip().lower()
    if mtype not in VERTICAL_REQUIRED_TYPES:
        return data, analyze_image_bytes(data)
    try:
        return normalize_image_bytes_for_storage(data)
    except VerticalImageError as err:
        raise ImageValidationError(str(err)) from err


def validate_image_path(path: Path, *, material_type: str = "") -> ImageOrientationInfo:
    if not path.is_file():
        raise ImageValidationError("图片文件不存在")
    mtype = (material_type or "").strip().lower()
    if mtype in VERTICAL_REQUIRED_TYPES:
        try:
            return validate_vertical_image_path(path)
        except VerticalImageError as err:
            raise ImageValidationError(str(err)) from err
    validate_image_bytes(path.read_bytes(), material_type=mtype)
    return analyze_image_bytes(path.read_bytes())


def is_invalid_asset_file(path: Path, *, material_type: str = "") -> bool:
    try:
        validate_image_path(path, material_type=material_type)
        return False
    except ImageValidationError:
        return True
    except Exception:
        return True
