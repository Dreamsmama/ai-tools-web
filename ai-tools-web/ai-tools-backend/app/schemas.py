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
