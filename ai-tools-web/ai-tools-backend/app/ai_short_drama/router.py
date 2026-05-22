from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter

from app.ai_short_drama.character_ip_api import character_ip_router
from app.ai_short_drama.materials_api import materials_router
from app.ai_short_drama.render_video_service import _resolve_render_shots, render_short_drama_video
from app.ai_short_drama.bgm import BGM_CATALOG, list_bgm_files
from app.ai_short_drama.schemas import (
    AiShortDramaEnvelope,
    AiShortDramaRequest,
    RenderVideoEnvelope,
    RenderVideoRequest,
)
from app.ai_short_drama.service import generate_short_drama
from app.ai_short_drama.tts_service import VOICE_OPTIONS, synthesize_all_segments

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-short-drama", tags=["ai-short-drama"])
router.include_router(materials_router)
router.include_router(character_ip_router)


@router.get("/bgm-tracks")
async def ai_short_drama_bgm_tracks():
    """返回可用 BGM 曲目列表（供前端手动选择）。"""
    files = list_bgm_files()
    tracks = [t for t in BGM_CATALOG if t["file"] in files] or list(BGM_CATALOG)
    return {"code": 0, "data": {"tracks": tracks, "files": files}}


@router.get("/voice-options")
async def ai_short_drama_voice_options():
    """返回可用配音音色列表。"""
    options = [{"id": vid, "label": label} for label, vid in VOICE_OPTIONS.items()]
    return {"code": 0, "data": {"voices": options}}


@router.post(
    "/generate",
    response_model=AiShortDramaEnvelope,
    response_model_exclude_none=True,
)
async def ai_short_drama_generate(body: AiShortDramaRequest) -> AiShortDramaEnvelope:
    logger.info("[generate] request received params=%s", body.model_dump())
    try:
        envelope = await generate_short_drama(body)
        logger.info(
            "[generate] response returned code=%s success=%s",
            envelope.code,
            envelope.success,
        )
        return envelope
    except Exception as err:
        logger.exception("[generate] unhandled error: %s", err)
        return AiShortDramaEnvelope(
            code=500,
            success=False,
            message=str(err) or "生成失败",
            stage="unknown",
            data=None,
        )


@router.post(
    "/render-video",
    response_model=RenderVideoEnvelope,
    response_model_exclude_none=True,
)
async def ai_short_drama_render_video(body: RenderVideoRequest) -> RenderVideoEnvelope:
    """FFmpeg 合成在子线程执行，避免阻塞其它 API（单 worker 下否则全站卡住）。"""
    try:
        voice_paths = None
        if body.voice_id:
            from app.config.settings import settings as _settings
            if not _settings.dashscope_api_key:
                return RenderVideoEnvelope(
                    code=400,
                    message="配音功能需要配置 DASHSCOPE_API_KEY，当前未配置。",
                )
            shots = _resolve_render_shots(body)
            texts = [s.subtitle or "" for s in shots]
            durations = [float(s.duration) for s in shots]
            if texts:
                logger.info(
                    "[render] TTS 首段: len=%d text=%r",
                    len(texts[0].strip()),
                    texts[0].strip()[:60],
                )
            from pathlib import Path
            from app.ai_short_drama.render_video_service import GENERATED_DIR
            import uuid as _uuid
            tts_dir = GENERATED_DIR / f"tts_{_uuid.uuid4().hex[:8]}"
            logger.info("[render] 开始 TTS 配音 voice=%s segments=%d", body.voice_id, len(texts))
            voice_paths = await synthesize_all_segments(texts, durations, body.voice_id, tts_dir)
            logger.info("[render] TTS 完成 %d/%d", sum(1 for p in voice_paths if p), len(voice_paths))

        return await asyncio.to_thread(render_short_drama_video, body, voice_paths)
    except Exception as err:
        logger.exception("[render] unhandled error: %s", err)
        return RenderVideoEnvelope(
            code=500,
            message=str(err) or "视频生成失败",
        )
