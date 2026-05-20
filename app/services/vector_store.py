from typing import Any

import chromadb

from app.config import Settings, get_settings


class VectorStore:
    def __init__(self, settings: Settings | None = None, collection_name: str = "local_ai_chunks"):
        self.settings = settings or get_settings()
        self.client = chromadb.PersistentClient(path=self.settings.chroma_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, records: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
        if not records:
            return
        if len(records) != len(embeddings):
            raise ValueError("records와 embeddings 개수가 일치해야 합니다.")

        self.collection.upsert(
            ids=[str(record["chunk_id"]) for record in records],
            embeddings=embeddings,
            documents=[record["content"] for record in records],
            metadatas=[
                {
                    "chunk_id": record["chunk_id"],
                    "document_id": record["document_id"],
                    "filename": record["filename"],
                    "chunk_index": record["chunk_index"],
                }
                for record in records
            ],
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        result = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        results: list[dict[str, Any]] = []
        for index, chunk_id in enumerate(ids):
            metadata = metadatas[index] or {}
            results.append(
                {
                    "chunk_id": int(metadata.get("chunk_id") or chunk_id),
                    "document_id": int(metadata["document_id"]),
                    "filename": str(metadata["filename"]),
                    "chunk_index": int(metadata["chunk_index"]),
                    "content": documents[index],
                    "score": float(distances[index]) if distances else 0.0,
                }
            )
        return results

    def delete_document(self, document_id: int) -> None:
        self.collection.delete(where={"document_id": document_id})

    def count(self) -> int:
        return int(self.collection.count())

    def list_chunk_ids(self) -> set[int]:
        result = self.collection.get(include=["metadatas"])
        chunk_ids: set[int] = set()
        for raw_id, metadata in zip(result.get("ids", []), result.get("metadatas", []), strict=False):
            value = (metadata or {}).get("chunk_id", raw_id)
            try:
                chunk_ids.add(int(value))
            except (TypeError, ValueError):
                continue
        return chunk_ids
