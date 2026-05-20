from app.services.search_service import SearchService


class FakeEmbeddingService:
    async def embed_text(self, text: str) -> list[float]:
        assert text == "JWT"
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        assert query_embedding == [0.1, 0.2, 0.3]
        assert top_k == 1
        return [
            {
                "chunk_id": 1,
                "document_id": 2,
                "filename": "auth.md",
                "chunk_index": 0,
                "content": "JWT flow",
                "score": 0.12,
            }
        ]


def test_search_service_uses_embedding_and_vector_store() -> None:
    import asyncio

    service = SearchService(embedding_service=FakeEmbeddingService(), vector_store=FakeVectorStore())
    results = asyncio.run(service.search("JWT", top_k=1))
    assert results[0]["filename"] == "auth.md"
