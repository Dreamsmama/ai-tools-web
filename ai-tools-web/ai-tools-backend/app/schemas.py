"""Request/response models aligned with miniprogram cloud function `summarize`."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class SummaryTodo(BaseModel):
    owner: str = "未明确"
    task: str = ""
    due: str = ""


class SummaryData(BaseModel):
    summary: list[str] = Field(default_factory=list)
    todos: list[SummaryTodo] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
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
    summary: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


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
