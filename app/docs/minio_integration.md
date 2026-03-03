# MinIO Integration

This service now has centralized MinIO handling in `core` + `dependencies`.

## Core/Dependency files

- `services/core/minio.py`
  - `MinioService.from_settings()`
  - `ensure_user_bucket(user_id)`
  - `put_text_object(bucket, object_key, content)`
  - `build_public_url(bucket, object_key)`
- `services/dependencies/minio.py`
  - `get_minio_service()` FastAPI dependency provider

## Environment variables

Configured in `services/core/config.py`:

- `MINIO_ENDPOINT` (default: `localhost:9000`)
- `MINIO_ACCESS_KEY` (default: `minioadmin`)
- `MINIO_SECRET_KEY` (default: `minioadmin`)
- `MINIO_SECURE` (default: `false`)
- `MINIO_PUBLIC_BASE_URL` (default: `http://localhost:9000`)
- `MINIO_BUCKET_PREFIX` (default: `user-`)

## Bucket and key structure

### Bucket per user

Each user has a dedicated bucket:

- `user-{user_id}` (prefix configurable with `MINIO_BUCKET_PREFIX`)

### Session output object key

`{project_id}/{phase_id}/{step_id}/{thread_id}/output/v{version}.txt`

### Document object key

`{project_id}/{phase_id}/{step_id}/{session_id}/{filename}/v{version}`

## Route behavior

### Sessions

- Create/update session no longer accepts MinIO bucket/key/url inputs from client.
- `thread_id` is generated server-side.
- If `output_data` is provided, backend writes text to MinIO automatically.
- Backend stores generated `minio_bucket`, `minio_object_key`, and `minio_url`.

### Documents

- Create/update document is content-based (no file upload API).
- Backend writes `content` to MinIO on each create/update.
- Each update creates a new version.
- Responses include filename, version, content, and download URL.

## Dependency

`minio` Python SDK added to requirements:

- `minio==7.2.8`
