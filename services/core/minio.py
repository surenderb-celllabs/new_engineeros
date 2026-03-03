from io import BytesIO
from datetime import timedelta
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error
from minio.versioningconfig import ENABLED, VersioningConfig

from services.core.config import settings


class MinioService:
    def __init__(self, client: Minio):
        self.client = client

    @classmethod
    def from_settings(cls) -> "MinioService":
        endpoint = settings.MINIO_ENDPOINT
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            parsed = urlparse(endpoint)
            endpoint = parsed.netloc or parsed.path
        client = Minio(
            endpoint=endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        return cls(client=client)

    def ensure_user_bucket(self, user_id: int) -> str:
        bucket_name = f"{settings.MINIO_BUCKET_PREFIX}{user_id}".lower()
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
            self.client.set_bucket_versioning(bucket_name, VersioningConfig(ENABLED))
        except S3Error as exc:
            raise RuntimeError(f"Failed to ensure MinIO bucket '{bucket_name}': {exc}") from exc
        return bucket_name

    def put_text_object(self, bucket: str, object_key: str, content: str) -> None:
        payload = content.encode("utf-8")
        data = BytesIO(payload)
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_key,
                data=data,
                length=len(payload),
                content_type="text/plain; charset=utf-8",
            )
        except S3Error as exc:
            raise RuntimeError(f"Failed to upload object '{bucket}/{object_key}' to MinIO: {exc}") from exc

    def build_public_url(self, bucket: str, object_key: str) -> str:
        base = settings.MINIO_PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/{bucket}/{object_key}"

    def get_text_object(self, bucket: str, object_key: str) -> str:
        try:
            response = self.client.get_object(bucket_name=bucket, object_name=object_key)
            data = response.read()
            response.close()
            response.release_conn()
            return data.decode("utf-8")
        except S3Error as exc:
            raise RuntimeError(f"Failed to read object '{bucket}/{object_key}' from MinIO: {exc}") from exc

    def put_bytes_object(self, bucket: str, object_key: str, payload: bytes, content_type: str | None = None) -> str | None:
        data = BytesIO(payload)
        try:
            result = self.client.put_object(
                bucket_name=bucket,
                object_name=object_key,
                data=data,
                length=len(payload),
                content_type=content_type or "application/octet-stream",
            )
            return getattr(result, "version_id", None)
        except S3Error as exc:
            raise RuntimeError(f"Failed to upload object '{bucket}/{object_key}' to MinIO: {exc}") from exc

    def list_object_versions(self, bucket: str, object_key: str) -> list[dict]:
        try:
            objects = self.client.list_objects(
                bucket_name=bucket,
                prefix=object_key,
                recursive=True,
                include_version=True,
            )
        except S3Error as exc:
            raise RuntimeError(f"Failed to list versions for '{bucket}/{object_key}': {exc}") from exc

        versions: list[dict] = []
        for obj in objects:
            if obj.object_name != object_key:
                continue
            versions.append(
                {
                    "version_id": getattr(obj, "version_id", None),
                    "is_latest": bool(getattr(obj, "is_latest", False)),
                    "last_modified": getattr(obj, "last_modified", None),
                    "size": getattr(obj, "size", None),
                    "etag": getattr(obj, "etag", None),
                }
            )
        versions.sort(
            key=lambda item: item.get("last_modified") or 0,
            reverse=True,
        )
        return versions

    def list_objects(self, bucket: str, prefix: str, recursive: bool = True) -> list[dict]:
        try:
            objects = self.client.list_objects(bucket_name=bucket, prefix=prefix, recursive=recursive)
        except S3Error as exc:
            raise RuntimeError(f"Failed to list objects for '{bucket}/{prefix}': {exc}") from exc
        items: list[dict] = []
        for obj in objects:
            items.append(
                {
                    "object_name": obj.object_name,
                    "last_modified": getattr(obj, "last_modified", None),
                    "size": getattr(obj, "size", None),
                    "etag": getattr(obj, "etag", None),
                }
            )
        return items

    def get_object_bytes(self, bucket: str, object_key: str, version_id: str | None = None) -> bytes:
        try:
            response = self.client.get_object(bucket_name=bucket, object_name=object_key, version_id=version_id)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as exc:
            raise RuntimeError(f"Failed to read object '{bucket}/{object_key}' from MinIO: {exc}") from exc

    def presigned_download_url(
        self,
        bucket: str,
        object_key: str,
        expires_seconds: int = 3600,
        version_id: str | None = None,
    ) -> str:
        try:
            return self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_key,
                expires=timedelta(seconds=expires_seconds),
                version_id=version_id,
            )
        except S3Error:
            return self.build_public_url(bucket, object_key)
