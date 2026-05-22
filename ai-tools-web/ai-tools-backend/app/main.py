"""
FastAPI entry: app setup, middleware, static mounts, route registration.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import register_routes
from app.startup import ensure_runtime_directories, run_short_drama_startup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
_request_logger = logging.getLogger("app.request")

app = FastAPI(title="ai-tools-backend", version="0.1.0")


_TRACKED_PATH_PREFIXES = ("/ai-short-drama", "/tools/xiaohongshu-agent")


@app.middleware("http")
async def log_slow_agent_requests(request: Request, call_next):
    path = request.url.path
    track = path.startswith(_TRACKED_PATH_PREFIXES)
    if track:
        _request_logger.info("→ %s %s", request.method, path)
    started = time.perf_counter()
    response = await call_next(request)
    if track:
        elapsed = time.perf_counter() - started
        _request_logger.info(
            "← %s %s %.1fs status=%s",
            request.method,
            path,
            elapsed,
            response.status_code,
        )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)

_backend_root = Path(__file__).resolve().parent.parent
_generated_root, _uploads_root = ensure_runtime_directories(_backend_root)
run_short_drama_startup()

app.mount("/generated", StaticFiles(directory=str(_generated_root)), name="generated")
app.mount("/uploads", StaticFiles(directory=str(_uploads_root)), name="uploads")


def main() -> None:
    import os

    import uvicorn

    # 长任务（/generate）进行中 reload 会打断请求；本地默认关 reload，需要热更新时设 UVICORN_RELOAD=1
    reload = os.getenv("UVICORN_RELOAD", "0").lower() in ("1", "true", "yes")
    # 多 worker：生图/分镜长任务占用一个进程时，其它接口仍可由另一进程响应（reload 模式仅支持单进程）
    workers = 1
    if not reload:
        try:
            workers = max(1, min(8, int(os.getenv("UVICORN_WORKERS", "2"))))
        except ValueError:
            workers = 2
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload,
        workers=workers,
    )


if __name__ == "__main__":
    main()
