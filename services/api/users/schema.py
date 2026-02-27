from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    def __str__(self):
        return (
            f"Login User\n"
            f"------------\n"
            f"Email: {self.email}\n"
            f"Password {self.password}"
        )


class UserResponse(BaseModel):
    email: EmailStr
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    user: UserResponse
