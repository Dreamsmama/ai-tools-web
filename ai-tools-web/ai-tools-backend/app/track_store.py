from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from threading import Lock
from typing import Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from app.config import settings


def _now_ms() -> int:
    return int(time.time() * 1000)


def _ms_to_date(ms: int) -> str:
    return time.strftime("%Y-%m-%d", time.localtime(ms / 1000))


def hash_ip(raw_ip: str) -> str:
    plain = (raw_ip or "").strip() or "unknown"
    base = f"{plain}|{settings.analytics_ip_salt}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


@dataclass
class TrackEvent:
    event: str
    feature: str
    page: str
    event_id: str
    status: str
    error_code: str
    duration_ms: int
    is_retry: bool
    user_agent: str
    ip_hash: str
    props: Dict[str, object]
    client_ts: Optional[int]


class TrackStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._lock = Lock()
        self._ready = False

    def _conn(self) -> psycopg.Connection:
        return psycopg.connect(self._database_url, row_factory=dict_row)

    def _ensure(self) -> None:
        if self._ready:
            return
        with self._lock:
            if self._ready:
                return
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS analytics_events (
                            id TEXT PRIMARY KEY,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            event_date DATE NOT NULL,
                            client_ts_ms BIGINT,
                            ip_hash TEXT NOT NULL,
                            event TEXT NOT NULL,
                            feature TEXT NOT NULL,
                            page TEXT NOT NULL,
                            event_id TEXT NOT NULL,
                            status TEXT NOT NULL,
                            error_code TEXT NOT NULL,
                            duration_ms INTEGER NOT NULL,
                            is_retry BOOLEAN NOT NULL DEFAULT FALSE,
                            user_agent TEXT NOT NULL,
                            props_json TEXT NOT NULL
                        )
                        """
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics_events(event_date)"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics_events(event)"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_analytics_feature ON analytics_events(feature)"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_analytics_event_id ON analytics_events(event_id)"
                    )
                conn.commit()
            self._ready = True

    def insert_event(self, payload: TrackEvent) -> str:
        self._ensure()
        now_ms = _now_ms()
        row_id = uuid.uuid4().hex
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO analytics_events (
                        id, created_at, event_date, client_ts_ms, ip_hash, event, feature, page,
                        event_id, status, error_code, duration_ms, is_retry, user_agent, props_json
                    ) VALUES (%s, to_timestamp(%s / 1000.0), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row_id,
                        now_ms,
                        _ms_to_date(now_ms),
                        payload.client_ts,
                        payload.ip_hash,
                        payload.event,
                        payload.feature,
                        payload.page,
                        payload.event_id,
                        payload.status,
                        payload.error_code,
                        payload.duration_ms,
                        payload.is_retry,
                        payload.user_agent[:512],
                        json.dumps(payload.props, ensure_ascii=False),
                    ),
                )
            conn.commit()
        return row_id

    def stats(self, start_date: str, end_date: str) -> Dict[str, object]:
        self._ensure()
        where_sql = "event_date >= %s AND event_date <= %s"
        where_args = (start_date, end_date)
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT
                        COUNT(*) AS total_events,
                        COUNT(DISTINCT ip_hash) AS unique_users,
                        SUM(CASE WHEN event = 'page_view' THEN 1 ELSE 0 END) AS page_views,
                        SUM(CASE WHEN event = 'submit_click' THEN 1 ELSE 0 END) AS submit_clicks,
                        SUM(CASE WHEN event = 'api_success' THEN 1 ELSE 0 END) AS api_success,
                        SUM(CASE WHEN event = 'api_fail' THEN 1 ELSE 0 END) AS api_fail
                    FROM analytics_events
                    WHERE {where_sql}
                    """,
                    where_args,
                )
                core = cur.fetchone() or {}

                cur.execute(
                    f"""
                    SELECT feature, COUNT(*) AS total
                    FROM analytics_events
                    WHERE {where_sql} AND event = 'submit_click'
                    GROUP BY feature
                    ORDER BY total DESC
                    """,
                    where_args,
                )
                feature_rows = cur.fetchall()

                cur.execute(
                    f"""
                    SELECT
                        event_date::text AS event_date,
                        COUNT(DISTINCT ip_hash) AS unique_users,
                        SUM(CASE WHEN event = 'submit_click' THEN 1 ELSE 0 END) AS submit_clicks,
                        SUM(CASE WHEN event = 'api_success' THEN 1 ELSE 0 END) AS api_success,
                        SUM(CASE WHEN event = 'api_fail' THEN 1 ELSE 0 END) AS api_fail
                    FROM analytics_events
                    WHERE {where_sql}
                    GROUP BY event_date
                    ORDER BY event_date ASC
                    """,
                    where_args,
                )
                trend_rows = cur.fetchall()

                cur.execute(
                    f"""
                    SELECT event_date::text AS event_date,
                           CAST(EXTRACT(EPOCH FROM created_at) * 1000 AS BIGINT) AS timestamp_ms,
                           feature, error_code, page
                    FROM analytics_events
                    WHERE {where_sql} AND event = 'api_fail'
                    ORDER BY created_at DESC
                    LIMIT 30
                    """,
                    where_args,
                )
                fail_rows = cur.fetchall()

        submit_clicks = int(core["submit_clicks"] or 0)
        api_success = int(core["api_success"] or 0)
        success_rate = 0.0 if submit_clicks <= 0 else round(api_success * 100.0 / submit_clicks, 2)

        return {
            "summary": {
                "unique_users": int(core["unique_users"] or 0),
                "total_events": int(core["total_events"] or 0),
                "page_views": int(core["page_views"] or 0),
                "submit_clicks": submit_clicks,
                "api_success": api_success,
                "api_fail": int(core["api_fail"] or 0),
                "success_rate": success_rate,
            },
            "feature_usage": [
                {"feature": str(row["feature"] or "unknown"), "count": int(row["total"] or 0)}
                for row in feature_rows
            ],
            "trend": [
                {
                    "date": str(row["event_date"]),
                    "unique_users": int(row["unique_users"] or 0),
                    "submit_clicks": int(row["submit_clicks"] or 0),
                    "api_success": int(row["api_success"] or 0),
                    "api_fail": int(row["api_fail"] or 0),
                }
                for row in trend_rows
            ],
            "recent_failures": [
                {
                    "date": str(row["event_date"]),
                    "timestamp_ms": int(row["timestamp_ms"] or 0),
                    "feature": str(row["feature"] or "unknown"),
                    "error_code": str(row["error_code"] or ""),
                    "page": str(row["page"] or ""),
                }
                for row in fail_rows
            ],
        }


track_store = TrackStore(settings.analytics_database_url.strip() or settings.rag_database_url)
