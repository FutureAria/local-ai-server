from app.services.rag_service import RagService


def test_rag_answer_guard_blocks_code_not_in_context() -> None:
    service = RagService()
    answer = "```java\nclass Demo {}\n```"
    context = "JWT authentication flow"
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_blocks_unsupported_security_details() -> None:
    service = RagService()
    answer = "서버는 refresh token과 패스워드를 확인한다."
    context = "서버는 access token을 발급한다."
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_blocks_speculative_language() -> None:
    service = RagService()
    answer = "Controller의 responsibility일 수 있습니다."
    context = "Controller가 HTTP 요청과 응답을 담당한다."
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_blocks_korean_speculative_language() -> None:
    service = RagService()
    answer = "refresh token 키워드를 통해 토큰이 재발급될 수 있습니다."
    context = "JWT PDF notes access token refresh token local ai server"
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_blocks_unsupported_availability_language() -> None:
    service = RagService()
    answer = "이 단계는 현재 문서에서 자세한 내용은 unavailable이다."
    context = "JWT는 Bearer 헤더로 전달된다."
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_blocks_mixed_english_availability_phrase() -> None:
    service = RagService()
    answer = 'refresh token 관련 정보는 available isn\'t.'
    context = "JWT PDF notes access token refresh token local ai server"
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_blocks_not_available_phrase() -> None:
    service = RagService()
    answer = "refresh token 키워드는 PDF에 있지만 exact keyword는 not available in the indexed documents."
    context = "JWT PDF notes access token refresh token local ai server"
    assert service._violates_context(answer, context) is True


def test_rag_answer_guard_allows_plain_grounded_answer() -> None:
    service = RagService()
    answer = "JWT는 Authorization Bearer 헤더로 전달된다."
    context = "JWT는 Authorization Bearer 헤더로 전달된다."
    assert service._violates_context(answer, context) is False


def test_rag_fallback_answer_uses_sources() -> None:
    service = RagService()
    answer = service._build_fallback_answer(
        [
            {
                "filename": "backend.md",
                "chunk_index": 0,
                "content": "JWT는 Bearer 헤더로 전달된다.",
            }
        ]
    )
    assert "backend.md" in answer
    assert "JWT는 Bearer 헤더로 전달된다." in answer
