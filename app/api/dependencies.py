from threading import RLock

from fastapi import Header, HTTPException, Request, status

from app.config import get_settings
from app.services.agent_service import AgentService
from app.services.document_service import DocumentService
from app.services.feedback_service import FeedbackService
from app.services.rate_limiter import InMemoryRateLimiter, rate_limit_identity
from app.services.rag_service import RagService
from app.services.search_service import SearchService
from app.services.vector_store import VectorStore


_service_lock = RLock()
_rate_limiter = InMemoryRateLimiter()
_vector_store: VectorStore | None = None
_document_service: DocumentService | None = None
_search_service: SearchService | None = None
_rag_service: RagService | None = None
_feedback_service: FeedbackService | None = None
_agent_service: AgentService | None = None


def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    settings = get_settings()
    presented_key = x_api_key or _bearer_token(authorization)
    if settings.local_api_key and presented_key != settings.local_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LOCAL_API_KEY가 설정되어 있어 X-API-Key 또는 Authorization: Bearer 헤더가 필요합니다.",
        )
    identity = rate_limit_identity(
        presented_key if settings.local_api_key else None,
        request.client.host if request.client else None,
    )
    retry_after = _rate_limiter.check(identity, settings.local_rate_limit_per_minute)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="요청이 너무 많습니다. 잠시 후 다시 시도하세요.",
            headers={"Retry-After": str(retry_after)},
        )


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def reset_rate_limiter() -> None:
    _rate_limiter.reset()


def get_vector_store() -> VectorStore:
    global _vector_store
    with _service_lock:
        if _vector_store is None:
            _vector_store = VectorStore(get_settings())
        return _vector_store


def get_document_service() -> DocumentService:
    global _document_service
    with _service_lock:
        if _document_service is None:
            _document_service = DocumentService(vector_store=get_vector_store())
        return _document_service


def get_search_service() -> SearchService:
    global _search_service
    with _service_lock:
        if _search_service is None:
            _search_service = SearchService(vector_store=get_vector_store())
        return _search_service


def get_rag_service() -> RagService:
    global _rag_service
    with _service_lock:
        if _rag_service is None:
            _rag_service = RagService(search_service=get_search_service())
        return _rag_service


def get_feedback_service() -> FeedbackService:
    global _feedback_service
    with _service_lock:
        if _feedback_service is None:
            _feedback_service = FeedbackService()
        return _feedback_service


def get_agent_service() -> AgentService:
    global _agent_service
    with _service_lock:
        if _agent_service is None:
            _agent_service = AgentService()
        return _agent_service
