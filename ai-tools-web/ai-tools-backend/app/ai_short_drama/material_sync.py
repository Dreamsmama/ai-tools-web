from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from app.ai_short_drama.material_paths import UPLOAD_ROOT, UPLOAD_URL_PREFIX, VALID_SCENES
from app.ai_short_drama.tag_utils import ensure_material_tags

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
_SKIP_TOP_DIRS = frozenset({"character-ip", "_quarantine", "placeholders", "effects"})


def _now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _slug_to_scene_key(slug: str) -> str:
    key = (slug or "").strip().lower().replace("-", "_")
    if key in VALID_SCENES:
        return key
    aliases = {
        "night_office": "night_office",
        "office_night": "office_night",
        "office_day": "office_day",
    }
    return aliases.get(key, key if key in VALID_SCENES else "office")


def _infer_from_rel(rel: Path) -> Optional[Dict[str, Any]]:
    parts = rel.parts
    if not parts or parts[0] in _SKIP_TOP_DIRS:
        return None
    if any(p.startswith("_") for p in parts):
        return None

    mtype = "scene"
    role = "none"
    emotion = "none"
    scene = "none"
    tags: List[str] = []

    top = parts[0]
    if top == "scenes" and len(parts) >= 2:
        mtype = "scene"
        scene = _slug_to_scene_key(parts[1])
        tags = ["scene", scene]
    elif top == "ui":
        mtype = "ui"
        sub = parts[1] if len(parts) > 1 else "misc"
        tag = sub.replace("-", "_")
        tags = ["ui", tag]
    elif top == "props":
        mtype = "props"
        sub = parts[1] if len(parts) > 1 else "misc"
        tags = ["props", sub.replace("-", "_")]
    elif top == "characters" and len(parts) >= 2:
        mtype = "character"
        role = parts[1].replace("-", "_")
        emotion = parts[2].replace("-", "_") if len(parts) > 2 else "normal"
        tags = ["character", role, emotion]
    else:
        return None

    stem = rel.stem
    name = stem.replace("_", " ").replace("-", " ")
    material_id = "disk_" + re.sub(r"[^a-z0-9_]+", "_", rel.as_posix().lower())[:80]
    url = f"{UPLOAD_URL_PREFIX}/{rel.as_posix()}"

    row = {
        "id": material_id,
        "name": name,
        "type": mtype,
        "role": role,
        "emotion": emotion,
        "scene": scene,
        "url": url,
        "tags": tags,
        "aiGenerated": False,
        "style": "",
        "cacheKey": "",
        "source": "disk_sync",
        "createdAt": _now_str(),
        "updatedAt": _now_str(),
    }
    row["tags"] = ensure_material_tags(row, row["tags"])
    return row


def scan_upload_disk_records() -> List[Dict[str, Any]]:
    """扫描 uploads/short-drama 下已有图片，生成素材记录（不写入库）。"""
    if not UPLOAD_ROOT.is_dir():
        return []
    out: List[Dict[str, Any]] = []
    seen_urls: Set[str] = set()
    for path in sorted(UPLOAD_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _IMAGE_EXTS:
            continue
        try:
            rel = path.relative_to(UPLOAD_ROOT)
        except ValueError:
            continue
        row = _infer_from_rel(rel)
        if not row:
            continue
        url = row["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        out.append(row)
    return out


def sync_uploads_to_material_store(*, prune_stale: bool = False) -> int:
    """
    将 uploads/short-drama 下图片同步进素材库（以 URL 为键 upsert）。
    prune_stale=True 时删除库中指向 uploads 但文件已不存在的记录。
    """
    from app.ai_short_drama.material_store import material_store

    disk_rows = scan_upload_disk_records()
    if not disk_rows:
        return 0

    try:
        existing = material_store.list_materials()
    except Exception as err:
        logger.warning("[素材同步] 读取库失败: %s", err)
        existing = []

    by_url = {str(i.get("url") or ""): i for i in existing if i.get("url")}
    disk_urls = {r["url"] for r in disk_rows}
    synced = 0

    for row in disk_rows:
        url = row["url"]
        prev = by_url.get(url)
        if prev:
            continue
        try:
            material_store.create_material(row)
            synced += 1
        except Exception as err:
            logger.warning("[素材同步] 写入失败 %s: %s", url, err)

    if prune_stale:
        for item in existing:
            url = str(item.get("url") or "")
            if not url.startswith(UPLOAD_URL_PREFIX):
                continue
            if url in disk_urls:
                continue
            mid = str(item.get("id") or "")
            if mid:
                material_store.delete_material(mid)

    if synced:
        logger.info("[素材同步] 已从 uploads 导入 %s 条素材（扫描到 %s 个文件）", synced, len(disk_rows))
    return synced


def is_legacy_public_material_url(url: str) -> bool:
    """public 内置 SVG（/short-drama/xxx.svg），不是 uploads 真实素材。"""
    u = (url or "").strip()
    return u.startswith("/short-drama/") and not u.startswith(UPLOAD_URL_PREFIX)


def remove_builtin_public_entries() -> int:
    """移除指向 public/short-drama 的旧内置 SVG 占位记录。"""
    from app.ai_short_drama.material_store import material_store

    removed = 0
    try:
        items = material_store.list_materials()
    except Exception:
        return 0
    for item in items:
        url = str(item.get("url") or "")
        if not is_legacy_public_material_url(url):
            continue
        mid = str(item.get("id") or "")
        if mid and material_store.delete_material(mid):
            removed += 1
    if removed:
        logger.info("[素材同步] 已移除 %s 条 public 内置占位记录", removed)
    return removed


def reconcile_material_store() -> Dict[str, int]:
    """同步 uploads 并清理 public 占位（每次启动/刷新都应执行）。"""
    synced = sync_uploads_to_material_store()
    removed = remove_builtin_public_entries()
    return {"synced": synced, "removed_builtin": removed}
