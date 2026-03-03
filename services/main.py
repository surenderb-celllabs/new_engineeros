import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.projects.routes import router as projects_router
from services.api.sessions.routes import router as sessions_router
from services.api.users.routes import router as users_router
from services.core.config import settings
from services.core.database import init_db
from services.websockets.routes import router as websockets_router


app = FastAPI(title=settings.APP_NAME)


cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000, http://localhost:4200/"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(projects_router, prefix=settings.API_PREFIX)
app.include_router(sessions_router, prefix=settings.API_PREFIX)
app.include_router(websockets_router, prefix=settings.API_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.main:app", host="0.0.0.0", port=8000, reload=True)
