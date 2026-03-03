"""Dependency providers for FastAPI endpoints."""

from services.dependencies.minio import get_minio_service

__all__ = ["get_minio_service"]
