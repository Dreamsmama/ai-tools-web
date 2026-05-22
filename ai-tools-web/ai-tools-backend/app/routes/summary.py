from __future__ import annotations

from fastapi import APIRouter

from app.schemas import SummaryEnvelope, SummaryRequest
from app.services.summarize_service import summarize_chat

router = APIRouter(tags=["summary"])


@router.post(
    "/summary",
    response_model=SummaryEnvelope,
    response_model_exclude_none=True,
)
async def summary(body: SummaryRequest) -> SummaryEnvelope:
    """
    Body: `{ "inputText": "..." }` — same field name as `wx.cloud.callFunction({ data: { inputText } })`.
    Response: `{ "code": 0, "data": { intent, emotion, strategy, reply } }` or `{ "code", "message" }`.
    """
    return await summarize_chat(body.inputText)
