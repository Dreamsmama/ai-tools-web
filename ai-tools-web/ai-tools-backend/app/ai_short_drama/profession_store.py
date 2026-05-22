from __future__ import annotations

import json
import logging
import re
import time
import uuid
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from app.ai_short_drama.material_infer import ROLE_CN_TO_KEY
from app.ai_short_drama.material_paths import VALID_ROLES

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
PROFESSIONS_JSON = BACKEND_ROOT / "data" / "short_drama_professions.json"

_BUILTIN: List[Dict[str, Any]] = [
    {"roleKey": "programmer", "name": "程序员", "description": "", "styleHint": "", "builtIn": True},
    {"roleKey": "product_manager", "name": "产品经理", "description": "", "styleHint": "", "builtIn": True},
    {"roleKey": "hr", "name": "HR", "description": "", "styleHint": "", "builtIn": True},
    {"roleKey": "tester", "name": "测试", "description": "", "styleHint": "", "builtIn": True},
    {"roleKey": "devops", "name": "运维", "description": "", "styleHint": "", "builtIn": True},
    {"roleKey": "sales", "name": "销售", "description": "", "styleHint": "", "builtIn": True},
]

_ROLE_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{1,47}$")


def _now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _slug_role_key(name: str, existing: set[str]) -> str:
    cn = (name or "").strip()
    if cn in ROLE_CN_TO_KEY:
        key = ROLE_CN_TO_KEY[cn]
    else:
        ascii_key = re.sub(r"[^a-z0-9]+", "_", cn.lower()).strip("_")
        if ascii_key and _ROLE_KEY_RE.match(ascii_key):
            key = ascii_key
        else:
            key = f"prof_{uuid.uuid4().hex[:8]}"
    base = key
    n = 1
    while key in existing:
        key = f"{base}_{n}"
        n += 1
    return key


class ProfessionStore:
    """可扩展职业注册表（内置 + 用户自定义）。"""

    def __init__(self) -> None:
        self._lock = RLock()
        self._items_cache: Optional[List[Dict[str, Any]]] = None
        self._role_index: Dict[str, Dict[str, Any]] = {}
        self._cache_mtime: float = 0.0
        PROFESSIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_seeded()

    def _ensure_seeded(self) -> None:
        with self._lock:
            if PROFESSIONS_JSON.is_file():
                return
            items = []
            for b in _BUILTIN:
                items.append(
                    {
                        "id": f"prof_{b['roleKey']}",
                        "roleKey": b["roleKey"],
                        "name": b["name"],
                        "description": b.get("description") or "",
                        "styleHint": b.get("styleHint") or "",
                        "builtIn": True,
                        "createdAt": _now_str(),
                    }
                )
            self._save_all(items)

    def _load_all(self) -> List[Dict[str, Any]]:
        self._ensure_seeded()
        try:
            data = json.loads(PROFESSIONS_JSON.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_all(self, items: List[Dict[str, Any]]) -> None:
        PROFESSIONS_JSON.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._rebuild_cache(items)

    def _rebuild_cache(self, items: List[Dict[str, Any]]) -> None:
        self._items_cache = list(items)
        self._role_index = {
            str(p.get("roleKey") or "").lower(): p
            for p in items
            if p.get("roleKey")
        }
        self._cache_mtime = (
            PROFESSIONS_JSON.stat().st_mtime if PROFESSIONS_JSON.is_file() else 0.0
        )

    def _items(self) -> List[Dict[str, Any]]:
        mtime = PROFESSIONS_JSON.stat().st_mtime if PROFESSIONS_JSON.is_file() else 0.0
        with self._lock:
            if self._items_cache is not None and mtime == self._cache_mtime:
                return self._items_cache
            items = self._load_all()
            self._rebuild_cache(items)
            return self._items_cache or []

    def list_all(self) -> List[Dict[str, Any]]:
        return sorted(self._items(), key=lambda x: (not x.get("builtIn"), x.get("name") or ""))

    def get_by_id(self, prof_id: str) -> Optional[Dict[str, Any]]:
        for item in self.list_all():
            if item.get("id") == prof_id:
                return item
        return None

    def get_by_role_key(self, role_key: str) -> Optional[Dict[str, Any]]:
        rk = (role_key or "").strip().lower()
        if not rk:
            return None
        self._items()
        return self._role_index.get(rk)

    def all_role_keys(self) -> List[str]:
        return [str(p.get("roleKey") or "") for p in self.list_all() if p.get("roleKey")]

    def is_valid_role(self, role_key: str) -> bool:
        rk = (role_key or "").strip().lower()
        return bool(rk) and self.get_by_role_key(rk) is not None

    def role_label(self, role_key: str) -> str:
        p = self.get_by_role_key(role_key)
        if p:
            return str(p.get("name") or role_key)
        return role_key

    def style_hint(self, role_key: str) -> str:
        p = self.get_by_role_key(role_key)
        return str((p or {}).get("styleHint") or "").strip()

    def resolve_career_cn(self, career_cn: str) -> str:
        cn = (career_cn or "").strip()
        if not cn:
            return ""
        for item in self.list_all():
            if (item.get("name") or "").strip() == cn:
                return str(item.get("roleKey") or "")
        return ROLE_CN_TO_KEY.get(cn, "")

    def career_options_cn(self) -> List[str]:
        return [str(p.get("name") or "") for p in self.list_all() if p.get("name")]

    def create(
        self,
        *,
        name: str,
        description: str = "",
        style_hint: str = "",
    ) -> Dict[str, Any]:
        label = (name or "").strip()
        if not label:
            raise ValueError("请填写职业名称")
        if len(label) > 24:
            raise ValueError("职业名称不能超过 24 字")

        with self._lock:
            items = self._load_all()
            for item in items:
                if (item.get("name") or "").strip() == label:
                    raise ValueError(f"职业「{label}」已存在")

            existing_keys = {(i.get("roleKey") or "").lower() for i in items}
            role_key = _slug_role_key(label, existing_keys)
            record = {
                "id": f"prof_{uuid.uuid4().hex[:10]}",
                "roleKey": role_key,
                "name": label,
                "description": (description or "").strip()[:500],
                "styleHint": (style_hint or "").strip()[:500],
                "builtIn": False,
                "createdAt": _now_str(),
            }
            items.append(record)
            self._save_all(items)
            logger.info("[职业] 新增 name=%s roleKey=%s", label, role_key)
            return dict(record)

    def update(
        self,
        prof_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        style_hint: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        with self._lock:
            items = self._load_all()
            target = None
            for item in items:
                if item.get("id") == prof_id:
                    target = item
                    break
            if not target:
                return None

            if name is not None:
                label = name.strip()
                if not label:
                    raise ValueError("职业名称不能为空")
                if len(label) > 24:
                    raise ValueError("职业名称不能超过 24 字")
                for item in items:
                    if item.get("id") != prof_id and (item.get("name") or "").strip() == label:
                        raise ValueError(f"职业「{label}」已存在")
                target["name"] = label

            if description is not None:
                target["description"] = description.strip()[:500]
            if style_hint is not None:
                target["styleHint"] = style_hint.strip()[:500]

            self._save_all(items)
            return dict(target)

    def delete(self, prof_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            items = self._load_all()
            removed = None
            kept = []
            for item in items:
                if item.get("id") == prof_id:
                    removed = item
                else:
                    kept.append(item)
            if not removed:
                return None
            if removed.get("builtIn"):
                raise ValueError("内置职业不可删除")
            self._save_all(kept)
            logger.info("[职业] 删除 id=%s name=%s", prof_id, removed.get("name"))
            return dict(removed)


profession_store = ProfessionStore()

# 兼容旧代码：动态标签表
def get_role_labels_map() -> Dict[str, str]:
    return {str(p["roleKey"]): str(p["name"]) for p in profession_store.list_all()}
