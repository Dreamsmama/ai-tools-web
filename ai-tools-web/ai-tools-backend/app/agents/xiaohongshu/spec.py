"""
Declarative pipeline config for xiaohongshu content agent (R9).

Edit step order, labels, prompt paths, and response field bindings here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from app.schemas import XiaohongshuAgentData
from app.utils.llm_json import lines_from_plain_text

ALLOWED_STYLES = frozenset({"种草", "干货", "情绪", "测评", "清单"})


@dataclass(frozen=True)
class LlmStepSpec:
    """One LLM call in the five-step pipeline."""

    id: str
    label: str
    output_fields: tuple[str, ...]
    system_prompt: str | None = None
    user_prompt: str | None = None
    system_inline: str | None = None
    skill: str | None = None


@dataclass(frozen=True)
class ToolStepSpec:
    """Non-LLM step (e.g. image generation), optional at runtime."""

    id: str
    label: str


@dataclass(frozen=True)
class ResponseFieldBinding:
    """Maps a pipeline step JSON key into ``XiaohongshuAgentData``."""

    field: str
    step_id: str
    json_key: str
    limit: int | None = None
    limit_from_count: bool = False


# --- Pipeline (order = execution order) ---

LLM_PIPELINE: tuple[LlmStepSpec, ...] = (
    LlmStepSpec(
        id="topic_analyzer",
        label="主题分析",
        system_prompt="topic_analyzer_system",
        user_prompt="topic_analyzer_user",
        output_fields=(
            "topic_focus",
            "value_points",
            "audience_insights",
            "tone_guidance",
            "style",
        ),
    ),
    LlmStepSpec(
        id="content_planner",
        label="内容规划",
        system_inline="你是内容规划助手。只输出严格 JSON。",
        output_fields=("positioning", "outline", "title_angles", "count"),
    ),
    LlmStepSpec(
        id="copywriter",
        label="文案撰写",
        system_prompt="copywriter_system",
        user_prompt="copywriter_user",
        output_fields=("titles", "content"),
    ),
    LlmStepSpec(
        id="image_prompt_generator",
        label="配图提示词",
        system_inline="你是图片提示词生成助手。严格输出 JSON。",
        output_fields=("image_prompts",),
    ),
    LlmStepSpec(
        id="risk_checker",
        label="合规检查",
        system_inline="你是内容合规检查助手。严格输出 JSON。",
        skill="content_compliance",
        output_fields=("publish_tips", "risks"),
    ),
)

OPTIONAL_TOOL_STEPS: tuple[ToolStepSpec, ...] = (
    ToolStepSpec(id="image_provider", label="配图生成"),
)

RESPONSE_BINDINGS: tuple[ResponseFieldBinding, ...] = (
    ResponseFieldBinding("titles", "copywriter", "titles", limit_from_count=True),
    ResponseFieldBinding("content", "copywriter", "content"),
    ResponseFieldBinding(
        "image_prompts",
        "image_prompt_generator",
        "image_prompts",
        limit_from_count=True,
    ),
    ResponseFieldBinding("publish_tips", "risk_checker", "publish_tips", limit=5),
    ResponseFieldBinding("risks", "risk_checker", "risks", limit=5),
)

STEP_BY_ID: dict[str, LlmStepSpec | ToolStepSpec] = {
    **{s.id: s for s in LLM_PIPELINE},
    **{s.id: s for s in OPTIONAL_TOOL_STEPS},
}


def step_label(step_id: str) -> str:
    spec = STEP_BY_ID.get(step_id)
    return spec.label if spec else step_id


def step_labels() -> dict[str, str]:
    return {step_id: step_label(step_id) for step_id in STEP_BY_ID}


def pipeline_step_ids(*, generate_images: bool) -> list[str]:
    ids = [s.id for s in LLM_PIPELINE]
    if generate_images:
        ids.extend(s.id for s in OPTIONAL_TOOL_STEPS)
    return ids


def _list_of_str(obj: dict[str, Any], key: str, fallback_text: str = "") -> list[str]:
    raw = obj.get(key)
    if isinstance(raw, list):
        items = [str(x).strip() for x in raw if str(x).strip()]
        if items:
            return items
    if fallback_text:
        lines = lines_from_plain_text(fallback_text, max_lines=5)
        if lines:
            return lines
    return []


def _str_value(obj: dict[str, Any], key: str, fallback_text: str = "") -> str:
    raw = obj.get(key)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    if fallback_text:
        return fallback_text.strip()[:1200]
    return ""


def assemble_response_data(
    outputs: dict[str, dict[str, Any]],
    count: int,
) -> XiaohongshuAgentData:
    """Merge per-step JSON into the API response model (see RESPONSE_BINDINGS)."""
    kwargs: dict[str, Any] = {}
    for binding in RESPONSE_BINDINGS:
        step_out = outputs.get(binding.step_id) or {}
        if binding.field in ("titles", "image_prompts", "publish_tips", "risks"):
            items = _list_of_str(step_out, binding.json_key)
            cap = count if binding.limit_from_count else binding.limit
            kwargs[binding.field] = items[:cap] if cap else items
        else:
            kwargs[binding.field] = _str_value(step_out, binding.json_key)
    return XiaohongshuAgentData(**kwargs)
