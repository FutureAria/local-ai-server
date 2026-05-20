import asyncio

from app.config import Settings, get_settings
from app.services.ollama_client import OllamaClient, OllamaError


class EmbeddingService:
    def __init__(self, ollama_client: OllamaClient | None = None, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.ollama_client = ollama_client or OllamaClient(self.settings)

    async def embed_text(self, text: str) -> list[float]:
        return await self.ollama_client.embed(text)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self.settings.embedding_batch_size):
            batch = texts[start : start + self.settings.embedding_batch_size]
            embeddings.extend(await self._embed_batch_with_retry(batch))
        return embeddings

    async def _embed_batch_with_retry(self, batch: list[str]) -> list[list[float]]:
        last_error: OllamaError | None = None
        for attempt in range(self.settings.embedding_max_retries + 1):
            try:
                return await self.ollama_client.embed_texts(batch)
            except OllamaError as exc:
                last_error = exc
                if attempt >= self.settings.embedding_max_retries:
                    break
                await asyncio.sleep(0.1 * (attempt + 1))
        raise OllamaError(
            f"Embedding batch 처리에 실패했습니다. batch_size={len(batch)}, "
            f"retries={self.settings.embedding_max_retries}, error={last_error}"
        ) from last_error
