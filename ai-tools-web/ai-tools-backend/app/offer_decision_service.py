from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

import httpx

from app import user_messages as user_msg
from app.config import settings
from app.llm_json import parse_offer_decision_model_output
from app.schemas import OfferDecisionData, OfferDecisionEnvelope, OfferOptionInsight

logger = logging.getLogger(__name__)


def _safe_trim(v: Any) -> str:
    return v.strip() if isinstance(v, str) else ""


async def _call_dashscope(messages: List[Dict[str, str]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": settings.dashscope_model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": settings.dashscope_temperature,
            "max_tokens": settings.dashscope_max_tokens,
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(settings.dashscope_timeout_seconds)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(settings.dashscope_url, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()

    content = None
    try:
        choices = body.get("output", {}).get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content")
        if content is None:
            content = body.get("output", {}).get("text")
        if content is None and choices:
            content = choices[0].get("text")
    except (TypeError, IndexError, AttributeError):
        content = None

    if not content:
        snippet = json.dumps(body, ensure_ascii=False)[:500]
        raise RuntimeError(f"DashScope 返回为空或结构不匹配：{snippet}")
    return content if isinstance(content, str) else str(content)


async def offer_decision_analyze(input_text: str) -> OfferDecisionEnvelope:
    text = _safe_trim(input_text)
    if not text:
        return OfferDecisionEnvelope(code=400, message=user_msg.msg_input_empty())
    option_hints = _detect_option_hints(text)

    system_message = {
        "role": "system",
        "content": (
            "你是职场决策分析助手。目标是帮助用户理清 offer / 跳槽决策，不做算命、不绝对化。"
            "输出风格克制、真实，像有经验的人一起分析。"
            "只输出严格 JSON，不要 markdown，不要多余文本。"
        ),
    }
    user_message = {
        "role": "user",
        "content": f"""
请根据用户输入做职业决策分析，只返回 JSON：
{{
  "core_conflict": ["..."],
  "option_insights": [
    {{
      "option_name": "选择1",
      "stability": "...",
      "growth": "...",
      "risk": "...",
      "long_term_space": "...",
      "tech_value": "...",
      "team_industry_factor": "..."
    }}
  ],
  "blind_spots": ["..."],
  "regret_after_3_months": ["..."],
  "fit_by_choice": ["..."],
  "questions_to_confirm": ["..."],
  "recommendation": "..."
}}

要求：
- 不要假设只有 Offer A / Offer B。支持任意数量选择，或“工作 vs 读博/考公/创业”等路径。
- core_conflict：2~4条，不复述原话，提炼真正卡点
- option_insights：按用户输入中的每个选择分别分析；每项都写清稳定性/成长性/风险/长期空间/技术价值/团队或行业因素
- option_insights 必须具体到“这个选择”的真实代价和收益，不要写模板化空话
- blind_spots：2~4条，用户最容易忽略的问题
- regret_after_3_months：2~4条，必须是“具体后悔场景”，要写出触发条件与后果，不能空泛
- fit_by_choice：3~6条，说明“什么样的人更适合不同选择”
- questions_to_confirm：3~6条，用户还需向对方确认的问题
- recommendation：1段建议，不替用户做决定，不要推荐指数，不要“最佳选择/必须/一定”
- recommendation 要给出 48 小时内可执行动作（如先确认哪些变量、问谁、怎么对比），避免鸡汤化表达

我从用户输入里初步识别到的选择有：{json.dumps(option_hints, ensure_ascii=False)}
请尽量逐个覆盖这些选择（如识别有误可改名，但不要整体忽略）。

用户输入：
{text}
""".strip(),
    }

    try:
        raw = await _call_dashscope([system_message, user_message])
        data = _normalize_offer_decision_data(parse_offer_decision_model_output(raw), option_hints)
        if (
            not data.core_conflict
            and not data.option_insights
            and not data.blind_spots
            and not data.regret_after_3_months
            and not data.fit_by_choice
            and not data.questions_to_confirm
            and not data.recommendation
        ):
            return OfferDecisionEnvelope(code=500, message=user_msg.msg_model_empty())
        return OfferDecisionEnvelope(code=0, data=data)
    except httpx.TimeoutException:
        logger.exception("offer_decision timeout")
        return OfferDecisionEnvelope(code=504, message=user_msg.msg_timeout())
    except Exception as err:
        logger.exception("offer_decision error")
        low = str(err).lower() if err else ""
        if "timeout" in low:
            return OfferDecisionEnvelope(code=504, message=user_msg.msg_timeout())
        return OfferDecisionEnvelope(code=500, message=user_msg.from_exception(err))


def _normalize_offer_decision_data(
    data: OfferDecisionData, option_hints: List[str]
) -> OfferDecisionData:
    # Guarantee key sections are never blank in UI.
    option_insights = data.option_insights or _fallback_option_insights(option_hints)
    core_conflict = data.core_conflict or ["你在“长期竞争力”和“现实稳定性”之间拉扯，还没把优先级排清。"]
    blind_spots = data.blind_spots or ["你可能高估了短期标签收益，低估了日常节奏和协作环境的长期影响。"]
    regret_after_3_months = data.regret_after_3_months or _fallback_regret_points(option_hints)
    fit_by_choice = data.fit_by_choice or _fallback_fit_by_choice(option_hints)
    questions = data.questions_to_confirm or [
        "这个岗位前 3 个月的核心产出是什么？如何衡量是否达标？",
        "团队实际加班强度和周末工作频率如何？最近 3 个月是否有波动？",
        "期权授予、归属与离职处理规则是否能写进正式条款？",
    ]
    recommendation = data.recommendation.strip() if data.recommendation else ""
    if not recommendation:
        recommendation = _fallback_recommendation(core_conflict, option_hints)
    return data.model_copy(
        update={
            "option_insights": option_insights[:6],
            "core_conflict": core_conflict[:4],
            "blind_spots": blind_spots[:4],
            "regret_after_3_months": regret_after_3_months[:4],
            "fit_by_choice": fit_by_choice[:6],
            "questions_to_confirm": questions[:6],
            "recommendation": recommendation[:500],
        }
    )


def _detect_option_hints(text: str) -> List[str]:
    hints: List[str] = []
    for line in text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        m = re.match(r"^(?:[-*]\s*)?(?:方案|选项|路径)?\s*[A-Za-z0-9一二三四五六七八九十]*\s*[:：]\s*(.+)$", ln)
        if m:
            name = m.group(1).strip()[:30]
            if name:
                hints.append(name)
    if len(hints) >= 1:
        return list(dict.fromkeys(hints))[:5]
    if re.search(r"读博", text):
        hints.append("读博")
    if re.search(r"考公", text):
        hints.append("考公")
    if re.search(r"创业", text):
        hints.append("创业")
    if re.search(r"(留在|当前公司|现公司)", text):
        hints.append("留在当前工作")
    if re.search(r"(offer|跳槽|新公司)", text, flags=re.I):
        hints.append("接受新机会")
    return list(dict.fromkeys(hints))[:5] or ["当前路径", "备选路径"]


def _fallback_option_insights(option_hints: List[str]) -> List[OfferOptionInsight]:
    insights: List[OfferOptionInsight] = []
    for name in option_hints[:5]:
        insights.append(
            OfferOptionInsight(
                option_name=name,
                stability=f"{name} 的稳定性重点看收入波动、城市/家庭匹配度和日常节奏是否可持续。",
                growth=f"{name} 的成长性关键不在标签，而在能否拿到可复用的核心项目与明确反馈。",
                risk=f"{name} 的主要风险是你以为会得到的机会，和实际工作内容不一致。",
                long_term_space=f"{name} 的长期空间要看 2-3 年后是否能形成更强履历，而不是短期抬头。",
                tech_value=f"{name} 的技术价值要区分“真正能力提升”还是“工具调用型执行”。",
                team_industry_factor=f"{name} 受团队带教质量、老板风格和行业景气周期影响很大。",
            )
        )
    return insights


def _fallback_fit_by_choice(option_hints: List[str]) -> List[str]:
    if not option_hints:
        return ["偏成长型：能接受短期波动，愿意为长期能力投入额外精力。"]
    out: List[str] = []
    for name in option_hints[:5]:
        out.append(f"{name}：更适合能接受该路径主要代价、并且与你当前阶段优先级一致的人。")
    return out


def _fallback_regret_points(option_hints: List[str]) -> List[str]:
    names = option_hints[:2] if option_hints else ["当前路径", "备选路径"]
    first = names[0]
    second = names[1] if len(names) > 1 else "其他路径"
    return [
        f"若选择 {first} 却没提前确认真实工作内容，3个月后可能发现投入和预期不一致，时间成本已经发生。",
        f"若放弃 {second} 但没有设立补救计划，3个月后遇到同类焦虑时会反复自我怀疑。",
        "若只比较短期薪资或标签，忽略节奏与家庭承受度，3个月后容易出现持续疲惫和决策后悔。",
    ]


def _fallback_recommendation(core_conflict: List[str], option_hints: List[str]) -> str:
    focus = core_conflict[0] if core_conflict else "你当前最核心的取舍"
    options = " / ".join(option_hints[:3]) if option_hints else "当前路径 / 备选路径"
    return (
        f"先把“{focus}”写成一条决策标准。接下来 48 小时内做三件事："
        f"1）给 {options} 做同维度对比（稳定、成长、风险、长期空间）；"
        "2）各找 1 位在岗或前员工核实真实节奏与产出；"
        "3）把不可接受底线写清（如通勤时长、加班频率、现金流安全线）。"
        "证据补齐后再决定，会比现在直接拍板更稳。"
    )
