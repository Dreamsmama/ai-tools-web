from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
TARGET_ASPECT = 9 / 16
VERTICAL_SIZE_API = "1080x1920"
# 允许略宽于 9:16 的误差（API 有时差 1~2px）
MIN_HEIGHT_RATIO = 1.05

VERTICAL_PROMPT_EN = (
    "9:16 vertical composition, portrait mobile video composition, "
    "for TikTok vertical video, vertical framing, subject centered vertically, "
    "single subject center frame, leave safe margin top and bottom for subtitles"
)

VERTICAL_PROMPT_CN = (
    "适合抖音/小红书/B站竖屏视频，9:16竖屏构图，竖屏短视频画幅，"
    "主体位于画面中央，中景构图，上下预留字幕安全区，"
    "禁止横向超宽构图，禁止横屏全景"
)

FORBIDDEN_HORIZONTAL_HINT_CN = (
    "禁止：横向超宽办公桌、横向多人会议室、横向显示器墙、横向服务器长廊、"
    "宽银幕横构图、panoramic horizontal layout"
)

RECOMMENDED_CONTENT_CN = (
    "推荐：中国互联网职场瞬间、中心构图、上下字幕留白、竖屏景深，"
    "可以是地铁/便利店/飞书界面/夜景街道，避免横屏工位壁纸"
)


class VerticalImageError(ValueError):
    pass


@dataclass
class ImageOrientationInfo:
    width: int
    height: int
    aspect_ratio: str
    is_vertical: bool
    exif_orientation: Optional[int] = None
    was_exif_transposed: bool = False

    def to_meta_dict(self) -> Dict[str, Any]:
        return {
            "imageWidth": self.width,
            "imageHeight": self.height,
            "aspectRatio": self.aspect_ratio,
            "isVertical": self.is_vertical,
            "exifOrientation": self.exif_orientation,
        }


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a or 1


def format_aspect_ratio(width: int, height: int) -> str:
    if width < 1 or height < 1:
        return "unknown"
    g = _gcd(width, height)
    return f"{width // g}:{height // g}"


def _read_exif_orientation(im) -> Optional[int]:
    try:
        exif = im.getexif()
        if exif:
            return int(exif.get(274))  # Orientation
    except Exception:
        pass
    return None


def analyze_image_bytes(data: bytes) -> ImageOrientationInfo:
    from PIL import Image

    im = Image.open(BytesIO(data))
    exif_ori = _read_exif_orientation(im)
    w, h = im.size
    is_vertical = h > w * MIN_HEIGHT_RATIO
    return ImageOrientationInfo(
        width=w,
        height=h,
        aspect_ratio=format_aspect_ratio(w, h),
        is_vertical=is_vertical,
        exif_orientation=exif_ori,
        was_exif_transposed=False,
    )


def normalize_image_bytes_for_storage(data: bytes) -> Tuple[bytes, ImageOrientationInfo]:
    """
    仅做 EXIF 方向纠正（非横转竖）；纠正后必须为竖图才返回 PNG 字节。
    """
    from PIL import Image, ImageOps

    im = Image.open(BytesIO(data))
    exif_ori = _read_exif_orientation(im)
    transposed = ImageOps.exif_transpose(im)
    was_exif = transposed.size != im.size or exif_ori not in (None, 1)

    w, h = transposed.size
    info = ImageOrientationInfo(
        width=w,
        height=h,
        aspect_ratio=format_aspect_ratio(w, h),
        is_vertical=h > w * MIN_HEIGHT_RATIO,
        exif_orientation=exif_ori,
        was_exif_transposed=was_exif,
    )

    if not info.is_vertical:
        raise VerticalImageError(
            f"图片为横图或方图（{w}x{h}），不符合 9:16 竖屏要求，已拒绝入库"
        )

    buf = BytesIO()
    if transposed.mode not in ("RGB", "RGBA"):
        transposed = transposed.convert("RGB")
    transposed.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), info


def validate_vertical_image_bytes(data: bytes) -> ImageOrientationInfo:
    """校验：竖屏比例；横图直接拒绝。"""
    try:
        _, info = normalize_image_bytes_for_storage(data)
        return info
    except VerticalImageError:
        raise
    except Exception as err:
        raise VerticalImageError(f"无法解析图片方向：{err}") from err


def validate_vertical_image_path(path) -> ImageOrientationInfo:
    from pathlib import Path

    p = Path(path)
    return validate_vertical_image_bytes(p.read_bytes())


def append_vertical_prompt(prompt: str, *, material_type: str = "scene") -> str:
    base = (prompt or "").strip().rstrip("。.")
    parts = [
        base,
        VERTICAL_PROMPT_CN,
        VERTICAL_PROMPT_EN,
        FORBIDDEN_HORIZONTAL_HINT_CN,
    ]
    if material_type in ("scene", "effects"):
        parts.append(RECOMMENDED_CONTENT_CN)
    return "。".join(p for p in parts if p) + "。"


def build_scene_generation_prompt(
    *,
    scene_desc: str,
    mood: str,
    props_fragment: str,
    material_type: str = "scene",
) -> str:
    if material_type == "ui":
        return append_vertical_prompt(
            f"竖屏手机界面截图风格，{scene_desc}，单屏 UI 特写，无横向分屏，无人物，无水印",
            material_type="ui",
        )
    if material_type == "effects":
        return append_vertical_prompt(
            f"竖屏氛围特效，{scene_desc}，{mood}，轻量粒子/光晕，中心构图",
            material_type="effects",
        )
    if material_type == "props":
        return append_vertical_prompt(
            f"竖屏特写道具，{props_fragment or scene_desc}，中心构图，浅景深",
            material_type="props",
        )
    return append_vertical_prompt(
        f"{scene_desc}。{props_fragment}。{mood}。国产互联网插画半写实，无人物特写，无水印",
        material_type="scene",
    )


def ffmpeg_vertical_fit_filter(width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT) -> str:
    """
    竖屏成片：模糊背景铺满 + 前景等比缩小居中。不改变图片方向，不 transpose。
    """
    return (
        f"[0:v]split=2[sd_fg][sd_bg];"
        f"[sd_bg]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},gblur=sigma=28[sd_bg_bl];"
        f"[sd_fg]scale={width}:{height}:force_original_aspect_ratio=decrease[sd_fg_sc];"
        f"[sd_bg_bl][sd_fg_sc]overlay=(W-w)/2:(H-h)/2"
    )
