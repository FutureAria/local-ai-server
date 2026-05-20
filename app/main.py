from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api import agent, ask, assistant, chat_logs, documents, feedback, health, project, search
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="local-ai-server", version="0.1.0", lifespan=lifespan)
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
