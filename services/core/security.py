import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

import bcrypt

from services.core.config import settings
from services.core.exceptions import AuthError


ALGORITHM = "HS256"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if settings.JWT_ALGORITHM != ALGORITHM:
        raise AuthError(f"Unsupported JWT algorithm: {settings.JWT_ALGORITHM}")

    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    expire_at = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": int(expire_at.timestamp())}

    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_segment = _b64url_encode(signature)

    return f"{header_segment}.{payload_segment}.{signature_segment}"


def decode_access_token(token: str) -> dict:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise AuthError("Invalid token format") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    try:
        token_signature = _b64url_decode(signature_segment)
    except Exception as exc:
        raise AuthError("Invalid token signature encoding") from exc

    if not hmac.compare_digest(expected_signature, token_signature):
        raise AuthError("Invalid token signature")

    try:
        header = json.loads(_b64url_decode(header_segment).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    except Exception as exc:
        raise AuthError("Invalid token payload") from exc

    if header.get("alg") != settings.JWT_ALGORITHM:
        raise AuthError("Token algorithm mismatch")

    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise AuthError("Invalid token expiration")

    if datetime.now(UTC).timestamp() > exp:
        raise AuthError("Token has expired")

    return payload
