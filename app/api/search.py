from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_search_service, require_api_key
from app.schemas.search import SearchRequest, SearchResponse
from app.services.ollama_client import OllamaError
from app.services.search_service import SearchService

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse, dependencies=[Depends(require_api_key)])
async def search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    try:
        results = await search_service.search(request.query, top_k=request.top_k)
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return SearchResponse(query=request.query, results=results)
