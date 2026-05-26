from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent, ask, assistant, chat_logs, documents, feedback, health, project, search
from app.config import get_settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="local-ai-server", version="0.1.0", lifespan=lifespan)
    settings = get_settings()
    if settings.local_api_key is None and settings.local_api_key_warn:
        print(
            "WARNING: LOCAL_API_KEY is not set. Protected local endpoints are running without API key enforcement.",
            file=sys.stderr,
        )
    cors_origins = [origin.strip() for origin in settings.local_cors_origins.split(",") if origin.strip()]
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=settings.local_cors_allow_credentials,
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-API-Key"],
        )
    app.include_router(health.router)
    app.include_router(ask.router)
    app.include_router(chat_logs.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    app.include_router(feedback.router)
    app.include_router(agent.router)
    app.include_router(project.router)
    app.include_router(assistant.router)
    return app


app = create_app()
