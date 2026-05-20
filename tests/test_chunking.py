from app.services.chunking_service import ChunkingService


def test_chunking_handles_normal_text() -> None:
    chunker = ChunkingService(chunk_size=10, chunk_overlap=2)
    chunks = chunker.split_text("abcdefghijklmnopqrstuvwxyz")
    assert len(chunks) >= 3
    assert chunks[0].content == "abcdefghij"
    assert chunks[1].chunk_index == 1


def test_chunking_handles_short_text() -> None:
    chunker = ChunkingService(chunk_size=1200, chunk_overlap=200)
    chunks = chunker.split_text("short text")
    assert len(chunks) == 1
    assert chunks[0].content == "short text"


def test_chunking_does_not_create_empty_chunks() -> None:
    chunker = ChunkingService(chunk_size=10, chunk_overlap=2)
    assert chunker.split_text("   \n  ") == []
