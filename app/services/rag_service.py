import json

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.models import ChatLog
from app.services.ollama_client import OllamaClient
from app.services.search_service import SearchService


RAG_SYSTEM_PROMPT = """You are a careful local AI assistant for document-grounded Q&A.
Use the provided context as the only factual source.
Do not add implementation details, security claims, credentials, IDs, passwords, API behavior, or source references that are not present in the context.
If the context is insufficient, say that the indexed documents do not contain enough information.
Do not invent sources. If the user asks in Korean, answer in Korean.
Keep technical explanations clear, practical, and explicitly tied to the provided context."""


class RagService:
    def __init__(
        self,
        settings: Settings | None = None,
        ollama_client: OllamaClient | None = None,
        search_service: SearchService | None = None,
    ):
        self.settings = settings or get_settings()
        self.ollama_client = ollama_client or OllamaClient(self.settings)
        self.search_service = search_service or SearchService()

    async def ask(self, db: Session, question: str, system_prompt: str | None, temperature: float) -> ChatLog:
        answer = await self.ollama_client.chat(
            question=question,
            system_prompt=system_prompt,
            temperature=temperature,
        )
        chat_log = ChatLog(
            question=question,
            answer=answer,
            mode="direct",
            model=self.settings.ollama_llm_model,
            used_sources_json=None,
        )
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)
        return chat_log

    async def ask_with_docs(self, db: Session, question: str, top_k: int, temperature: float) -> ChatLog:
        results = await self.search_service.search(question, top_k=top_k)
        context = self._build_context(results)
        grounded_question = self._build_grounded_question(question)
        answer = await self.ollama_client.chat(
            question=grounded_question,
            system_prompt=RAG_SYSTEM_PROMPT,
            temperature=temperature,
            context=context,
        )
        if self._violates_context(answer, context):
            answer = self._build_fallback_answer(results)
        sources = [
            {
                "document_id": result["document_id"],
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "chunk_id": result["chunk_id"],
            }
            for result in results
        ]
        chat_log = ChatLog(
            question=question,
            answer=answer,
            mode="rag",
            model=self.settings.ollama_llm_model,
            used_sources_json=json.dumps(sources, ensure_ascii=False),
        )
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)
        return chat_log

    def _build_context(self, results: list[dict]) -> str:
        if not results:
            return "Indexed document context is empty."
        sections = []
        for result in results:
            sections.append(
                f"[source chunk_id={result['chunk_id']} document_id={result['document_id']} "
                f"filename={result['filename']} chunk_index={result['chunk_index']}]\n{result['content']}"
            )
        return "\n\n".join(sections)

    def _build_grounded_question(self, question: str) -> str:
        return (
            f"User question:\n{question}\n\n"
            "Answer constraints:\n"
            "- Use only the provided context.\n"
            "- Do not include code examples unless code exists in the provided context.\n"
            "- Do not add login/password, token validation, refresh, logging, or security details unless they exist in the provided context.\n"
            "- If a detail is not in the context, say it is not available in the indexed documents.\n"
            "- For each main point, keep it traceable to the provided context."
        )

    def _violates_context(self, answer: str, context: str) -> bool:
        answer_lower = answer.lower()
        context_lower = context.lower()
        if "```" in answer and "```" not in context:
            return True
        if ("http://" in answer_lower or "https://" in answer_lower) and "http" not in context_lower:
            return True
        unsupported_markers = [
            "password",
            "패스워드",
            "refresh token",
            "mvc",
            "spring security",
            "oauth",
            "401",
            "unauthorized",
            "token generator",
            "token validator",
            "responsibility",
            "일 수 있",
            "될 수",
            "키워드를 통해",
            "유효한 사용자",
            "unavailable",
            "available isn't",
            "isn't available",
            "not available",
            "exact keyword",
            "자세한 내용",
        ]
        for marker in unsupported_markers:
            if marker in answer_lower and marker not in context_lower:
                return True
        return False

    def _build_fallback_answer(self, results: list[dict]) -> str:
        if not results:
            return "색인된 문서에 충분한 정보가 없습니다."

        lines = ["색인된 문서 기준으로 확인된 내용은 다음과 같습니다:"]
        for result in results:
            content = " ".join(result["content"].split())
            lines.append(
                f"- [{result['filename']} chunk {result['chunk_index']}] {content}"
            )
        lines.append("문서에 없는 코드 예시, 외부 링크, 세부 구현은 추가하지 않았습니다.")
        return "\n".join(lines)
