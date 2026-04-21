from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from app.config import settings
from app.rag.constants import DOC_STATUS_UPLOADED
from app.rag.scope import RequestScope


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RagRepository:
    """PostgreSQL implementation (replaces legacy sqlite3 repository)."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.init_db()

    def _conn(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def init_db(self) -> None:
        embedding_dim = int(settings.rag_embedding_dim)
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cur.execute(
                    f"""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_default BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS workspaces (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    is_default BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS knowledge_bases (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    kb_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_hash TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content_summary TEXT NOT NULL DEFAULT '',
                    error_message TEXT NOT NULL DEFAULT '',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    kb_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json JSONB NOT NULL,
                    embedding_vector VECTOR({embedding_dim}) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS query_logs (
                    id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    kb_id TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    top_k INTEGER NOT NULL,
                    retrieved_chunk_ids TEXT NOT NULL,
                    retrieved_chunks_json TEXT NOT NULL DEFAULT '[]',
                    retrieval_latency_ms INTEGER NOT NULL DEFAULT 0,
                    generation_latency_ms INTEGER NOT NULL DEFAULT 0,
                    total_latency_ms INTEGER NOT NULL DEFAULT 0,
                    answer TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                );
                """
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_doc_scope ON documents(user_id, workspace_id, kb_id, status)"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_chunk_scope ON document_chunks(user_id, workspace_id, kb_id)"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query_scope ON query_logs(user_id, workspace_id, kb_id, created_at)"
                )
                # Placeholder index for future ANN optimization (ivfflat/hnsw tuning by workload):
                # CREATE INDEX IF NOT EXISTS idx_chunks_embedding_ivfflat
                # ON document_chunks USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
            self._ensure_query_log_columns(conn)
            self._ensure_kb_columns(conn)
            conn.commit()
        self.ensure_default_scope()

    def _ensure_query_log_columns(self, conn: psycopg.Connection) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='query_logs' AND table_schema='public'
                """
            )
            existing = {row["column_name"] for row in cur.fetchall()}
            if "retrieved_chunks_json" not in existing:
                cur.execute(
                    "ALTER TABLE query_logs ADD COLUMN retrieved_chunks_json TEXT NOT NULL DEFAULT '[]'"
                )
            if "retrieval_latency_ms" not in existing:
                cur.execute(
                    "ALTER TABLE query_logs ADD COLUMN retrieval_latency_ms INTEGER NOT NULL DEFAULT 0"
                )
            if "generation_latency_ms" not in existing:
                cur.execute(
                    "ALTER TABLE query_logs ADD COLUMN generation_latency_ms INTEGER NOT NULL DEFAULT 0"
                )
            if "total_latency_ms" not in existing:
                cur.execute(
                    "ALTER TABLE query_logs ADD COLUMN total_latency_ms INTEGER NOT NULL DEFAULT 0"
                )

    def _ensure_kb_columns(self, conn: psycopg.Connection) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='knowledge_bases' AND table_schema='public'
                """
            )
            existing = {row["column_name"] for row in cur.fetchall()}
            if "source_type" not in existing:
                cur.execute(
                    "ALTER TABLE knowledge_bases ADD COLUMN source_type TEXT NOT NULL DEFAULT 'user'"
                )
            if "is_selectable" not in existing:
                cur.execute(
                    "ALTER TABLE knowledge_bases ADD COLUMN is_selectable BOOLEAN NOT NULL DEFAULT FALSE"
                )

    def ensure_default_scope(self) -> None:
        now = _utc_now()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users(id, name, is_default, created_at)
                    VALUES (%s, %s, TRUE, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (settings.rag_default_user_id, "Default User", now),
                )
                cur.execute(
                    """
                    INSERT INTO workspaces(id, user_id, name, is_default, created_at)
                    VALUES (%s, %s, %s, TRUE, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        settings.rag_default_workspace_id,
                        settings.rag_default_user_id,
                        "Default Workspace",
                        now,
                    ),
                )
                cur.execute(
                    """
                    INSERT INTO knowledge_bases(id, user_id, workspace_id, name, description, source_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, 'official', %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        settings.rag_official_kb_id,
                        settings.rag_default_user_id,
                        settings.rag_default_workspace_id,
                        settings.rag_official_kb_name,
                        settings.rag_official_kb_description,
                        now,
                    ),
                )
                cur.execute(
                    """
                    UPDATE knowledge_bases
                    SET source_type='official', is_selectable=TRUE
                    WHERE id=%s AND user_id=%s AND workspace_id=%s
                    """,
                    (
                        settings.rag_official_kb_id,
                        settings.rag_default_user_id,
                        settings.rag_default_workspace_id,
                    ),
                )
            conn.commit()

    def create_kb(self, scope: RequestScope, name: str, description: str) -> Dict[str, Any]:
        now = _utc_now()
        kb_id = uuid.uuid4().hex
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO knowledge_bases(id, user_id, workspace_id, name, description, source_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, 'user', %s)
                    """,
                    (kb_id, scope.user_id, scope.workspace_id, name, description, now),
                )
                cur.execute(
                    "UPDATE knowledge_bases SET is_selectable=FALSE WHERE id=%s",
                    (kb_id,),
                )
            conn.commit()
        return {
            "id": kb_id,
            "name": name,
            "description": description,
            "source_type": "user",
            "is_selectable": False,
            "created_at": now,
        }

    def list_kbs(self, scope: RequestScope) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, source_type, is_selectable, created_at::text AS created_at
                    FROM knowledge_bases
                    WHERE user_id=%s AND workspace_id=%s
                      AND (
                        source_type='user'
                        OR (source_type='official' AND is_selectable=TRUE)
                      )
                    ORDER BY created_at DESC
                    """,
                    (scope.user_id, scope.workspace_id),
                )
                return [dict(row) for row in cur.fetchall()]

    def kb_exists_in_scope(self, scope: RequestScope, kb_id: str) -> bool:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id FROM knowledge_bases
                    WHERE id=%s AND user_id=%s AND workspace_id=%s
                      AND (
                        source_type='user'
                        OR (source_type='official' AND is_selectable=TRUE)
                      )
                    """,
                    (kb_id, scope.user_id, scope.workspace_id),
                )
                return cur.fetchone() is not None

    def create_document(
        self,
        scope: RequestScope,
        kb_id: str,
        filename: str,
        mime_type: str,
        file_size: int,
        file_hash: str,
        storage_path: str,
    ) -> Dict[str, Any]:
        doc_id = uuid.uuid4().hex
        now = _utc_now()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO documents(
                        id, user_id, workspace_id, kb_id, filename, mime_type, file_size,
                        file_hash, storage_path, status, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        doc_id,
                        scope.user_id,
                        scope.workspace_id,
                        kb_id,
                        filename,
                        mime_type,
                        file_size,
                        file_hash,
                        storage_path,
                        DOC_STATUS_UPLOADED,
                        now,
                        now,
                    ),
                )
            conn.commit()
        return self.get_document(scope, doc_id)

    def get_document(self, scope: RequestScope, document_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, kb_id, filename, mime_type, file_size, file_hash, status,
                           content_summary, error_message,
                           created_at::text AS created_at,
                           updated_at::text AS updated_at,
                           storage_path, retry_count
                    FROM documents
                    WHERE id=%s AND user_id=%s AND workspace_id=%s
                    """,
                    (document_id, scope.user_id, scope.workspace_id),
                )
                row = cur.fetchone()
        if not row:
            raise ValueError("文档不存在")
        return dict(row)

    def update_document_status(
        self,
        scope: RequestScope,
        document_id: str,
        status: str,
        error_message: str = "",
        content_summary: Optional[str] = None,
        increase_retry: bool = False,
    ) -> None:
        now = _utc_now()
        with self._conn() as conn:
            with conn.cursor() as cur:
                if increase_retry:
                    cur.execute(
                        """
                        UPDATE documents
                        SET status=%s, error_message=%s, updated_at=%s, retry_count=retry_count+1
                        WHERE id=%s AND user_id=%s AND workspace_id=%s
                        """,
                        (status, error_message, now, document_id, scope.user_id, scope.workspace_id),
                    )
                elif content_summary is None:
                    cur.execute(
                        """
                        UPDATE documents
                        SET status=%s, error_message=%s, updated_at=%s
                        WHERE id=%s AND user_id=%s AND workspace_id=%s
                        """,
                        (status, error_message, now, document_id, scope.user_id, scope.workspace_id),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE documents
                        SET status=%s, error_message=%s, content_summary=%s, updated_at=%s
                        WHERE id=%s AND user_id=%s AND workspace_id=%s
                        """,
                        (status, error_message, content_summary, now, document_id, scope.user_id, scope.workspace_id),
                    )
            conn.commit()

    def replace_chunks_with_vectors(
        self,
        scope: RequestScope,
        kb_id: str,
        document_id: str,
        chunks: List[Dict[str, Any]],
    ) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM document_chunks
                    WHERE document_id=%s AND user_id=%s AND workspace_id=%s AND kb_id=%s
                    """,
                    (document_id, scope.user_id, scope.workspace_id, kb_id),
                )
                now = _utc_now()
                for chunk in chunks:
                    vector_literal = "[" + ",".join(str(float(v)) for v in chunk["embedding"]) + "]"
                    cur.execute(
                        """
                        INSERT INTO document_chunks(
                            id, user_id, workspace_id, kb_id, document_id, chunk_index, content, metadata_json,
                            embedding_vector, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::vector, %s)
                        """,
                        (
                            uuid.uuid4().hex,
                            scope.user_id,
                            scope.workspace_id,
                            kb_id,
                            document_id,
                            chunk["chunk_index"],
                            chunk["content"],
                            json.dumps(chunk["metadata"], ensure_ascii=False),
                            vector_literal,
                            now,
                        ),
                    )
            conn.commit()

    def list_vectors_by_kb(self, scope: RequestScope, kb_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.document_id, c.content, c.embedding_vector::text AS embedding_vector,
                           c.metadata_json, d.filename
                    FROM document_chunks c
                    JOIN documents d ON d.id = c.document_id
                    WHERE c.user_id=%s AND c.workspace_id=%s AND c.kb_id=%s AND d.status='indexed'
                    """,
                    (scope.user_id, scope.workspace_id, kb_id),
                )
                rows = cur.fetchall()
        result: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            vec_text = item["embedding_vector"].strip("[]")
            item["embedding_vector"] = [float(x) for x in vec_text.split(",")] if vec_text else []
            result.append(item)
        return result

    def append_query_log(
        self,
        scope: RequestScope,
        kb_id: str,
        query_text: str,
        top_k: int,
        retrieved_chunk_ids: List[str],
        retrieved_chunks: List[Dict[str, Any]],
        answer: str,
        status: str,
        error_message: str,
        trace_id: str,
        retrieval_latency_ms: int,
        generation_latency_ms: int,
        total_latency_ms: int,
    ) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO query_logs(
                        id, trace_id, user_id, workspace_id, kb_id, query_text, top_k, retrieved_chunk_ids,
                        retrieved_chunks_json, retrieval_latency_ms, generation_latency_ms, total_latency_ms,
                        answer, status, error_message, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid.uuid4().hex,
                        trace_id,
                        scope.user_id,
                        scope.workspace_id,
                        kb_id,
                        query_text,
                        top_k,
                        json.dumps(retrieved_chunk_ids),
                        json.dumps(retrieved_chunks, ensure_ascii=False),
                        int(retrieval_latency_ms),
                        int(generation_latency_ms),
                        int(total_latency_ms),
                        answer,
                        status,
                        error_message,
                        _utc_now(),
                    ),
                )
            conn.commit()


rag_repository = RagRepository(settings.rag_database_url)
