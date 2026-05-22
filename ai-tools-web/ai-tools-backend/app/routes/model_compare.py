from __future__ import annotations

from fastapi import APIRouter

from app.services.model_compare_service import compare_model_output
from app.schemas import ModelCompareEnvelope, ModelCompareRequest

router = APIRouter(tags=["model-compare"])


@router.post(
    "/model-compare",
    response_model=ModelCompareEnvelope,
    response_model_exclude_none=True,
)
async def model_compare(body: ModelCompareRequest) -> ModelCompareEnvelope:
    return await compare_model_output(body.input)
