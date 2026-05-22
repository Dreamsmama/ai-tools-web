from __future__ import annotations

from fastapi import APIRouter

from app.services.memory_compare_service import memory_compare
from app.schemas import MemoryCompareEnvelope, MemoryCompareRequest

router = APIRouter(tags=["memory"])


@router.post(
    "/memory/compare",
    response_model=MemoryCompareEnvelope,
    response_model_exclude_none=True,
)
async def compare_memory_answer(body: MemoryCompareRequest) -> MemoryCompareEnvelope:
    return await memory_compare(body.chat_content, body.question)
