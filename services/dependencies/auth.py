from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from services.api.users.crud import get_user_by_email
from services.core.database import get_db
from services.core.exceptions import AuthError
from services.core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise AuthError("Invalid token subject")
        user = get_user_by_email(db, email)
        if user is None:
            raise AuthError("User no longer exists")
        return user
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
