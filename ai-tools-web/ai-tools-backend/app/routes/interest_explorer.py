from __future__ import annotations

from fastapi import APIRouter

from app.services.interest_explorer_service import interest_explorer_recommend
from app.schemas import InterestExplorerEnvelope, InterestExplorerRequest

router = APIRouter(tags=["interest-explorer"])


@router.post(
    "/interest-explorer",
    response_model=InterestExplorerEnvelope,
    response_model_exclude_none=True,
)
async def interest_explorer(body: InterestExplorerRequest) -> InterestExplorerEnvelope:
    return await interest_explorer_recommend(body)
