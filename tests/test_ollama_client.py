import asyncio

import httpx

from app.config import Settings
from app.services.ollama_client import OllamaClient


def test_ollama_chat_mock() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        return httpx.Response(200, json={"message": {"content": "mock answer"}})

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    httpx.AsyncClient = patched_client
    try:
        client = OllamaClient(Settings())
        assert asyncio.run(client.chat("question")) == "mock answer"
    finally:
        httpx.AsyncClient = original_client


def test_ollama_list_models_mock() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tags"
        return httpx.Response(200, json={"models": [{"name": "llama3.2:latest"}]})

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    httpx.AsyncClient = patched_client
    try:
        client = OllamaClient(Settings())
        assert asyncio.run(client.list_models()) == ["llama3.2:latest"]
    finally:
        httpx.AsyncClient = original_client


def test_ollama_embed_texts_mock() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/embed"
        payload = request.read()
        assert b'"input":["first","second"]' in payload
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    httpx.AsyncClient = patched_client
    try:
        client = OllamaClient(Settings())
        assert asyncio.run(client.embed_texts(["first", "second"])) == [[0.1, 0.2], [0.3, 0.4]]
    finally:
        httpx.AsyncClient = original_client
