from sqlalchemy.orm import Session

from services.api.users.crud import create_user, get_user_by_email
from services.api.users.model import User, build_user
from services.api.users.schema import AuthResponse, LoginRequest, SignupRequest, UserResponse
from services.core.exceptions import AuthError, UserExistsError, UserNotFoundError
from services.core.security import create_access_token, hash_password, verify_password


def signup_user(db: Session, payload: SignupRequest) -> AuthResponse:
    existing_user = get_user_by_email(db, payload.email)
    if existing_user:
        raise UserExistsError("User already exists")

    hashed_password = hash_password(payload.password)
    user = create_user(db, build_user(payload.email, payload.full_name, hashed_password))
    token = create_access_token(subject=user.email)

    return AuthResponse(
        access_token=token,
        user=UserResponse(email=user.email, full_name=user.full_name),
    )


def login_user(db: Session, payload: LoginRequest) -> AuthResponse:
    user = get_user_by_email(db, payload.email)
    if not user:
        raise UserNotFoundError("User not found")

    if not verify_password(payload.password, user.hashed_password):
        raise AuthError("Invalid email or password")

    token = create_access_token(subject=user.email)
    return AuthResponse(
        access_token=token,
        user=UserResponse(email=user.email, full_name=user.full_name),
    )
