from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai_short_drama.material_infer import infer_emotion_key, infer_role_key, normalize_scene_key
from app.ai_short_drama.materials import MATERIAL_CATALOG

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_PUBLIC = BACKEND_ROOT.parent / "ai-tools-frontend" / "public"
SHORT_DRAMA_PUBLIC = FRONTEND_PUBLIC / "short-drama"

_ROLE_TAGS = frozenset(
    {"programmer", "product_manager", "hr", "tester", "devops", "ops", "sales"}
)
_SCENE_TAGS = frozenset(
    {
        "night_office",
        "office",
        "meeting",
        "interview",
        "error_log",
        "messages",
        "alert",
        "oncall",
    }
)


def _now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def resolve_public_material_url(material_id: str, catalog_url: str = "") -> str:
    """解析 public/short-drama 下真实文件（优先 svg，兼容 catalog 里的 .png）。"""
    base = (material_id or "").strip()
    if not base and catalog_url.startswith("/short-drama/"):
        base = Path(catalog_url).stem
    if not base:
        return ""
    for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp"):
        path = SHORT_DRAMA_PUBLIC / f"{base}{ext}"
        if path.is_file():
            return f"/short-drama/{base}{ext}"
    return catalog_url if catalog_url else ""


_EMOTION_TAGS = frozenset({"tired", "stressed", "shocked", "angry", "happy", "calm", "normal"})


def _infer_fields_from_tags(tags: List[str]) -> Dict[str, str]:
    normalized = [str(t).strip().lower() for t in tags if str(t).strip()]
    role = "none"
    emotion = "normal"
    scene = "office"
    for tag in normalized:
        if tag in _ROLE_TAGS:
            role = infer_role_key(tag) or tag
            break
    for tag in normalized:
        if tag in _EMOTION_TAGS:
            emotion = infer_emotion_key(tag) or tag
            break
    for tag in normalized:
        if tag in _SCENE_TAGS:
            scene = normalize_scene_key(tag)
            break
    return {"role": role, "emotion": emotion, "scene": scene}


def catalog_entry_to_record(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    mid = str(entry.get("id") or "").strip()
    if not mid:
        return None
    url = resolve_public_material_url(mid, str(entry.get("url") or ""))
    if not url or not url.startswith("/short-drama/"):
        return None
    rel = url[len("/short-drama/") :].lstrip("/")
    if not (SHORT_DRAMA_PUBLIC / rel).is_file():
        return None
    tags = [str(t).strip().lower() for t in (entry.get("tags") or []) if str(t).strip()]
    fields = _infer_fields_from_tags(tags)
    return {
        "id": mid,
        "name": str(entry.get("name") or mid),
        "type": "scene",
        "role": fields["role"],
        "emotion": fields["emotion"],
        "scene": fields["scene"],
        "url": url,
        "tags": tags,
        "aiGenerated": False,
        "style": "",
        "cacheKey": "",
        "builtIn": True,
        "source": "static_public",
        "createdAt": _now_str(),
        "updatedAt": _now_str(),
    }


def list_builtin_public_materials() -> List[Dict[str, Any]]:
    """前端 public/short-drama 内置场景图（不写入 DB，仅合并到列表/匹配）。"""
    out: List[Dict[str, Any]] = []
    for entry in MATERIAL_CATALOG:
        row = catalog_entry_to_record(entry)
        if row:
            out.append(row)
    return out


def seed_builtin_materials_if_empty() -> int:
    """仅当 uploads 与素材库均为空时，才导入 public 内置 SVG（兜底）。"""
    from app.ai_short_drama.material_sync import is_legacy_public_material_url, scan_upload_disk_records
    from app.ai_short_drama.material_store import material_store

    if scan_upload_disk_records():
        return 0

    try:
        existing = material_store.list_materials()
    except Exception as err:
        logger.warning("[素材引导] 读取素材库失败: %s", err)
        return 0
    real = [i for i in existing if not is_legacy_public_material_url(str(i.get("url") or ""))]
    if real:
        return 0

    seeded = 0
    for entry in MATERIAL_CATALOG:
        row = catalog_entry_to_record(entry)
        if not row:
            continue
        try:
            material_store.create_material(row)
            seeded += 1
        except Exception as err:
            logger.warning("[素材引导] 写入 %s 失败: %s", row.get("id"), err)
    if seeded:
        logger.info("[素材引导] 已从 public/short-drama 导入 %s 条内置场景素材", seeded)
    return seeded
