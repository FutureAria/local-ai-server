import scripts.smoke_test_api as smoke


class FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeClient:
    def __init__(self, calls: list[dict]) -> None:
        self.calls = calls

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def get(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": "GET", "url": url, **kwargs})
        if url.endswith("/health"):
            return FakeResponse(200, {"status": "ok"})
        return FakeResponse(200, {"documents_count": 1, "chunks_count": 1})

    def post(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": "POST", "url": url, **kwargs})
        if url.endswith("/documents/upload"):
            return FakeResponse(200, {"document_id": 1, "filename": "smoke.md", "chunks_created": 1})
        if url.endswith("/search"):
            return FakeResponse(200, {"query": "JWT", "results": [{"chunk_id": 1}]})
        if url.endswith("/ask-with-docs"):
            return FakeResponse(200, {"request_id": "7", "sources": [{"chunk_id": 1}]})
        if url.endswith("/feedback"):
            return FakeResponse(200, {"feedback_id": 9})
        return FakeResponse(200, {})


def test_smoke_script_calls_expected_api_flow(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    summary = smoke.run_smoke_test("http://server.test/")

    assert summary["ok"] is True
    assert [step["step"] for step in summary["steps"]] == [
        "health",
        "upload",
        "search",
        "ask-with-docs",
        "feedback",
        "stats",
    ]
    assert calls[1]["headers"] == {"X-API-Key": "secret"}
    assert calls[3]["json"]["question"] == "내 문서 기준으로 access token은 어디로 전달해?"
