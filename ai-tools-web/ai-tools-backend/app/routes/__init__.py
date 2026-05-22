"""HTTP route handlers and unified router registration."""

from __future__ import annotations

from fastapi import FastAPI

from app.ai_short_drama.router import router as ai_short_drama_router
from app.routes.evening_plan import router as evening_plan_router
from app.routes.health import router as health_router
from app.routes.interest_explorer import router as interest_explorer_router
from app.routes.life_rpg import router as life_rpg_router
from app.routes.medical import router as medical_router
from app.routes.memory import router as memory_router
from app.routes.model_compare import router as model_compare_router
from app.routes.offer_decision import router as offer_decision_router
from app.routes.rag import router as rag_router
from app.routes.summary import router as summary_router
from app.routes.xiaohongshu_agent import router as xiaohongshu_agent_router
from app.routes.track import router as track_router


def register_routes(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(summary_router)
    app.include_router(offer_decision_router)
    app.include_router(evening_plan_router)
    app.include_router(interest_explorer_router)
    app.include_router(life_rpg_router)
    app.include_router(medical_router)
    app.include_router(model_compare_router)
    app.include_router(memory_router)
    app.include_router(xiaohongshu_agent_router)
    app.include_router(rag_router)
    app.include_router(track_router)
    app.include_router(ai_short_drama_router)
