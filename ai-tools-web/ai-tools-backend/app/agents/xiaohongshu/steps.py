"""LLM step runners for xiaohongshu agent (prompts driven by spec.py, R9)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.agents.xiaohongshu.prompt_loader import load_prompt
from app.agents.xiaohongshu.spec import LlmStepSpec, STEP_BY_ID
from app.llm.dashscope_client import call_dashscope
from app.skills.content_compliance.code import scan_copywriting
from app.skills.loader import load_skill_markdown
from app.utils.llm_json import try_parse_json_object


def _parse_json_or_raise(raw: str) -> Dict[str, Any]:
    obj = try_parse_json_object(raw)
    if obj is None:
        raise ValueError("模型返回内容不是合法 JSON")
    return obj


def _llm_spec(step_id: str) -> LlmStepSpec:
    spec = STEP_BY_ID.get(step_id)
    if not isinstance(spec, LlmStepSpec):
        raise KeyError(f"Unknown LLM step: {step_id}")
    return spec


@dataclass
class PipelineContext:
    topic: str
    product: str
    audience: str
    style: str
    count: int
    outputs: Dict[str, Dict[str, Any]]

    def analysis(self) -> Dict[str, Any]:
        return self.outputs["topic_analyzer"]

    def plan(self) -> Dict[str, Any]:
        return self.outputs["content_planner"]

    def copywriting(self) -> Dict[str, Any]:
        return self.outputs["copywriter"]


@dataclass
class TopicAnalyzer:
    async def run(self, topic: str, product: str, audience: str, style: str) -> Dict[str, Any]:
        spec = _llm_spec("topic_analyzer")
        messages = [
            {"role": "system", "content": load_prompt(spec.system_prompt or "")},
            {
                "role": "user",
                "content": load_prompt(
                    spec.user_prompt or "",
                    topic=topic,
                    product=product or "未提供",
                    audience=audience or "未提供",
                    style=style,
                ),
            },
        ]
        return _parse_json_or_raise(await call_dashscope(messages))


@dataclass
class ContentPlanner:
    async def run(self, analysis: Dict[str, Any], count: int) -> Dict[str, Any]:
        spec = _llm_spec("content_planner")
        messages = [
            {"role": "system", "content": spec.system_inline or ""},
            {
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
            },
        ]
        return _parse_json_or_raise(await call_dashscope(messages))


@dataclass
class Copywriter:
    async def run(self, analysis: Dict[str, Any], plan: Dict[str, Any], count: int) -> Dict[str, Any]:
        spec = _llm_spec("copywriter")
        messages = [
            {"role": "system", "content": load_prompt(spec.system_prompt or "")},
            {
                "role": "user",
                "content": load_prompt(
                    spec.user_prompt or "",
                    count=count,
                    analysis=analysis,
                    plan=plan,
                ),
            },
        ]
        return _parse_json_or_raise(await call_dashscope(messages))


@dataclass
class ImagePromptGenerator:
    async def run(
        self,
        analysis: Dict[str, Any],
        copywriting: Dict[str, Any],
        count: int,
    ) -> Dict[str, Any]:
        spec = _llm_spec("image_prompt_generator")
        messages = [
            {"role": "system", "content": spec.system_inline or ""},
            {
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
            },
        ]
        return _parse_json_or_raise(await call_dashscope(messages))


@dataclass
class RiskChecker:
    async def run(self, copywriting: Dict[str, Any]) -> Dict[str, Any]:
        spec = _llm_spec("risk_checker")
        scan = scan_copywriting(copywriting)
        skill_block = load_skill_markdown(spec.skill or "content_compliance")
        scan_hint = ""
        if scan.get("sensitive_hits"):
            scan_hint = (
                "\n\n【规则引擎预检】文案命中敏感词："
                + "、".join(scan["sensitive_hits"])
                + "。请在 risks 中说明，并在 publish_tips 中给出修改建议。"
            )
        messages = [
            {
                "role": "system",
                "content": f"{spec.system_inline or ''}\n\n{skill_block}",
            },
            {
                "role": "user",
                "content": f"""
检查文案是否存在夸大、违规、医疗/金融/绝对化表达风险，只返回 JSON：
{{
  "publish_tips": ["发布建议1", "发布建议2"],
  "risks": ["注意事项1", "注意事项2"]
}}

copywriting={copywriting}{scan_hint}
""".strip(),
            },
        ]
        return _parse_json_or_raise(await call_dashscope(messages))


@dataclass
class StepRunners:
    topic_analyzer: TopicAnalyzer
    content_planner: ContentPlanner
    copywriter: Copywriter
    image_prompt_generator: ImagePromptGenerator
    risk_checker: RiskChecker

    async def run_llm_step(self, step_id: str, ctx: PipelineContext) -> Dict[str, Any]:
        if step_id == "topic_analyzer":
            return await self.topic_analyzer.run(
                ctx.topic, ctx.product, ctx.audience, ctx.style
            )
        if step_id == "content_planner":
            return await self.content_planner.run(ctx.analysis(), ctx.count)
        if step_id == "copywriter":
            return await self.copywriter.run(ctx.analysis(), ctx.plan(), ctx.count)
        if step_id == "image_prompt_generator":
            return await self.image_prompt_generator.run(
                ctx.analysis(), ctx.copywriting(), ctx.count
            )
        if step_id == "risk_checker":
            return await self.risk_checker.run(ctx.copywriting())
        raise KeyError(f"No runner for step: {step_id}")


default_step_runners = StepRunners(
    topic_analyzer=TopicAnalyzer(),
    content_planner=ContentPlanner(),
    copywriter=Copywriter(),
    image_prompt_generator=ImagePromptGenerator(),
    risk_checker=RiskChecker(),
)
