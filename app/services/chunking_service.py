from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    content: str
    chunk_index: int
    token_estimate: int
    metadata: dict


class ChunkingService:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size는 1 이상이어야 합니다.")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap은 0 이상이어야 합니다.")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap은 chunk_size보다 작아야 합니다.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, metadata: dict | None = None) -> list[TextChunk]:
        source_metadata = metadata or {}
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            return []

        chunks: list[TextChunk] = []
        start = 0
        index = 0
        step = self.chunk_size - self.chunk_overlap
        while start < len(normalized):
            raw_chunk = normalized[start : start + self.chunk_size].strip()
            if raw_chunk:
                chunks.append(
                    TextChunk(
                        content=raw_chunk,
                        chunk_index=index,
                        token_estimate=max(1, len(raw_chunk) // 4),
                        metadata={**source_metadata, "chunk_index": index},
                    )
                )
                index += 1
            start += step
        return chunks
