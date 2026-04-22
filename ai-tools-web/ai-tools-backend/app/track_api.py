from __future__ import annotations

import time
import uuid
from datetime import date, timedelta
from typing import Dict, Literal, Optional

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, Field

from app.track_store import TrackEvent, hash_ip, track_store

router = APIRouter(prefix="/track", tags=["track"])


class TrackEventRequest(BaseModel):
    event: str = Field(..., description="event name, e.g. page_view/submit_click/api_success/api_fail")
    feature: str = Field(default="unknown")
    page: str = Field(default="")
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    status: str = Field(default="")
    error_code: str = Field(default="")
    duration_ms: int = Field(default=0)
    is_retry: bool = Field(default=False)
    props: Dict[str, object] = Field(default_factory=dict)
    ts: Optional[int] = Field(default=None, description="client timestamp in ms")


class Envelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[Dict[str, object]] = None


def _extract_ip(request: Request, x_forwarded_for: Optional[str], x_real_ip: Optional[str]) -> str:
    if x_forwarded_for:
        first = x_forwarded_for.split(",")[0].strip()
        if first:
            return first
    if x_real_ip:
        raw = x_real_ip.strip()
        if raw:
            return raw
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.post("/events", response_model=Envelope)
async def track_event(
    body: TrackEventRequest,
    request: Request,
    x_forwarded_for: Optional[str] = Header(default=None),
    x_real_ip: Optional[str] = Header(default=None),
    user_agent: Optional[str] = Header(default=None),
) -> Envelope:
    ip_hash = hash_ip(_extract_ip(request, x_forwarded_for, x_real_ip))
    row_id = track_store.insert_event(
        TrackEvent(
            event=body.event.strip()[:64] or "unknown",
            feature=body.feature.strip()[:64] or "unknown",
            page=body.page.strip()[:200],
            event_id=body.event_id.strip()[:128] or uuid.uuid4().hex,
            status=body.status.strip()[:64],
            error_code=body.error_code.strip()[:64],
            duration_ms=max(0, int(body.duration_ms or 0)),
            is_retry=bool(body.is_retry),
            user_agent=(user_agent or "").strip(),
            ip_hash=ip_hash,
            props=body.props if isinstance(body.props, dict) else {},
            client_ts=body.ts,
        )
    )
    return Envelope(code=0, data={"id": row_id})


def _resolve_range(
    period: Literal["today", "7d", "30d", "all"],
    start_date: Optional[str],
    end_date: Optional[str],
) -> tuple[str, str]:
    today = date.today()
    if period == "today":
        start = today
    elif period == "30d":
        start = today - timedelta(days=29)
    elif period == "all":
        start = date(1970, 1, 1)
    else:
        start = today - timedelta(days=6)
    end = today

    if start_date:
        start = date.fromisoformat(start_date)
    if end_date:
        end = date.fromisoformat(end_date)
    if start > end:
        start, end = end, start
    return start.isoformat(), end.isoformat()


@router.get("/stats", response_model=Envelope)
async def track_stats(
    period: Literal["today", "7d", "30d", "all"] = Query(default="7d"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
) -> Envelope:
    try:
        start, end = _resolve_range(period, start_date, end_date)
    except ValueError:
        return Envelope(code=400, message="日期格式错误，请使用 YYYY-MM-DD")

    data = track_store.stats(start, end)
    data["range"] = {
        "period": period,
        "start_date": start,
        "end_date": end,
        "generated_at_ms": int(time.time() * 1000),
    }
    return Envelope(code=0, data=data)
