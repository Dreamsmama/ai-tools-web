from __future__ import annotations

from fastapi import APIRouter

from app.services.offer_decision_service import offer_decision_analyze
from app.schemas import OfferDecisionEnvelope, OfferDecisionRequest

router = APIRouter(tags=["offer-decision"])


@router.post(
    "/offer-decision",
    response_model=OfferDecisionEnvelope,
    response_model_exclude_none=True,
)
async def offer_decision(body: OfferDecisionRequest) -> OfferDecisionEnvelope:
    return await offer_decision_analyze(body.input_text)
