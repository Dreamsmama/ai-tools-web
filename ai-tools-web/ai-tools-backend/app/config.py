from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    dashscope_api_key: str = ""
    dashscope_url: str = (
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    )
    dashscope_model: str = "qwen-turbo"
    dashscope_optimized_model: str = ""
    dashscope_timeout_seconds: float = 30.0
    dashscope_temperature: float = 0.2
    dashscope_max_tokens: int = 512
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


settings = Settings()
