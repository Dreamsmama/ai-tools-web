from __future__ import annotations

from fastapi import APIRouter

from app.services.life_rpg_service import life_rpg_create_route, life_rpg_daily_generate
from app.schemas import (
    LifeRpgCreateRouteRequest,
    LifeRpgDailyRequest,
    LifeRpgEnvelope,
    LifeRpgRouteEnvelope,
)

router = APIRouter(tags=["life-rpg"])


@router.post(
    "/life-rpg/create-route",
    response_model=LifeRpgRouteEnvelope,
    response_model_exclude_none=True,
)
async def life_rpg_create_route_api(body: LifeRpgCreateRouteRequest) -> LifeRpgRouteEnvelope:
    return await life_rpg_create_route(body)


@router.post(
    "/life-rpg/daily",
    response_model=LifeRpgEnvelope,
    response_model_exclude_none=True,
)
async def life_rpg_daily(body: LifeRpgDailyRequest) -> LifeRpgEnvelope:
    return await life_rpg_daily_generate(body)
