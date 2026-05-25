from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    dashscope_api_key: str = ""
    dashscope_url: str = (
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    )
    dashscope_model: str = "qwen-plus"
    dashscope_optimized_model: str = ""
    dashscope_timeout_seconds: float = 30.0
    dashscope_temperature: float = 0.2
    dashscope_max_tokens: int = 512
    # 短剧文案分析（拆段+元数据）通常比摘要更慢，单独放宽
    short_drama_script_timeout_seconds: float = 90.0
    # 单段 AI 动态配图（即梦）超时
    short_drama_ai_material_timeout_seconds: float = 90.0
    # 并发生成动态配图的段数（加快整次 /generate）
    short_drama_ai_material_parallel: int = 3
    # prepareConsult 云函数：max_tokens=256，超时在云函数侧 2.5s；自建服务可放宽
    dashscope_prepare_max_tokens: int = 256
    dashscope_prepare_timeout_seconds: float = 30.0
    dashscope_embedding_url: str = (
        "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
    )
    dashscope_embedding_model: str = "text-embedding-v3"
    rag_default_user_id: str = "default_user"
    rag_default_workspace_id: str = "default_workspace"
    rag_storage_dir: str = "./data/rag_storage"
    rag_database_url: str = "postgresql://postgres:postgres@127.0.0.1:5432/ai_tools"
    rag_chunk_size: int = 600
    rag_chunk_overlap: int = 120
    rag_top_k: int = 5
    rag_embedding_provider: str = "hash"
    rag_embedding_dim: int = 128
    rag_file_storage_backend: str = "local"
    rag_vector_store_backend: str = "pgvector"
    rag_official_only: bool = False
    rag_official_kb_id: str = "official_kb_default"
    rag_official_kb_name: str = "官方模板库"
    rag_official_kb_description: str = "平台官方只读知识库"
    analytics_database_url: str = ""
    analytics_ip_salt: str = "change-me"
    # 短剧素材库：留空则使用本地 JSON（不与 RAG 共用远程库）
    short_drama_database_url: str = ""
    # 启动时扫描 uploads 下图片做纯色清理（本地开发建议关闭，避免阻塞启动）
    short_drama_startup_cleanup: bool = False

    # 即梦 AI 图片生成（OpenAI 兼容接口，如火山方舟 / 第三方网关）
    jimeng_api_key: str = ""
    jimeng_api_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    jimeng_model: str = "doubao-seedream-4-0-250828"
    jimeng_image_size: str = "1080x1920"
    jimeng_timeout_seconds: float = 120.0
    # 通义万相回退（与 DashScope 共用 API Key）
    dashscope_image_url: str = (
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    )
    dashscope_image_model: str = "wanx2.1-t2i-turbo"

    # AI 换发型（复用 jimeng_api_key / jimeng_api_base_url；需配置支持图片编辑的模型）
    hairstyle_model: str = ""
    hairstyle_timeout_seconds: float = 90.0

    # CosyVoice TTS 配音（复用 dashscope_api_key）
    # 模型：cosyvoice-v2 / cosyvoice-v3-flash 等，见百炼非流式 CosyVoice 文档
    tts_model: str = "cosyvoice-v2"
    tts_voice_default: str = "longxiaochun_v2"
    tts_timeout_seconds: float = 60.0


settings = Settings()
