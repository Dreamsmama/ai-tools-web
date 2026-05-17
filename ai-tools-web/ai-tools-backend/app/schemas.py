"""Request/response models aligned with miniprogram cloud function `summarize`."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SummaryData(BaseModel):
    intent: List[str] = Field(default_factory=list)
    emotion: List[str] = Field(default_factory=list)
    strategy: List[str] = Field(default_factory=list)
    reply: str = ""


class SummaryRequest(BaseModel):
    """Matches wx.cloud.callFunction({ name: 'summarize', data: { inputText } })."""

    inputText: str = Field(..., description="聊天原文，对应小程序 textarea")


class SummaryEnvelope(BaseModel):
    """
    Matches cloud function return: { code: 0, data } or { code, message }.
    HTTP layer always 200 so clients can read `code` like mini program `res.result`.
    """

    code: int
    message: Optional[str] = None
    data: Optional[SummaryData] = None

    model_config = {"extra": "allow"}


class OfferDecisionRequest(BaseModel):
    """Offer / 职业决策输入。"""

    input_text: str = Field(..., description="用户输入的 offer 信息与顾虑")


class OfferOptionInsight(BaseModel):
    option_name: str = ""
    stability: str = ""
    growth: str = ""
    risk: str = ""
    long_term_space: str = ""
    tech_value: str = ""
    team_industry_factor: str = ""


class OfferDecisionData(BaseModel):
    core_conflict: List[str] = Field(default_factory=list)
    option_insights: List[OfferOptionInsight] = Field(default_factory=list)
    blind_spots: List[str] = Field(default_factory=list)
    regret_after_3_months: List[str] = Field(default_factory=list)
    fit_by_choice: List[str] = Field(default_factory=list)
    questions_to_confirm: List[str] = Field(default_factory=list)
    recommendation: str = ""


class OfferDecisionEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[OfferDecisionData] = None

    model_config = {"extra": "allow"}


class PrepareConsultData(BaseModel):
    summary: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class PrepareConsultRequest(BaseModel):
    """Matches wx.cloud.callFunction prepareConsult: symptom, report, target."""

    symptom: str = Field(..., description="症状，必填")
    report: str = Field(default="", description="检查/报告")
    target: str = Field(default="", description="想问医生的问题")


class PrepareConsultEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[PrepareConsultData] = None

    model_config = {"extra": "allow"}


class ModelCompareRequest(BaseModel):
    """模型优化实验请求参数。"""

    input: str = Field(..., description="用户输入内容")


class ModelCompareData(BaseModel):
    original_output: str = ""
    optimized_output: str = ""
    mode: str = "placeholder"


class ModelCompareEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[ModelCompareData] = None

    model_config = {"extra": "allow"}


class XiaohongshuAgentRequest(BaseModel):
    topic: str = Field(..., description="内容主题，必填")
    product: str = Field(default="", description="产品/服务")
    audience: str = Field(default="", description="目标人群")
    style: str = Field(default="种草", description="内容风格")
    count: int = Field(default=3, ge=1, le=10, description="输出数量")


class XiaohongshuAgentData(BaseModel):
    titles: List[str] = Field(default_factory=list)
    content: str = ""
    image_prompts: List[str] = Field(default_factory=list)
    publish_tips: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class XiaohongshuAgentEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[XiaohongshuAgentData] = None

    model_config = {"extra": "allow"}


class StructuredMemory(BaseModel):
    职业: str = ""
    目标: str = ""
    情绪: str = ""
    风险倾向: str = ""
    关键事件: List[str] = Field(default_factory=list)


class MemoryCompareRequest(BaseModel):
    chat_content: str = Field(..., description="聊天记录")
    question: str = Field(..., description="用户问题")


class MemoryCompareData(BaseModel):
    normal_answer: str = ""
    memory_answer: str = ""
    structured_memory: StructuredMemory = Field(default_factory=StructuredMemory)


class MemoryCompareEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[MemoryCompareData] = None

    model_config = {"extra": "allow"}


class EveningPlanRequest(BaseModel):
    """下班后不知道干什么 — 用户表单。"""

    city: str = Field(default="", description="当前城市")
    current_time: str = Field(default="", description="现在时间 HH:mm")
    energy_level: str = Field(default="", description="今天状态")
    mood: str = Field(default="", description="今天心情")
    go_out: str = Field(default="", description="是否想出门")
    social: str = Field(default="", description="是否想社交")
    budget: str = Field(default="", description="预算")
    interests: List[str] = Field(default_factory=list, description="今天更想做什么")
    extra_notes: str = Field(default="", description="额外补充")


class EveningPlanItem(BaseModel):
    plan_type: str = ""
    title: str = ""
    reason: str = ""
    actions: List[str] = Field(default_factory=list)
    cost: str = ""
    duration: str = ""
    fit_score: int = 3


class EveningLazyFallback(BaseModel):
    title: str = ""
    description: str = ""


class EveningPlanData(BaseModel):
    mode: str = ""
    plans: List[EveningPlanItem] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    lazy_fallback: EveningLazyFallback = Field(default_factory=EveningLazyFallback)
    tomorrow_tips: List[str] = Field(default_factory=list)


class EveningPlanEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[EveningPlanData] = None

    model_config = {"extra": "allow"}


class InterestExplorerRequest(BaseModel):
    """AI 兴趣推荐 — 用户表单。"""

    life_stage: str = Field(default="", description="当前阶段")
    work_state: str = Field(default="", description="工作/学习状态")
    social_style: str = Field(default="", description="社交倾向")
    preferences: List[str] = Field(default_factory=list, description="更喜欢")
    budget: str = Field(default="", description="预算")
    weekend_state: str = Field(default="", description="周末一般状态")
    goals: List[str] = Field(default_factory=list, description="最想获得什么")
    extra_notes: str = Field(default="", description="最近的状态/想法")


class InterestExplorerPersonality(BaseModel):
    type_title: str = ""
    analysis: str = ""
    why_past_failed: str = ""


class InterestExplorerItem(BaseModel):
    name: str = ""
    why_fit: str = ""
    difficulty: int = 3
    cost_level: str = "低"
    social_level: str = "低"
    long_term: str = ""
    best_time: str = ""
    starter_tip: str = ""


class InterestExplorerWeekItem(BaseModel):
    day: str = ""
    activity: str = ""


class InterestExplorerLazyFallback(BaseModel):
    title: str = ""
    description: str = ""


class InterestExplorerData(BaseModel):
    personality: InterestExplorerPersonality = Field(default_factory=InterestExplorerPersonality)
    interests: List[InterestExplorerItem] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    week_plan: List[InterestExplorerWeekItem] = Field(default_factory=list)
    lazy_fallback: InterestExplorerLazyFallback = Field(
        default_factory=InterestExplorerLazyFallback
    )


class InterestExplorerEnvelope(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[InterestExplorerData] = None

    model_config = {"extra": "allow"}
