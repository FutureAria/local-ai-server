from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class SearchService:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        embedding = await self.embedding_service.embed_text(query)
        return self.vector_store.search(embedding, top_k=top_k)
