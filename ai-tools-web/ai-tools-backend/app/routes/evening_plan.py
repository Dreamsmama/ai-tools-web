from __future__ import annotations

from fastapi import APIRouter

from app.services.evening_plan_service import evening_plan_recommend
from app.schemas import EveningPlanEnvelope, EveningPlanRequest

router = APIRouter(tags=["evening-plan"])


@router.post(
    "/evening-plan",
    response_model=EveningPlanEnvelope,
    response_model_exclude_none=True,
)
async def evening_plan(body: EveningPlanRequest) -> EveningPlanEnvelope:
    return await evening_plan_recommend(body)
