from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import List

from app.ai_short_drama.material_asset_filter import is_placeholder_material_record
from app.ai_short_drama.material_image_validate import is_invalid_asset_file
from app.ai_short_drama.material_paths import UPLOAD_ROOT
from app.ai_short_drama.material_store import material_store

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_PUBLIC = BACKEND_ROOT.parent / "ai-tools-frontend" / "public"
QUARANTINE_ROOT = UPLOAD_ROOT / "_quarantine"

SCAN_REL_DIRS = (
    "scenes",
    "ui",
    "props",
    "effects",
)


def _scan_upload_dirs() -> List[Path]:
    found: List[Path] = []
    for rel in SCAN_REL_DIRS:
        base = UPLOAD_ROOT / rel
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                found.append(p)
    return found


def _scan_public_placeholders() -> List[Path]:
    ph = FRONTEND_PUBLIC / "short-drama" / "placeholders"
    if not ph.is_dir():
        return []
    return [p for p in ph.glob("*") if p.is_file()]


def _scan_quarantine_files() -> List[Path]:
    if not QUARANTINE_ROOT.is_dir():
        return []
    return [
        p
        for p in QUARANTINE_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]


def _purge_store_records_for_url(url: str) -> None:
    if not url:
        return
    try:
        items = material_store.list_materials()
    except Exception:
        return
    for item in items:
        if (item.get("url") or "") == url:
            try:
                material_store.delete_material(item["id"])
                logger.info("[素材清理] 已删除素材库记录 id=%s", item.get("id"))
            except Exception as err:
                logger.warning("[素材清理] 删除记录失败 id=%s: %s", item.get("id"), err)


def _delete_file(path: Path) -> bool:
    if not path.is_file():
        return False
    path.unlink()
    logger.info("[素材清理] 已删除文件 %s", path)
    return True


def scan_and_delete_invalid_assets(*, dry_run: bool = False) -> int:
    """
    扫描并直接删除纯色/无效图与 public/placeholders 占位文件，清理素材库记录。
    """
    deleted = 0
    candidates: List[tuple[Path, str]] = []

    for p in _scan_upload_dirs():
        candidates.append((p, "uploads"))
    for p in _scan_public_placeholders():
        candidates.append((p, "public-placeholders"))
    for p in _scan_quarantine_files():
        candidates.append((p, "quarantine"))

    for path, label in candidates:
        invalid = is_invalid_asset_file(path)
        in_placeholder_dir = "placeholders" in str(path).lower()
        if not invalid and not in_placeholder_dir:
            continue

        reason = "纯色/过小" if invalid else "占位目录"
        url = ""
        if label == "uploads":
            try:
                rel = path.relative_to(UPLOAD_ROOT)
                url = f"/uploads/short-drama/{rel.as_posix()}"
            except ValueError:
                pass

        logger.info("[素材清理] %s (%s) %s", path, reason, "待删除" if dry_run else "删除")
        if dry_run:
            deleted += 1
            continue

        if _delete_file(path):
            if url:
                _purge_store_records_for_url(url)
            deleted += 1

    if not dry_run:
        try:
            for item in material_store.list_materials():
                if not is_placeholder_material_record(item):
                    url = item.get("url") or ""
                    if url.startswith("/uploads/"):
                        disk = UPLOAD_ROOT / url.replace("/uploads/short-drama/", "")
                        if disk.is_file() and is_invalid_asset_file(disk):
                            _delete_file(disk)
                            material_store.delete_material(item["id"])
                            deleted += 1
                            continue
                    continue
                material_store.delete_material(item["id"])
                logger.info("[素材清理] 删除占位记录 id=%s", item.get("id"))
                deleted += 1
        except Exception as err:
            logger.warning("[素材清理] 扫描素材库失败: %s", err)

        if QUARANTINE_ROOT.is_dir():
            try:
                shutil.rmtree(QUARANTINE_ROOT)
                logger.info("[素材清理] 已移除隔离目录 %s", QUARANTINE_ROOT)
            except Exception as err:
                logger.warning("[素材清理] 移除隔离目录失败: %s", err)

    return deleted


# 兼容旧调用名
def scan_and_quarantine_invalid_assets(*, dry_run: bool = False) -> int:
    return scan_and_delete_invalid_assets(dry_run=dry_run)
