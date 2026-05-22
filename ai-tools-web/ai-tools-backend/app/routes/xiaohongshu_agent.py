from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import XiaohongshuAgentEnvelope, XiaohongshuAgentRequest
from app.services.xiaohongshu_agent_service import xiaohongshu_agent_service

router = APIRouter(tags=["xiaohongshu-agent"])


@router.post(
    "/tools/xiaohongshu-agent/generate",
    response_model=XiaohongshuAgentEnvelope,
    response_model_exclude_none=True,
)
async def xiaohongshu_agent_generate(
    body: XiaohongshuAgentRequest,
) -> XiaohongshuAgentEnvelope:
    return await xiaohongshu_agent_service.run(
        topic=body.topic,
        product=body.product,
        audience=body.audience,
        style=body.style,
        count=body.count,
        generate_images=body.generate_images,
    )


@router.post("/tools/xiaohongshu-agent/generate-stream")
async def xiaohongshu_agent_generate_stream(
    body: XiaohongshuAgentRequest,
) -> StreamingResponse:
    """SSE：推送步骤进度（progress）与最终结果（result）。"""

    async def event_stream():
        async for chunk in xiaohongshu_agent_service.iter_sse(
            topic=body.topic,
            product=body.product,
            audience=body.audience,
            style=body.style,
            count=body.count,
            generate_images=body.generate_images,
        ):
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
