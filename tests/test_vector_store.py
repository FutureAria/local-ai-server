from app.services.vector_store import VectorStore


class FakeCollection:
    def get(self, include=None):
        return {
            "ids": ["1", "2", "bad"],
            "metadatas": [{"chunk_id": 1}, {"chunk_id": "2"}, {"chunk_id": "not-int"}],
        }


def test_vector_store_list_chunk_ids() -> None:
    store = object.__new__(VectorStore)
    store.collection = FakeCollection()
    assert store.list_chunk_ids() == {1, 2}
