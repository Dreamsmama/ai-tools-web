from __future__ import annotations

import hashlib
import math
from typing import List

import httpx

from app.config import settings


class EmbeddingService:
    async def embed(self, texts: List[str]) -> List[List[float]]:
        provider = settings.rag_embedding_provider.strip().lower()
        if provider == "dashscope":
            try:
                return await self._embed_dashscope(texts)
            except Exception:
                # Degrade to local hash embedding when external service is unreachable.
                return self._embed_hash(texts)
        return self._embed_hash(texts)

    def _embed_hash(self, texts: List[str]) -> List[List[float]]:
        dim = settings.rag_embedding_dim
        vectors: List[List[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            values = []
            for i in range(dim):
                b = digest[i % len(digest)]
                values.append((b / 255.0) - 0.5)
            norm = math.sqrt(sum(v * v for v in values)) or 1.0
            vectors.append([v / norm for v in values])
        return vectors

    async def _embed_dashscope(self, texts: List[str]) -> List[List[float]]:
        api_key = settings.dashscope_api_key.strip()
        if not api_key:
            raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        timeout = httpx.Timeout(settings.dashscope_timeout_seconds)
        vectors: List[List[float]] = []
        async with httpx.AsyncClient(timeout=timeout) as client:
            for text in texts:
                payload = {"model": settings.dashscope_embedding_model, "input": {"texts": [text]}}
                resp = await client.post(settings.dashscope_embedding_url, json=payload, headers=headers)
                resp.raise_for_status()
                body = resp.json()
                emb = (
                    body.get("output", {})
                    .get("embeddings", [{}])[0]
                    .get("embedding", [])
                )
                if not emb:
                    raise RuntimeError("embedding 返回为空")
                vectors.append([float(v) for v in emb])
        return vectors


embedding_service = EmbeddingService()
