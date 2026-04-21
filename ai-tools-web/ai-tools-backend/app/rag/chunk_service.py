from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.config import settings


@dataclass
class Chunk:
    index: int
    content: str
    metadata: dict


class ChunkService:
    def __init__(self, chunk_size: int, overlap: int) -> None:
        self.chunk_size = max(100, chunk_size)
        self.overlap = max(0, min(overlap, self.chunk_size // 2))

    def split(self, text: str) -> List[Chunk]:
        if not text:
            return []
        chunks: List[Chunk] = []
        start = 0
        idx = 0
        n = len(text)
        while start < n:
            end = min(start + self.chunk_size, n)
            content = text[start:end].strip()
            if content:
                chunks.append(
                    Chunk(
                        index=idx,
                        content=content,
                        metadata={"start": start, "end": end, "char_count": len(content)},
                    )
                )
                idx += 1
            if end >= n:
                break
            start = end - self.overlap
        return chunks


chunk_service = ChunkService(
    chunk_size=settings.rag_chunk_size,
    overlap=settings.rag_chunk_overlap,
)
