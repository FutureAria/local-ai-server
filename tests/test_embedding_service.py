import asyncio

import pytest

from app.config import Settings
from app.services.embedding_service import EmbeddingService
from app.services.ollama_client import OllamaError


class FakeOllamaClient:
    def __init__(self):
        self.calls: list[list[str]] = []

    async def embed(self, text: str) -> list[float]:
        return [float(len(text))]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[float(len(text))] for text in texts]


def test_embedding_service_batches_texts() -> None:
    ollama_client = FakeOllamaClient()
    settings = Settings(EMBEDDING_BATCH_SIZE=2)
    service = EmbeddingService(ollama_client=ollama_client, settings=settings)

    embeddings = asyncio.run(service.embed_texts(["a", "bb", "ccc", "dddd", "eeeee"]))

    assert embeddings == [[1.0], [2.0], [3.0], [4.0], [5.0]]
    assert ollama_client.calls == [["a", "bb"], ["ccc", "dddd"], ["eeeee"]]


class FlakyOllamaClient:
    def __init__(self):
        self.calls = 0

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        if self.calls == 1:
            raise OllamaError("temporary embedding failure")
        return [[1.0] for _ in texts]


class FailingOllamaClient:
    def __init__(self):
        self.calls = 0

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        raise OllamaError("persistent embedding failure")


def test_embedding_service_retries_transient_batch_failure() -> None:
    ollama_client = FlakyOllamaClient()
    settings = Settings(EMBEDDING_BATCH_SIZE=2, EMBEDDING_MAX_RETRIES=1)
    service = EmbeddingService(ollama_client=ollama_client, settings=settings)

    embeddings = asyncio.run(service.embed_texts(["a", "b"]))

    assert embeddings == [[1.0], [1.0]]
    assert ollama_client.calls == 2


def test_embedding_service_raises_after_retry_exhaustion() -> None:
    ollama_client = FailingOllamaClient()
    settings = Settings(EMBEDDING_BATCH_SIZE=2, EMBEDDING_MAX_RETRIES=1)
    service = EmbeddingService(ollama_client=ollama_client, settings=settings)

    with pytest.raises(OllamaError, match="Embedding batch 처리에 실패했습니다"):
        asyncio.run(service.embed_texts(["a", "b"]))

    assert ollama_client.calls == 2
