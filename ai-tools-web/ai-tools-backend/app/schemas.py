"""Request/response models aligned with miniprogram cloud function `summarize`."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SummaryTodo(BaseModel):
    owner: str = "未明确"
    task: str = ""
    due: str = ""


class SummaryData(BaseModel):
    summary: List[str] = Field(default_factory=list)
    todos: List[SummaryTodo] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
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
