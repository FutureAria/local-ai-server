from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    system_prompt: str | None = None
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class SourceReference(BaseModel):
    document_id: int
    filename: str
    chunk_index: int
    chunk_id: int


class AskResponse(BaseModel):
    answer: str
    model: str
    used_documents: bool
    request_id: str


class AskWithDocsRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class AskWithDocsResponse(AskResponse):
    sources: list[SourceReference]
