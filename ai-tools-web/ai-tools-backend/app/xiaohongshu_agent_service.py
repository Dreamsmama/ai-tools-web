"""
小红书内容生产 Agent Flow:
topic -> plan -> copywriting -> image prompts -> risk check -> final result
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app import user_messages as user_msg
from app.llm_json import lines_from_plain_text, try_parse_json_object
from app.schemas import XiaohongshuAgentData, XiaohongshuAgentEnvelope
from app.summarize_service import _call_dashscope

logger = logging.getLogger(__name__)

ALLOWED_STYLES = {"种草", "干货", "情绪", "测评", "清单"}


class ImageProvider:
    """Reserved extension point for image generation."""

    async def generate(self, prompts: list[str]) -> list[str]:
        return []


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


def _parse_json_or_raise(raw: str) -> dict[str, Any]:
    obj = try_parse_json_object(raw)
    if obj is None:
        raise ValueError("模型返回内容不是合法 JSON")
    return obj


@dataclass
class TopicAnalyzer:
    async def run(self, topic: str, product: str, audience: str, style: str) -> dict[str, Any]:
        system_message = {
            "role": "system",
            "content": (
                "你是内容策略分析助手。"
                "只输出严格 JSON，不要 markdown，不要多余文本。"
            ),
        }
        user_message = {
            "role": "user",
            "content": f"""
请基于输入做小红书内容方向分析，只返回 JSON：
{{
  "topic_focus": "...",
  "value_points": ["..."],
  "audience_insights": ["..."],
  "tone_guidance": ["..."],
  "style": "{style}"
}}

输入：
- topic: {topic}
- product: {product or "未提供"}
- audience: {audience or "未提供"}
- style: {style}
""".strip(),
        }
        raw = await _call_dashscope([system_message, user_message])
        return _parse_json_or_raise(raw)


@dataclass
class ContentPlanner:
    async def run(self, analysis: dict[str, Any], count: int) -> dict[str, Any]:
        system_message = {
            "role": "system",
            "content": "你是内容规划助手。只输出严格 JSON。",
        }
        user_message = {
            "role": "user",
            "content": f"""
根据分析结果产出内容结构规划，只返回 JSON：
{{
  "positioning": "...",
  "outline": ["开头钩子", "核心价值", "行动引导"],
  "title_angles": ["角度1", "角度2"],
  "count": {count}
}}

analysis={analysis}
""".strip(),
        }
        raw = await _call_dashscope([system_message, user_message])
        return _parse_json_or_raise(raw)


@dataclass
class Copywriter:
    async def run(self, analysis: dict[str, Any], plan: dict[str, Any], count: int) -> dict[str, Any]:
        system_message = {
            "role": "system",
            "content": "你是小红书文案助手。严格输出 JSON。",
        }
        user_message = {
            "role": "user",
            "content": f"""
基于 analysis + plan 生成文案，只返回 JSON：
{{
  "titles": ["标题1", "标题2"],
  "content": "正文文案，包含自然换行"
}}

要求：
- titles 数量为 {count}
- 标题要口语化、可发布
- 正文 220~420 字，结构清楚，有行动引导

analysis={analysis}
plan={plan}
""".strip(),
        }
        raw = await _call_dashscope([system_message, user_message])
        return _parse_json_or_raise(raw)


@dataclass
class ImagePromptGenerator:
    async def run(self, analysis: dict[str, Any], copywriting: dict[str, Any], count: int) -> dict[str, Any]:
        system_message = {
            "role": "system",
            "content": "你是图片提示词生成助手。严格输出 JSON。",
        }
        user_message = {
            "role": "user",
            "content": f"""
基于文案生成图片提示词，只返回 JSON：
{{
  "image_prompts": ["提示词1", "提示词2"]
}}

要求：
- 生成 {count} 条中文提示词
- 每条包含：主体、场景、风格、光线、构图关键词

analysis={analysis}
copywriting={copywriting}
""".strip(),
        }
        raw = await _call_dashscope([system_message, user_message])
        return _parse_json_or_raise(raw)


@dataclass
class RiskChecker:
    async def run(self, copywriting: dict[str, Any]) -> dict[str, Any]:
        system_message = {
            "role": "system",
            "content": "你是内容合规检查助手。严格输出 JSON。",
        }
        user_message = {
            "role": "user",
            "content": f"""
检查文案是否存在夸大、违规、医疗/金融/绝对化表达风险，只返回 JSON：
{{
  "publish_tips": ["发布建议1", "发布建议2"],
  "risks": ["注意事项1", "注意事项2"]
}}

copywriting={copywriting}
""".strip(),
        }
        raw = await _call_dashscope([system_message, user_message])
        return _parse_json_or_raise(raw)


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


@dataclass
class XiaohongshuAgentService:
    topic_analyzer: TopicAnalyzer
    content_planner: ContentPlanner
    copywriter: Copywriter
    image_prompt_generator: ImagePromptGenerator
    risk_checker: RiskChecker
    image_provider: ImageProvider | None = None
    video_provider: VideoProvider | None = None

    async def run(
        self,
        topic: str,
        product: str,
        audience: str,
        style: str,
        count: int,
    ) -> XiaohongshuAgentEnvelope:
        topic = _safe_trim(topic)
        if not topic:
            return XiaohongshuAgentEnvelope(code=400, message="请先填写内容主题。")

        normalized_style = _safe_trim(style) or "种草"
        if normalized_style not in ALLOWED_STYLES:
            normalized_style = "种草"
        normalized_count = _clamp_count(count)

        try:
            analysis = await self.topic_analyzer.run(topic, _safe_trim(product), _safe_trim(audience), normalized_style)
            plan = await self.content_planner.run(analysis, normalized_count)
            copywriting = await self.copywriter.run(analysis, plan, normalized_count)
            image_prompt_data = await self.image_prompt_generator.run(analysis, copywriting, normalized_count)
            risk_data = await self.risk_checker.run(copywriting)

            data = XiaohongshuAgentData(
                titles=_list_of_str(copywriting, "titles")[:normalized_count],
                content=_str_value(copywriting, "content"),
                image_prompts=_list_of_str(image_prompt_data, "image_prompts")[:normalized_count],
                publish_tips=_list_of_str(risk_data, "publish_tips")[:5],
                risks=_list_of_str(risk_data, "risks")[:5],
            )
            if not data.titles and not data.content and not data.image_prompts:
                return XiaohongshuAgentEnvelope(code=500, message="未生成到可用结果，请重试。")

            return XiaohongshuAgentEnvelope(code=0, data=data)
        except httpx.TimeoutException:
            logger.exception("xiaohongshu_agent timeout")
            return XiaohongshuAgentEnvelope(code=504, message=user_msg.msg_timeout())
        except ValueError:
            logger.exception("xiaohongshu_agent invalid json")
            return XiaohongshuAgentEnvelope(
                code=500,
                message="模型返回格式异常，请重试。如连续失败，请稍后再试。",
            )
        except Exception as err:
            logger.exception("xiaohongshu_agent error")
            low = str(err).lower() if err else ""
            if "timeout" in low:
                return XiaohongshuAgentEnvelope(code=504, message=user_msg.msg_timeout())
            return XiaohongshuAgentEnvelope(code=500, message=user_msg.from_exception(err))


xiaohongshu_agent_service = XiaohongshuAgentService(
    topic_analyzer=TopicAnalyzer(),
    content_planner=ContentPlanner(),
    copywriter=Copywriter(),
    image_prompt_generator=ImagePromptGenerator(),
    risk_checker=RiskChecker(),
    image_provider=ImageProvider(),
    video_provider=VideoProvider(),
)

