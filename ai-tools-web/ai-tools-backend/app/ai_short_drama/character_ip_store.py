from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from app.ai_short_drama.material_infer import ROLE_CN_TO_KEY
from app.ai_short_drama.material_paths import UPLOAD_ROOT, UPLOAD_URL_PREFIX
from app.ai_short_drama.profession_store import profession_store

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
JSON_STORE_PATH = BACKEND_ROOT / "data" / "short_drama_character_ip.json"
CHARACTER_IP_DIR = UPLOAD_ROOT / "character-ip"

class _RoleLabelsProxy:
    """兼容 dict 用法，标签来自职业注册表。"""

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        if profession_store.is_valid_role(key):
            return profession_store.role_label(key)
        return default

    def __contains__(self, key: object) -> bool:
        return profession_store.is_valid_role(str(key))


ROLE_LABELS = _RoleLabelsProxy()


def role_label_for(role_key: str) -> str:
    return profession_store.role_label(role_key)


def _now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _role_slug(role: str) -> str:
    return role.strip().lower().replace("_", "-")


class CharacterIpStore:
    """角色 IP 存储：每职业多个候选，仅一个 isActive。"""

    def __init__(self) -> None:
        self._lock = Lock()
        self._cache: Optional[List[Dict[str, Any]]] = None
        self._cache_mtime: float = 0.0
        JSON_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CHARACTER_IP_DIR.mkdir(parents=True, exist_ok=True)

    def _invalidate_cache(self) -> None:
        self._cache = None
        self._cache_mtime = 0.0

    def _load_all(self) -> List[Dict[str, Any]]:
        if not JSON_STORE_PATH.is_file():
            return []
        try:
            data = json.loads(JSON_STORE_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _load_all_cached(self) -> List[Dict[str, Any]]:
        mtime = JSON_STORE_PATH.stat().st_mtime if JSON_STORE_PATH.is_file() else 0.0
        with self._lock:
            if self._cache is not None and mtime == self._cache_mtime:
                return list(self._cache)
            items = self._load_all()
            self._cache = items
            self._cache_mtime = mtime
            return list(items)

    def _save_all(self, items: List[Dict[str, Any]]) -> None:
        JSON_STORE_PATH.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        with self._lock:
            self._cache = list(items)
            self._cache_mtime = (
                JSON_STORE_PATH.stat().st_mtime if JSON_STORE_PATH.is_file() else 0.0
            )

    def list_all(self, role: str = "") -> List[Dict[str, Any]]:
        items = self._load_all_cached()
        if role:
            rk = role.strip().lower()
            items = [i for i in items if (i.get("role") or "").lower() == rk]
        return sorted(items, key=lambda x: x.get("createdAt") or "", reverse=True)

    def list_all_grouped_by_role(self) -> Dict[str, List[Dict[str, Any]]]:
        """一次读取，按 role 分组（工作台用）。"""
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for item in self._load_all_cached():
            rk = (item.get("role") or "").lower()
            if not rk:
                continue
            grouped.setdefault(rk, []).append(item)
        for rk in grouped:
            grouped[rk].sort(key=lambda x: x.get("createdAt") or "", reverse=True)
        return grouped

    def get_by_id(self, ip_id: str) -> Optional[Dict[str, Any]]:
        for item in self.list_all():
            if item.get("id") == ip_id:
                return item
        return None

    def get_active(self, role: str) -> Optional[Dict[str, Any]]:
        rk = role.strip().lower()
        for item in self.list_all(role=rk):
            if item.get("isActive") and item.get("status") == "approved":
                return item
        return None

    def list_pending(self, role: str = "") -> List[Dict[str, Any]]:
        items = self.list_all(role=role)
        return [i for i in items if i.get("status") == "pending"]

    def save_image_bytes(self, role: str, data: bytes, *, suffix: str = "png") -> tuple[str, str]:
        ip_id = f"ip_{uuid.uuid4().hex[:8]}"
        rel = f"character-ip/{_role_slug(role)}/{ip_id}.{suffix}"
        dest = UPLOAD_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        url = f"{UPLOAD_URL_PREFIX}/{rel}"
        return ip_id, url

    def create_record(
        self,
        *,
        role: str,
        base_image_url: str,
        source: str,
        status: str = "pending",
        is_active: bool = False,
        name: str = "",
        ip_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        rk = role.strip().lower()
        if not profession_store.is_valid_role(rk):
            raise ValueError(f"不支持的职业角色: {role}，请先在角色管理中创建该职业")

        record = {
            "id": ip_id or f"ip_{uuid.uuid4().hex[:8]}",
            "role": rk,
            "name": name or role_label_for(rk),
            "baseImageUrl": base_image_url,
            "source": source,
            "status": status,
            "isActive": bool(is_active),
            "createdAt": _now_str(),
        }

        with self._lock:
            items = self._load_all()
            if is_active:
                for item in items:
                    if (item.get("role") or "").lower() == rk:
                        item["isActive"] = False
            items.append(record)
            self._save_all(items)

        logger.info(
            "[角色IP] 创建 id=%s role=%s status=%s active=%s",
            record["id"],
            rk,
            status,
            is_active,
        )
        return record

    def activate(self, ip_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            items = self._load_all()
            target = None
            for item in items:
                if item.get("id") == ip_id:
                    target = item
                    break
            if not target:
                return None

            rk = (target.get("role") or "").lower()
            for item in items:
                if (item.get("role") or "").lower() == rk:
                    item["isActive"] = item.get("id") == ip_id
                    if item.get("id") == ip_id:
                        item["status"] = "approved"
                        target = item
            self._save_all(items)
            return dict(target)

    def delete(self, ip_id: str) -> bool:
        with self._lock:
            items = self._load_all()
            kept = []
            removed = None
            for item in items:
                if item.get("id") == ip_id:
                    removed = item
                    continue
                kept.append(item)
            if not removed:
                return False
            self._save_all(kept)

        url = removed.get("baseImageUrl") or ""
        if url.startswith(UPLOAD_URL_PREFIX):
            rel = url[len(UPLOAD_URL_PREFIX) + 1 :]
            path = UPLOAD_ROOT / rel
            if path.is_file():
                path.unlink(missing_ok=True)
        return True

    def reject(self, ip_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            items = self._load_all()
            for item in items:
                if item.get("id") == ip_id:
                    item["status"] = "rejected"
                    item["isActive"] = False
                    self._save_all(items)
                    return item
        return None

    def migrate_from_legacy_materials(self, materials: List[Dict[str, Any]]) -> int:
        """将已有 character 素材迁移为 approved 角色 IP（每职业仅首个）。"""
        migrated = 0
        for role in profession_store.all_role_keys():
            if self.get_active(role):
                continue
            candidates = [
                m
                for m in materials
                if (m.get("type") or "").lower() == "character"
                and (m.get("role") or "").lower() == role
                and (m.get("url") or "").strip()
            ]
            if not candidates:
                continue
            best = candidates[0]
            self.create_record(
                role=role,
                base_image_url=best["url"],
                source="uploaded",
                status="approved",
                is_active=True,
                name=role_label_for(role),
                ip_id=f"legacy_{role}",
            )
            migrated += 1
        return migrated


def infer_role_key_from_cn(career_cn: str) -> str:
    from app.ai_short_drama.role_catalog import resolve_role_key

    cn = (career_cn or "").strip()
    if not cn:
        return ""
    return resolve_role_key(cn, "")


character_ip_store = CharacterIpStore()
