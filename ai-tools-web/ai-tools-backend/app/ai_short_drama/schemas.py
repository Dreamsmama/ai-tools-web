from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AiShortDramaRequest(BaseModel):
    input_mode: Literal["ai", "script"] = Field(
        "script", description="ai=参数生成文案；script=粘贴完整文案直出"
    )
    script: Optional[str] = Field(None, description="完整职业观察局文案（script 模式）")
    career: Optional[str] = Field(None, description="职业角色；script 模式可选，作识别提示")
    theme: Optional[str] = Field(None, description="主题（ai 模式必填）")
    emotion_style: Optional[str] = Field(None, description="情绪风格（ai 模式必填）")
    generate_dynamic_materials: bool = Field(
        True, description="分镜匹配时若无合适动态素材则 AI 生成并缓存"
    )


class MaterialMatch(BaseModel):
    id: str
    name: str = ""
    url: str = ""
    tags: List[str] = Field(default_factory=list)
    aiGenerated: bool = False
    cacheHit: bool = False
    source: Literal[
        "catalog", "cache", "generated", "default", "placeholder", "missing", "character_ip"
    ] = "catalog"
    materialStatus: Literal["ready", "placeholder", "generating", "missing"] = "ready"
    materialError: Optional[str] = None
    materialType: str = ""
    contentType: str = ""
    plannedSlotType: str = ""
    imageWidth: Optional[int] = None
    imageHeight: Optional[int] = None
    aspectRatio: Optional[str] = None
    isVertical: Optional[bool] = None
    exifOrientation: Optional[int] = None


class TextImageSegment(BaseModel):
    """图文成片段落（职业观察局风格）。"""

    segmentNo: int
    duration: int
    text: str
    role: str
    emotion: str
    scene: str
    sceneIntent: str = Field(
        "",
        description="镜头语义：opening/communication/work_pressure/fatigue/collapse/emotion/daily_life",
    )
    sceneDescription: str = Field(
        "",
        description="视觉导演撰写的本段画面描述（中国互联网职场宇宙竖屏场景）",
    )
    sceneDescriptionSource: str = Field(
        "",
        description="场景描述来源：llm=AI写的；fallback=兜底模板（LLM未给描述时使用）",
    )
    imageTags: List[str] = Field(default_factory=list)
    props: List[str] = Field(default_factory=list)
    material: Optional[MaterialMatch] = None
    contentType: str = ""


class ShortDramaShot(BaseModel):
    """兼容旧分镜字段，内部仍可用于视频合成。"""

    shotNo: int
    duration: int
    scene: str
    role: str
    emotion: str
    subtitle: str
    imageTags: List[str] = Field(default_factory=list)
    props: List[str] = Field(default_factory=list)
    material: Optional[MaterialMatch] = None


class AiShortDramaData(BaseModel):
    title: str
    source: Literal["ai", "mock"] = "mock"
    emotionStyle: Optional[str] = Field(None, description="整体情绪风格，用于 BGM 匹配")
    estimatedDurationSeconds: Optional[int] = Field(
        None, description="根据自动节奏引擎计算的预计成片时长（秒）"
    )
    detectedCareer: Optional[str] = Field(None, description="识别或指定的中文职业名")
    detectedRole: Optional[str] = Field(None, description="职业英文 role key")
    characterIp: Optional[CharacterIpStatus] = Field(None, description="该职业基础角色 IP 状态")
    segments: List[TextImageSegment] = Field(default_factory=list)
    shots: List[ShortDramaShot] = Field(default_factory=list)


class AiShortDramaEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[AiShortDramaData] = None
    success: Optional[bool] = None
    stage: Optional[str] = None


class RenderVideoShotInput(BaseModel):
    shotNo: int
    duration: int
    subtitle: str
    imageUrl: Optional[str] = None


class RenderVideoSegmentInput(BaseModel):
    segmentNo: int
    duration: int
    text: str
    imageUrl: Optional[str] = None
    emotion: Optional[str] = None


class RenderVideoRequest(BaseModel):
    title: str = ""
    shots: List[RenderVideoShotInput] = Field(default_factory=list)
    segments: List[RenderVideoSegmentInput] = Field(default_factory=list)
    bgm_mode: Literal["auto", "manual", "none"] = Field(
        "auto", description="BGM：自动匹配 / 手动 / 无"
    )
    bgm_file: Optional[str] = Field(None, description="手动模式下的 BGM 文件名")
    emotion_style: Optional[str] = Field(None, description="整体情绪风格，自动 BGM 优先使用")
    voice_id: Optional[str] = Field(None, description="配音音色ID（如 longxiaochun_v2），None 表示不配音")


class RenderVideoData(BaseModel):
    videoUrl: str
    bgmFile: Optional[str] = None
    bgmMode: Optional[str] = None
    voiceApplied: bool = False


class RenderVideoEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[RenderVideoData] = None


class MaterialRecord(BaseModel):
    id: str
    name: str
    type: str
    role: str
    emotion: str
    scene: str
    url: str
    tags: List[str] = Field(default_factory=list)
    aiGenerated: bool = False
    style: str = ""
    createdAt: str = ""
    updatedAt: str = ""
    imageWidth: Optional[int] = None
    imageHeight: Optional[int] = None
    aspectRatio: Optional[str] = None
    isVertical: Optional[bool] = None
    exifOrientation: Optional[int] = None


class MaterialCreateRequest(BaseModel):
    id: Optional[str] = None
    name: str = ""
    type: str = "scene"
    role: str = "none"
    emotion: str = "none"
    scene: str = "none"
    url: str
    tags: List[str] = Field(default_factory=list)


class MaterialUploadData(BaseModel):
    id: str
    url: str
    filename: str


class MaterialListData(BaseModel):
    items: List[MaterialRecord] = Field(default_factory=list)


class MaterialEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[MaterialRecord] = None


class MaterialListEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[MaterialListData] = None


class MaterialUploadEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[MaterialUploadData] = None


class MaterialAiTagData(BaseModel):
    material: MaterialRecord
    tagSource: Literal["ai", "fallback"] = "fallback"
    description: Optional[str] = None


class MaterialAiTagEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[MaterialAiTagData] = None


class MaterialDeleteEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None


class CharacterIpRecord(BaseModel):
    id: str
    role: str
    name: str = ""
    baseImageUrl: str = ""
    source: Literal["uploaded", "ai_generated"] = "uploaded"
    status: Literal["pending", "approved", "rejected"] = "pending"
    isActive: bool = False
    createdAt: str = ""


class ProfessionRecord(BaseModel):
    id: str
    roleKey: str
    name: str
    description: str = ""
    styleHint: str = ""
    builtIn: bool = False
    createdAt: str = ""


class ProfessionCreateBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=24)
    description: str = Field("", max_length=500)
    styleHint: str = Field("", max_length=500)


class ProfessionUpdateBody(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=24)
    description: Optional[str] = Field(None, max_length=500)
    styleHint: Optional[str] = Field(None, max_length=500)


class ProfessionListEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[List[ProfessionRecord]] = None


class ProfessionEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[ProfessionRecord] = None


class CharacterIpRoleSlot(BaseModel):
    professionId: Optional[str] = None
    role: str
    roleLabel: str = ""
    description: str = ""
    styleHint: str = ""
    builtIn: bool = False
    configured: bool = False
    active: Optional[CharacterIpRecord] = None
    pending: List[CharacterIpRecord] = Field(default_factory=list)


class CharacterIpWorkbenchData(BaseModel):
    roles: List[CharacterIpRoleSlot] = Field(default_factory=list)


class CharacterIpWorkbenchEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[CharacterIpWorkbenchData] = None


class CharacterIpStatus(BaseModel):
    role: str = ""
    roleLabel: str = ""
    configured: bool = False
    baseImageUrl: Optional[str] = None
    name: Optional[str] = None


class CharacterIpStatusEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[CharacterIpStatus] = None


class CharacterIpListEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[List[CharacterIpRecord]] = None


class CharacterIpUploadEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[CharacterIpRecord] = None


class CharacterIpGenerateEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[List[CharacterIpRecord]] = None


class CharacterIpActivateEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
    data: Optional[CharacterIpRecord] = None


class CharacterIpDeleteEnvelope(BaseModel):
    code: int = 0
    message: Optional[str] = None
