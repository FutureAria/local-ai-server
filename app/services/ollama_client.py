from typing import Any

import httpx

from app.config import Settings, get_settings


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, settings: Settings | None = None, timeout: float = 60.0):
        self.settings = settings or get_settings()
        self.timeout = timeout

    async def chat(
        self,
        question: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        context: str | None = None,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": question})

        payload: dict[str, Any] = {
            "model": self.settings.ollama_llm_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.settings.ollama_base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.ConnectError as exc:
            raise OllamaError(
                f"Ollama에 연결할 수 없습니다. ollama serve 실행 여부와 URL을 확인하세요: {self.settings.ollama_base_url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaError(f"Ollama API 오류: HTTP {exc.response.status_code} {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise OllamaError(f"Ollama 요청 실패: {exc}") from exc

        data = response.json()
        content = data.get("message", {}).get("content")
        if not content:
            raise OllamaError("Ollama 응답에 message.content가 없습니다.")
        return content

    async def embed(self, text: str) -> list[float]:
        embeddings = await self.embed_texts([text])
        return embeddings[0]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        payload: dict[str, Any] = {"model": self.settings.ollama_embed_model}
        if len(texts) == 1:
            payload["input"] = texts[0]
        else:
            payload["input"] = texts
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.settings.ollama_base_url}/api/embed", json=payload)
                response.raise_for_status()
        except httpx.ConnectError as exc:
            raise OllamaError(
                f"Ollama embedding API에 연결할 수 없습니다. ollama serve 실행 여부를 확인하세요: {self.settings.ollama_base_url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaError(f"Ollama embedding API 오류: HTTP {exc.response.status_code} {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise OllamaError(f"Ollama embedding 요청 실패: {exc}") from exc

        data = response.json()
        if "embeddings" in data and data["embeddings"]:
            embeddings = [list(embedding) for embedding in data["embeddings"]]
            if len(embeddings) != len(texts):
                raise OllamaError(
                    f"Ollama embedding 응답 개수가 요청 개수와 다릅니다: 요청 {len(texts)}개, 응답 {len(embeddings)}개"
                )
            return embeddings
        if "embedding" in data:
            if len(texts) != 1:
                raise OllamaError("Ollama embedding 응답이 단일 embedding만 반환했습니다.")
            return [list(data["embedding"])]
        raise OllamaError("Ollama embedding 응답에 embedding 값이 없습니다.")

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.settings.ollama_base_url}/api/tags")
                response.raise_for_status()
        except httpx.ConnectError as exc:
            raise OllamaError(
                f"Ollama에 연결할 수 없습니다. ollama serve 실행 여부와 URL을 확인하세요: {self.settings.ollama_base_url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaError(f"Ollama model list API 오류: HTTP {exc.response.status_code} {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise OllamaError(f"Ollama model list 요청 실패: {exc}") from exc

        data = response.json()
        return [model.get("name", "") for model in data.get("models", []) if model.get("name")]
