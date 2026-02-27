from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from services.api.users.model import User
from services.api.users.schema import AuthResponse, LoginRequest, SignupRequest, UserResponse
from services.api.users.services import login_user, signup_user
from services.core.database import get_db
from services.core.exceptions import AuthError, UserExistsError, UserNotFoundError
from services.dependencies.auth import get_current_user

from app import ColoredLogger
logger = ColoredLogger("User >> API")


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    logger.debug(payload)
    try:
        return signup_user(db, payload)
    except UserExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    logger.debug(payload)
    try:
        return login_user(db, payload)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(email=current_user.email, full_name=current_user.full_name)
