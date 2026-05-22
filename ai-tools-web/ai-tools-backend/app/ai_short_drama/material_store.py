from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from app.ai_short_drama.material_media import validate_upload_filename
from app.ai_short_drama.material_paths import (
    UPLOAD_ROOT,
    build_material_paths,
    ensure_standard_layout,
    url_to_disk_path,
)
from app.ai_short_drama.tag_utils import ensure_material_tags
from app.config import settings
from app.utils.pg_utils import is_postgres_reachable

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = UPLOAD_ROOT
JSON_STORE_PATH = BACKEND_ROOT / "data" / "short_drama_materials.json"


def _now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _parse_tags(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(t).strip().lower() for t in raw if str(t).strip()]
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(t).strip().lower() for t in parsed if str(t).strip()]
        except json.JSONDecodeError:
            pass
        return [t.strip().lower() for t in text.replace("，", ",").split(",") if t.strip()]
    return []


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    created = row.get("created_at")
    updated = row.get("updated_at")
    if hasattr(created, "strftime"):
        created = created.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(updated, "strftime"):
        updated = updated.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": row["id"],
        "name": row["name"],
        "type": row["type"],
        "role": row["role"],
        "emotion": row["emotion"],
        "scene": row["scene"],
        "url": row["url"],
        "tags": _parse_tags(row.get("tags")),
        "aiGenerated": bool(row.get("ai_generated") or row.get("aiGenerated")),
        "style": str(row.get("style") or ""),
        "cacheKey": str(row.get("cache_key") or row.get("cacheKey") or ""),
        "createdAt": created or row.get("createdAt") or "",
        "updatedAt": updated or row.get("updatedAt") or "",
    }


class MaterialStore:
    """PostgreSQL 主存储；连接失败时降级到 JSON 文件（便于本地开发）。"""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.strip()
        self._lock = Lock()
        self._pg_ready = False
        self._use_json = False
        JSON_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        ensure_standard_layout()
        if self._database_url and is_postgres_reachable(self._database_url):
            try:
                self._ensure_pg()
                self._pg_ready = True
            except Exception as err:
                logger.warning("short drama materials: PG unavailable, use JSON store: %s", err)
                self._use_json = True
        else:
            if self._database_url:
                logger.warning(
                    "short drama materials: PostgreSQL not reachable, use JSON store"
                )
            self._use_json = True

    def _conn(self) -> psycopg.Connection:
        return psycopg.connect(
            self._database_url,
            row_factory=dict_row,
            connect_timeout=5,
        )

    def _ensure_pg(self) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ai_short_drama_material (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL DEFAULT 'scene',
                        role TEXT NOT NULL DEFAULT 'none',
                        emotion TEXT NOT NULL DEFAULT 'none',
                        scene TEXT NOT NULL DEFAULT 'none',
                        url TEXT NOT NULL,
                        tags TEXT NOT NULL DEFAULT '[]',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sd_material_type ON ai_short_drama_material(type)"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sd_material_role ON ai_short_drama_material(role)"
                )
                cur.execute(
                    """
                    ALTER TABLE ai_short_drama_material
                    ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN NOT NULL DEFAULT FALSE
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE ai_short_drama_material
                    ADD COLUMN IF NOT EXISTS style TEXT NOT NULL DEFAULT ''
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE ai_short_drama_material
                    ADD COLUMN IF NOT EXISTS cache_key TEXT NOT NULL DEFAULT ''
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_sd_material_ai_generated
                    ON ai_short_drama_material(ai_generated)
                    """
                )
            conn.commit()

    def _load_json(self) -> List[Dict[str, Any]]:
        if not JSON_STORE_PATH.is_file():
            return []
        try:
            data = json.loads(JSON_STORE_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_json(self, items: List[Dict[str, Any]]) -> None:
        JSON_STORE_PATH.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_materials(
        self,
        *,
        type_filter: str = "",
        role_filter: str = "",
        emotion_filter: str = "",
        tag_keyword: str = "",
        ai_generated_filter: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        if self._pg_ready:
            return self._list_pg(
                type_filter, role_filter, emotion_filter, tag_keyword, ai_generated_filter
            )
        return self._list_json(
            type_filter, role_filter, emotion_filter, tag_keyword, ai_generated_filter
        )

    def _list_pg(
        self,
        type_filter: str,
        role_filter: str,
        emotion_filter: str,
        tag_keyword: str,
        ai_generated_filter: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        self._ensure_pg()
        sql = "SELECT * FROM ai_short_drama_material WHERE 1=1"
        params: List[Any] = []
        if type_filter:
            sql += " AND type = %s"
            params.append(type_filter)
        if role_filter:
            sql += " AND role = %s"
            params.append(role_filter)
        if emotion_filter:
            sql += " AND emotion = %s"
            params.append(emotion_filter)
        if ai_generated_filter is not None:
            sql += " AND ai_generated = %s"
            params.append(ai_generated_filter)
        if tag_keyword:
            sql += " AND tags ILIKE %s"
            params.append(f"%{tag_keyword.lower()}%")
        sql += " ORDER BY created_at DESC"
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        return [_row_to_dict(r) for r in rows]

    def _list_json(
        self,
        type_filter: str,
        role_filter: str,
        emotion_filter: str,
        tag_keyword: str,
        ai_generated_filter: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        items = self._load_json()
        out: List[Dict[str, Any]] = []
        kw = tag_keyword.lower().strip()
        for item in items:
            if type_filter and item.get("type") != type_filter:
                continue
            if role_filter and item.get("role") != role_filter:
                continue
            if emotion_filter and item.get("emotion") != emotion_filter:
                continue
            if ai_generated_filter is not None:
                flag = bool(item.get("aiGenerated") or item.get("ai_generated"))
                if flag != ai_generated_filter:
                    continue
            tags = _parse_tags(item.get("tags"))
            if kw and not any(kw in t for t in tags) and kw not in item.get("name", "").lower():
                continue
            normalized = _row_to_dict({**item, "tags": json.dumps(tags, ensure_ascii=False)})
            out.append(normalized)
        return sorted(out, key=lambda x: x.get("createdAt") or "", reverse=True)

    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        if self._pg_ready:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM ai_short_drama_material WHERE id = %s",
                        (material_id,),
                    )
                    row = cur.fetchone()
            return _row_to_dict(row) if row else None
        for item in self._load_json():
            if item.get("id") == material_id:
                return _row_to_dict(item)
        return None

    def create_material(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        material_id = (payload.get("id") or "").strip() or f"material_{uuid.uuid4().hex[:12]}"
        tags = ensure_material_tags(payload, _parse_tags(payload.get("tags")))
        now = _now_str()
        row = {
            "id": material_id,
            "name": (payload.get("name") or "").strip() or "未命名素材",
            "type": (payload.get("type") or "scene").strip(),
            "role": (payload.get("role") or "none").strip(),
            "emotion": (payload.get("emotion") or "none").strip(),
            "scene": (payload.get("scene") or "none").strip(),
            "url": (payload.get("url") or "").strip(),
            "tags": tags,
            "aiGenerated": bool(payload.get("aiGenerated") or payload.get("ai_generated")),
            "style": str(payload.get("style") or ""),
            "cacheKey": str(payload.get("cacheKey") or payload.get("cache_key") or ""),
            "createdAt": now,
            "updatedAt": now,
        }
        if not row["url"]:
            raise ValueError("素材 URL 不能为空")

        if self._pg_ready:
            self._ensure_pg()
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO ai_short_drama_material (
                            id, name, type, role, emotion, scene, url, tags,
                            ai_generated, style, cache_key, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """,
                        (
                            row["id"],
                            row["name"],
                            row["type"],
                            row["role"],
                            row["emotion"],
                            row["scene"],
                            row["url"],
                            json.dumps(tags, ensure_ascii=False),
                            row["aiGenerated"],
                            row["style"],
                            row["cacheKey"],
                        ),
                    )
                conn.commit()
            return self.get_material(material_id) or row

        items = self._load_json()
        items = [i for i in items if i.get("id") != material_id]
        items.append({**row, "tags": tags})
        self._save_json(items)
        return row

    def delete_material(self, material_id: str) -> bool:
        if self._pg_ready:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM ai_short_drama_material WHERE id = %s RETURNING url",
                        (material_id,),
                    )
                    deleted = cur.fetchone()
                conn.commit()
            if deleted and deleted.get("url"):
                self._try_remove_file(deleted["url"])
            return deleted is not None

        items = self._load_json()
        kept: List[Dict[str, Any]] = []
        removed = False
        for item in items:
            if item.get("id") == material_id:
                removed = True
                self._try_remove_file(item.get("url", ""))
            else:
                kept.append(item)
        if removed:
            self._save_json(kept)
        return removed

    def _try_remove_file(self, url: str) -> None:
        path = url_to_disk_path(url)
        if not path:
            # 兼容旧路径解析
            if url and url.startswith("/uploads/short-drama/"):
                legacy = BACKEND_ROOT / url.lstrip("/")
                path = legacy if legacy.is_file() else None
        if not path:
            return
        try:
            path.unlink()
        except OSError:
            pass

    def save_upload_file(
        self,
        filename: str,
        content: bytes,
        *,
        type: str = "placeholder",
        role: str = "none",
        emotion: str = "none",
        scene: str = "none",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        ext = Path(filename).suffix.lower()
        upload_err = validate_upload_filename(filename)
        if upload_err:
            raise ValueError(upload_err)

        paths = build_material_paths(
            type=type,
            role=role,
            emotion=emotion,
            scene=scene,
            tags=tags,
            ext=ext,
        )
        dest = UPLOAD_DIR / paths["rel_path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        return {
            "id": paths["id"],
            "url": paths["url"],
            "filename": paths["filename"],
            "rel_dir": paths["rel_dir"],
        }


material_store = MaterialStore(settings.short_drama_database_url.strip())
