"""
FastAPI entry: /health, /summary, /prepare-consult (aligned with WeChat cloud functions).
"""

from __future__ import annotations

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.prepare_consult_service import prepare_consult
from app.rag.api import router as rag_router
from app.schemas import (
    PrepareConsultEnvelope,
    PrepareConsultRequest,
    SummaryEnvelope,
    SummaryRequest,
)
from app.summarize_service import summarize_chat
from app.track_api import router as track_router

app = FastAPI(title="ai-tools-backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)
app.include_router(track_router)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/summary",
    response_model=SummaryEnvelope,
    response_model_exclude_none=True,
)
async def summary(body: SummaryRequest) -> SummaryEnvelope:
    """
    Body: `{ "inputText": "..." }` — same field name as `wx.cloud.callFunction({ data: { inputText } })`.
    Response: `{ "code": 0, "data": { summary, todos, risks, reply } }` or `{ "code", "message" }`.
    """
    return await summarize_chat(body.inputText)


@app.post(
    "/prepare-consult",
    response_model=PrepareConsultEnvelope,
    response_model_exclude_none=True,
)
@app.post(
    "/medical-assistant",
    response_model=PrepareConsultEnvelope,
    response_model_exclude_none=True,
)
async def prepare_consult_route(body: PrepareConsultRequest) -> PrepareConsultEnvelope:
    """
    对齐 `prepareConsult` 云函数：symptom / report / target。
    `/medical-assistant` 与 `/prepare-consult` 相同，供 Nginx 剥掉 `/api` 后路径为 /medical-assistant 时使用。
    """
    return await prepare_consult(body.symptom, body.report, body.target)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
