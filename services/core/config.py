import os


class Settings:
    """Application settings loaded from environment variables."""

    APP_NAME: str = os.getenv("APP_NAME", "Auth API")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./services.db")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
