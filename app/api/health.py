from fastapi import APIRouter

from app.config import get_settings
from app.services.ollama_client import OllamaClient, OllamaError

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "ollama_base_url": settings.ollama_base_url,
        "llm_model": settings.ollama_llm_model,
        "embedding_model": settings.ollama_embed_model,
    }


@router.get("/health/ollama")
async def ollama_health() -> dict:
    settings = get_settings()
    client = OllamaClient(settings)
    try:
        models = await client.list_models()
    except OllamaError as exc:
        return {
            "ollama_running": False,
            "ollama_base_url": settings.ollama_base_url,
            "models": [],
            "llm_model": settings.ollama_llm_model,
            "embedding_model": settings.ollama_embed_model,
            "llm_model_ready": False,
            "embedding_model_ready": False,
            "error": str(exc),
        }

    return {
        "ollama_running": True,
        "ollama_base_url": settings.ollama_base_url,
        "models": models,
        "llm_model": settings.ollama_llm_model,
        "embedding_model": settings.ollama_embed_model,
        "llm_model_ready": _model_ready(settings.ollama_llm_model, models),
        "embedding_model_ready": _model_ready(settings.ollama_embed_model, models),
        "error": None,
    }


def _model_ready(model_name: str, models: list[str]) -> bool:
    return model_name in models or f"{model_name}:latest" in models
