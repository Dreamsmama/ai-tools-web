from __future__ import annotations

import socket
from typing import Optional
from urllib.parse import urlparse


def pg_host_port(database_url: str) -> tuple[str, int]:
    parsed = urlparse(database_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 5432
    return host, port


def is_postgres_reachable(database_url: str, *, timeout: float = 1.0) -> bool:
    if not (database_url or "").strip():
        return False
    try:
        host, port = pg_host_port(database_url)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
