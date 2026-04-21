from __future__ import annotations

import hashlib
from pathlib import Path

from app.config import settings


class StorageProvider:
    """File storage abstraction for raw documents."""

    def save(self, file_bytes: bytes, filename: str) -> tuple[str, str]:
        raise NotImplementedError

    def load(self, storage_path: str) -> bytes:
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str) -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, file_bytes: bytes, filename: str) -> tuple[str, str]:
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        sanitized = filename.replace("/", "_").replace("\\", "_")
        storage_name = f"{file_hash[:12]}_{sanitized}"
        path = self.base_path / storage_name
        path.write_bytes(file_bytes)
        return str(path), file_hash

    def load(self, storage_path: str) -> bytes:
        return Path(storage_path).read_bytes()


class S3CompatibleStorageProvider(StorageProvider):
    """Placeholder for future MinIO/S3 integration."""

    def save(self, file_bytes: bytes, filename: str) -> tuple[str, str]:
        raise NotImplementedError("S3/MinIO provider is not implemented yet")

    def load(self, storage_path: str) -> bytes:
        raise NotImplementedError("S3/MinIO provider is not implemented yet")


def build_storage_provider() -> StorageProvider:
    backend = settings.rag_file_storage_backend.strip().lower()
    if backend == "local":
        return LocalStorageProvider(settings.rag_storage_dir)
    if backend in {"s3", "minio"}:
        return S3CompatibleStorageProvider()
    raise ValueError(f"unsupported rag_file_storage_backend: {backend}")


storage_provider = build_storage_provider()
