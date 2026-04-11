from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    dashscope_api_key: str = ""
    dashscope_url: str = (
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    )
    dashscope_model: str = "qwen-turbo"
    dashscope_timeout_seconds: float = 30.0
    dashscope_temperature: float = 0.2
    dashscope_max_tokens: int = 512
    # prepareConsult 云函数：max_tokens=256，超时在云函数侧 2.5s；自建服务可放宽
    dashscope_prepare_max_tokens: int = 256
    dashscope_prepare_timeout_seconds: float = 30.0


settings = Settings()
