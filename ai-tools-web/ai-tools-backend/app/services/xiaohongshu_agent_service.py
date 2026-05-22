"""
小红书内容生产 Agent Flow (orchestration only; steps & config in app.agents.xiaohongshu).
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx

from app.agents.xiaohongshu.spec import (
    ALLOWED_STYLES,
    LLM_PIPELINE,
    OPTIONAL_TOOL_STEPS,
    assemble_response_data,
    pipeline_step_ids,
    step_labels,
)
from app.agents.xiaohongshu.steps import PipelineContext, StepRunners, default_step_runners
from app.validators.content_output import validate_xiaohongshu_output
from app.utils import user_messages as user_msg
from app.schemas import XiaohongshuAgentEnvelope
from app.services.xiaohongshu_agent_sse import format_sse_message

logger = logging.getLogger(__name__)

_T = TypeVar("_T")

ProgressCallback = Callable[[dict[str, Any]], Awaitable[None]]

STEP_LABELS = step_labels()


async def _emit_progress(
    callback: ProgressCallback | None,
    *,
    phase: str,
    step: str,
    index: int,
    total: int,
    elapsed_ms: int | None = None,
) -> None:
    if not callback:
        return
    payload: dict[str, Any] = {
        "type": "step",
        "phase": phase,
        "step": step,
        "index": index,
        "total": total,
        "label": STEP_LABELS.get(step, step),
    }
    if elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms
    await callback(payload)


async def _logged_step(
    step: str,
    awaitable: Awaitable[_T],
    *,
    progress: ProgressCallback | None = None,
    step_index: int = 0,
    step_total: int = 0,
) -> _T:
    """Record per-step latency for production troubleshooting (R1)."""
    if step_total > 0:
        await _emit_progress(
            progress,
            phase="start",
            step=step,
            index=step_index,
            total=step_total,
        )
    started = time.perf_counter()
    try:
        result = await awaitable
        elapsed = time.perf_counter() - started
        logger.info(
            "xiaohongshu_agent step=%s elapsed=%.2fs status=ok",
            step,
            elapsed,
        )
        if step_total > 0:
            await _emit_progress(
                progress,
                phase="done",
                step=step,
                index=step_index,
                total=step_total,
                elapsed_ms=int(elapsed * 1000),
            )
        return result
    except Exception:
        elapsed = time.perf_counter() - started
        logger.info(
            "xiaohongshu_agent step=%s elapsed=%.2fs status=failed",
            step,
            elapsed,
        )
        if step_total > 0:
            await _emit_progress(
                progress,
                phase="failed",
                step=step,
                index=step_index,
                total=step_total,
                elapsed_ms=int(elapsed * 1000),
            )
        raise


class ImageProvider:
    """Extension point for image generation (see JimengImageProvider)."""

    async def generate(self, prompts: list[str]) -> list[str]:
        return []


class JimengImageProvider(ImageProvider):
    """Generate xiaohongshu note images via Jimeng (R7)."""

    async def generate(self, prompts: list[str]) -> list[str]:
        from app.providers.xiaohongshu_image_provider import generate_xiaohongshu_images

        return await generate_xiaohongshu_images(prompts)


class VideoProvider:
    """Reserved extension point for video generation."""

    async def generate(self, script: str) -> list[str]:
        return []


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


def _clamp_count(count: int) -> int:
    try:
        n = int(count)
    except (TypeError, ValueError):
        return 3
    return max(1, min(10, n))


@dataclass
class XiaohongshuAgentService:
    runners: StepRunners
    image_provider: ImageProvider | None = None
    video_provider: VideoProvider | None = None

    async def run(
        self,
        topic: str,
        product: str,
        audience: str,
        style: str,
        count: int,
        generate_images: bool = False,
        *,
        progress: ProgressCallback | None = None,
    ) -> XiaohongshuAgentEnvelope:
        return await self._run_core(
            topic,
            product,
            audience,
            style,
            count,
            generate_images,
            progress=progress,
        )

    async def _run_core(
        self,
        topic: str,
        product: str,
        audience: str,
        style: str,
        count: int,
        generate_images: bool,
        *,
        progress: ProgressCallback | None = None,
    ) -> XiaohongshuAgentEnvelope:
        topic = _safe_trim(topic)
        if not topic:
            logger.info("xiaohongshu_agent total=0.00s code=400 reason=empty_topic")
            return XiaohongshuAgentEnvelope(code=400, message="请先填写内容主题。")

        normalized_style = _safe_trim(style) or "种草"
        if normalized_style not in ALLOWED_STYLES:
            normalized_style = "种草"
        normalized_count = _clamp_count(count)

        total_started = time.perf_counter()
        product_s = _safe_trim(product)
        audience_s = _safe_trim(audience)
        step_ids = pipeline_step_ids(generate_images=generate_images)
        step_total = len(step_ids)

        def _idx(step_id: str) -> int:
            return step_ids.index(step_id) + 1

        ctx = PipelineContext(
            topic=topic,
            product=product_s,
            audience=audience_s,
            style=normalized_style,
            count=normalized_count,
            outputs={},
        )

        try:
            for step_spec in LLM_PIPELINE:
                output = await _logged_step(
                    step_spec.id,
                    self.runners.run_llm_step(step_spec.id, ctx),
                    progress=progress,
                    step_index=_idx(step_spec.id),
                    step_total=step_total,
                )
                ctx.outputs[step_spec.id] = output

            raw_data = assemble_response_data(ctx.outputs, normalized_count)
            data, _validator_fixes = validate_xiaohongshu_output(raw_data, normalized_count)

            image_urls: list[str] = []
            if generate_images and self.image_provider and data.image_prompts:
                tool_spec = OPTIONAL_TOOL_STEPS[0]
                image_urls = await _logged_step(
                    tool_spec.id,
                    self.image_provider.generate(data.image_prompts),
                    progress=progress,
                    step_index=_idx(tool_spec.id),
                    step_total=step_total,
                )
                image_urls = [u for u in image_urls if u]

            if not data.titles and not data.content and not data.image_prompts:
                logger.info(
                    "xiaohongshu_agent total=%.2fs code=500 reason=empty_result",
                    time.perf_counter() - total_started,
                )
                return XiaohongshuAgentEnvelope(code=500, message="未生成到可用结果，请重试。")

            logger.info(
                "xiaohongshu_agent total=%.2fs code=0 style=%s count=%s",
                time.perf_counter() - total_started,
                normalized_style,
                normalized_count,
            )
            return XiaohongshuAgentEnvelope(
                code=0,
                data=data.model_copy(update={"image_urls": image_urls}),
            )
        except httpx.TimeoutException:
            logger.exception("xiaohongshu_agent timeout")
            logger.info(
                "xiaohongshu_agent total=%.2fs code=504 reason=timeout",
                time.perf_counter() - total_started,
            )
            return XiaohongshuAgentEnvelope(code=504, message=user_msg.msg_timeout())
        except ValueError:
            logger.exception("xiaohongshu_agent invalid json")
            logger.info(
                "xiaohongshu_agent total=%.2fs code=500 reason=invalid_json",
                time.perf_counter() - total_started,
            )
            return XiaohongshuAgentEnvelope(
                code=500,
                message="模型返回格式异常，请重试。如连续失败，请稍后再试。",
            )
        except Exception as err:
            logger.exception("xiaohongshu_agent error")
            low = str(err).lower() if err else ""
            if "timeout" in low:
                logger.info(
                    "xiaohongshu_agent total=%.2fs code=504 reason=timeout",
                    time.perf_counter() - total_started,
                )
                return XiaohongshuAgentEnvelope(code=504, message=user_msg.msg_timeout())
            logger.info(
                "xiaohongshu_agent total=%.2fs code=500 reason=error",
                time.perf_counter() - total_started,
            )
            return XiaohongshuAgentEnvelope(code=500, message=user_msg.from_exception(err))

    async def iter_sse(
        self,
        topic: str,
        product: str,
        audience: str,
        style: str,
        count: int,
        generate_images: bool = False,
    ) -> AsyncIterator[str]:
        """Yield Server-Sent Events for step progress and final envelope (R8)."""
        queue: asyncio.Queue[tuple[str, Any] | None] = asyncio.Queue()

        async def on_progress(payload: dict[str, Any]) -> None:
            await queue.put(("progress", payload))

        async def worker() -> None:
            try:
                envelope = await self._run_core(
                    topic,
                    product,
                    audience,
                    style,
                    count,
                    generate_images,
                    progress=on_progress,
                )
                await queue.put(("result", envelope))
            except Exception as err:
                logger.exception("xiaohongshu_agent sse worker error")
                await queue.put(
                    (
                        "result",
                        XiaohongshuAgentEnvelope(
                            code=500,
                            message=user_msg.from_exception(err),
                        ),
                    )
                )
            finally:
                await queue.put(None)

        task = asyncio.create_task(worker())
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                kind, payload = item
                if kind == "progress":
                    yield format_sse_message("progress", payload)
                elif kind == "result":
                    body = (
                        payload.model_dump()
                        if isinstance(payload, XiaohongshuAgentEnvelope)
                        else payload
                    )
                    yield format_sse_message("result", body)
        finally:
            await task


xiaohongshu_agent_service = XiaohongshuAgentService(
    runners=default_step_runners,
    image_provider=JimengImageProvider(),
    video_provider=VideoProvider(),
)
