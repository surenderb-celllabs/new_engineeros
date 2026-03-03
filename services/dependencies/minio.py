from functools import lru_cache

from services.core.minio import MinioService


@lru_cache
def get_minio_service() -> MinioService:
    return MinioService.from_settings()
