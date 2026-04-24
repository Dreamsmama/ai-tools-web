from __future__ import annotations

import json
import logging

import httpx

from app import user_messages as user_msg
from app.config import settings
from app.schemas import ModelCompareData, ModelCompareEnvelope
from app.summarize_service import _call_dashscope

logger = logging.getLogger(__name__)


def _safe_trim(v: object) -> str:
    return v.strip() if isinstance(v, str) else ""


def _build_structured_prompt(input_text: str) -> list[dict[str, str]]:
    system_message = {
        "role": "system",
        "content": (
            "你是优化后的模型。请按固定结构输出，且不要输出结构之外内容。"
            "禁止使用 markdown 标题、列表序号、代码块。"
        ),
    }
    user_message = {
        "role": "user",
        "content": (
            f"输入内容：{input_text}\n\n"
            "请严格按以下格式输出：\n"
            "【核心问题】\n"
            "一句话概括核心问题\n\n"
            "【分析】\n"
            "给出2-4条简洁分析\n\n"
            "【建议】\n"
            "给出2-4条可执行建议"
        ),
    }
    return [system_message, user_message]


def _normalize_optimized_output(text: str) -> str:
    raw = _safe_trim(text)
    if not raw:
        return raw

    if "【核心问题】" in raw and "【分析】" in raw and "【建议】" in raw:
        return raw

    # 微调模型有时会输出 JSON；这里统一转换为三段文本，避免页面观感混乱。
    try:
        obj = json.loads(raw)
    except Exception:
        obj = None

    if isinstance(obj, dict):
        core = (
            obj.get("核心问题")
            or obj.get("core_problem")
            or obj.get("问题")
            or obj.get("summary")
            or "未明确"
        )
        analysis = obj.get("分析") or obj.get("analysis") or obj.get("原因") or ""
        advice = obj.get("建议") or obj.get("advice") or obj.get("方案") or ""

        if isinstance(analysis, list):
            analysis_text = "\n".join(f"- {str(item).strip()}" for item in analysis if str(item).strip())
        else:
            analysis_text = str(analysis).strip()

        if isinstance(advice, list):
            advice_text = "\n".join(f"- {str(item).strip()}" for item in advice if str(item).strip())
        else:
            advice_text = str(advice).strip()

        return (
            f"【核心问题】\n{str(core).strip()}\n\n"
            f"【分析】\n{analysis_text or '未明确'}\n\n"
            f"【建议】\n{advice_text or '未明确'}"
        )

    return (
        "【核心问题】\n"
        "模型未按约定结构输出，以下为原始结果。\n\n"
        "【分析】\n"
        "输出格式不稳定，可能与当前模型权重或提示词遵循度有关。\n\n"
        "【建议】\n"
        "请扩充结构化样本继续训练，或提高该格式在训练集中的占比。\n\n"
        f"原始输出：\n{raw}"
    )


async def call_original_model(input_text: str) -> str:
    system_message = {
        "role": "system",
        "content": "你是一个可靠的中文 AI 助手，请基于输入给出清晰回答。",
    }
    user_message = {"role": "user", "content": input_text}
    return await _call_dashscope([system_message, user_message])


async def call_optimized_model(input_text: str) -> str:
    optimized_model = settings.dashscope_optimized_model.strip()
    if optimized_model:
        raw = await _call_dashscope(_build_structured_prompt(input_text), model=optimized_model)
        return _normalize_optimized_output(raw)

    raw = await _call_dashscope(_build_structured_prompt(input_text))
    return _normalize_optimized_output(raw)


async def compare_model_output(input_text: str) -> ModelCompareEnvelope:
    text = _safe_trim(input_text)
    if not text:
        return ModelCompareEnvelope(code=400, message=user_msg.msg_input_empty())

    try:
        original_output = await call_original_model(text)
        optimized_output = await call_optimized_model(text)
        mode = "fine_tuned" if settings.dashscope_optimized_model.strip() else "placeholder"
        return ModelCompareEnvelope(
            code=0,
            data=ModelCompareData(
                original_output=original_output,
                optimized_output=optimized_output,
                mode=mode,
            ),
        )
    except httpx.TimeoutException:
        logger.exception("model_compare timeout")
        return ModelCompareEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("model_compare error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return ModelCompareEnvelope(code=504, message=user_msg.msg_timeout())
        return ModelCompareEnvelope(code=500, message=user_msg.from_exception(err))
