from __future__ import annotations

from pathlib import Path
from typing import Optional

# 上传与视频合成允许的位图格式（不含 svg）
ALLOWED_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})

SVG_REJECT_UPLOAD_MSG = "暂不支持 SVG，请上传 PNG/JPG"
SVG_VIDEO_ERROR_MSG = "当前素材是 SVG，视频合成暂不支持，请替换为 PNG/JPG 素材。"


def file_extension(name_or_url: str) -> str:
    raw = (name_or_url or "").strip().split("?")[0]
    return Path(raw).suffix.lower()


def is_svg(name_or_url: str) -> bool:
    return file_extension(name_or_url) == ".svg"


def is_allowed_upload_extension(ext: str) -> bool:
    e = (ext or "").lower()
    if not e.startswith("."):
        e = f".{e}"
    return e in ALLOWED_IMAGE_EXTENSIONS


def validate_upload_filename(filename: str) -> Optional[str]:
    ext = file_extension(filename)
    if is_svg(filename):
        return SVG_REJECT_UPLOAD_MSG
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return "仅支持 png / jpg / jpeg / webp"
    return None


def validate_image_path_for_video(path: Path) -> Optional[str]:
    """视频合成前校验；返回错误文案或 None 表示通过。"""
    if not path or not path.is_file():
        return "素材图片不存在，请更换素材后重试。"
    ext = path.suffix.lower()
    if ext == ".svg":
        return SVG_VIDEO_ERROR_MSG
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return f"视频合成暂不支持 {ext or '该'} 格式，请使用 PNG/JPG 素材。"
    return None
