from __future__ import annotations

from fastapi import APIRouter

from app.services.prepare_consult_service import prepare_consult
from app.schemas import PrepareConsultEnvelope, PrepareConsultRequest

router = APIRouter(tags=["medical"])


@router.post(
    "/prepare-consult",
    response_model=PrepareConsultEnvelope,
    response_model_exclude_none=True,
)
@router.post(
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
