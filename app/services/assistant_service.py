import json
import re
from pathlib import Path
from uuid import uuid4

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.db.models import AssistantMessage, AssistantSession
from app.schemas.assistant import AssistantMessageRequest, ProjectRootValidateRequest
from app.services.agent_service import AgentService
from app.services.document_service import DocumentService
from app.services.project_status_service import dry_run_shell_command, get_project_status, get_shell_policy
from app.services.rag_service import RagService
from app.services.search_service import SearchService


class AssistantService:
    def __init__(
        self,
        settings: Settings | None = None,
        rag_service: RagService | None = None,
        search_service: SearchService | None = None,
        document_service: DocumentService | None = None,
        agent_service: AgentService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.rag_service = rag_service or RagService()
        self.search_service = search_service or SearchService()
        self.document_service = document_service or DocumentService()
        self.agent_service = agent_service or AgentService(self.settings)

    def capabilities(self) -> dict:
        return {
            "service": self.settings.service_name,
            "modes": ["auto", "ask", "ask_with_docs", "search", "index_preview", "agent_plan", "shell_dry_run"],
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "llm_provider": "ollama-local",
            "vector_store": "chroma-local",
            "storage": "sqlite-local",
            "safe_defaults": {
                "shell_execution": "disabled",
                "shell_dry_run": "enabled",
                "browser_interaction": "blocked",
                "file_write_delete": "blocked",
                "folder_index_from_assistant": "preview-only",
                "agent_execution_enabled": self.settings.agent_execution_enabled,
                "web_fetch_enabled": self.settings.agent_web_fetch_enabled,
            },
            "endpoints": {
                "ping": "GET /assistant/ping",
                "config": "GET /assistant/config",
                "dashboard": "GET /assistant/dashboard",
                "bootstrap": "POST /assistant/bootstrap",
                "status": "GET /assistant/status",
                "message": "POST /assistant/message",
                "create_session": "POST /assistant/sessions",
                "list_sessions": "GET /assistant/sessions",
                "get_session": "GET /assistant/sessions/{session_id}",
                "list_session_messages": "GET /assistant/sessions/{session_id}/messages",
                "validate_project_root": "POST /assistant/project-root/validate",
                "shell_policy": "GET /project/shell-policy",
                "shell_dry_run": "POST /project/shell-dry-run",
            },
        }

    def ping(self) -> dict:
        return {
            "status": "ok",
            "service": self.settings.service_name,
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "ui_ready": True,
        }

    def config(self) -> dict:
        return {
            "service": self.settings.service_name,
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "cors_origins": _csv_values(self.settings.local_cors_origins),
            "allowed_roots": _root_summaries(self.settings.agent_allowed_roots),
            "models": {
                "llm_provider": "ollama-local",
                "llm_model": self.settings.ollama_llm_model,
                "embedding_model": self.settings.ollama_embed_model,
            },
            "storage": {
                "database": "sqlite-local",
                "vector_store": "chroma-local",
                "upload_dir": self.settings.upload_dir,
                "chroma_path": self.settings.chroma_path,
            },
            "safety": _safety(),
            "rate_limit": {
                "enabled": self.settings.local_rate_limit_per_minute > 0,
                "per_minute": self.settings.local_rate_limit_per_minute,
            },
        }

    def status(self, db: Session) -> dict:
        project_status = get_project_status()
        document_stats = self.document_service.get_stats(db)
        integrity = self.document_service.get_integrity_report(db)
        sessions_count = db.scalar(select(func.count(AssistantSession.id))) or 0
        messages_count = db.scalar(select(func.count(AssistantMessage.id))) or 0
        return {
            "service": self.settings.service_name,
            "current_phase": project_status["current_phase"],
            "documents": {
                "documents_count": document_stats["documents_count"],
                "chunks_count": document_stats["chunks_count"],
                "chroma_vectors_count": document_stats["chroma_vectors_count"],
                "missing_stored_files_count": document_stats["missing_stored_files_count"],
            },
            "integrity": {
                "status": integrity["status"],
                "chunks_missing_vectors_count": integrity["chunks_missing_vectors_count"],
                "orphan_vectors_count": integrity["orphan_vectors_count"],
                "repair_available": integrity["repair_available"],
            },
            "sessions": {
                "sessions_count": sessions_count,
                "messages_count": messages_count,
            },
            "safety": _safety(),
        }

    def dashboard(self, db: Session) -> dict:
        status = self.status(db)
        recent_sessions = self.list_sessions(db, limit=5, offset=0)["sessions"]
        return {
            "service": self.settings.service_name,
            "current_phase": status["current_phase"],
            "cards": {
                "documents": status["documents"],
                "integrity": status["integrity"],
                "sessions": status["sessions"],
                "connection": {
                    "status": "ready",
                    "protected": bool(self.settings.local_api_key),
                    "local_only": True,
                },
            },
            "recent_sessions": recent_sessions,
            "safety": status["safety"],
            "ui": {
                "ready": True,
                "badge": "DASHBOARD READY",
                "message": "대시보드 상태를 조회했습니다.",
                "recommended_refresh_seconds": 30,
            },
        }

    def bootstrap(
        self,
        db: Session,
        project_root: str | None = None,
        include_sessions: bool = True,
        sessions_limit: int = 10,
    ) -> dict:
        root_status = None
        if project_root:
            root_status = self.validate_project_root(ProjectRootValidateRequest(project_root=project_root))
        sessions = self.list_sessions(db, limit=sessions_limit, offset=0) if include_sessions else None
        return {
            "service": self.settings.service_name,
            "capabilities": self.capabilities(),
            "status": self.status(db),
            "project_root": root_status,
            "sessions": sessions,
            "recommended_calls": [
                {"method": "POST", "path": "/assistant/project-root/validate", "when": "project_root input changes"},
                {"method": "POST", "path": "/assistant/sessions", "when": "new chat starts"},
                {"method": "POST", "path": "/assistant/message", "when": "user sends a message"},
                {"method": "GET", "path": "/assistant/sessions", "when": "refresh session sidebar"},
            ],
            "ui": {
                "ready": True,
                "badge": "LOCAL API READY",
                "message": "로컬 assistant API가 준비되었습니다.",
                "blocked_actions": ["shell_execution", "browser_interaction", "file_write_delete"],
            },
        }

    def create_session(self, db: Session, title: str | None = None, project_root: str | None = None) -> AssistantSession:
        session = AssistantSession(
            id=uuid4().hex,
            title=title or "New local assistant session",
            project_root=project_root,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def list_sessions(self, db: Session, limit: int = 20, offset: int = 0) -> dict:
        message_counts = (
            select(
                AssistantMessage.session_id,
                func.count(AssistantMessage.id).label("messages_count"),
                func.max(AssistantMessage.id).label("last_message_id"),
            )
            .group_by(AssistantMessage.session_id)
            .subquery()
        )
        last_messages = (
            select(AssistantMessage.id, AssistantMessage.content)
        ).subquery()
        stmt = (
            select(
                AssistantSession,
                func.coalesce(message_counts.c.messages_count, 0),
                last_messages.c.content,
            )
            .outerjoin(message_counts, message_counts.c.session_id == AssistantSession.id)
            .outerjoin(last_messages, last_messages.c.id == message_counts.c.last_message_id)
            .order_by(desc(AssistantSession.updated_at))
            .limit(limit)
            .offset(offset)
        )
        sessions = []
        for session, messages_count, last_message in db.execute(stmt).all():
            sessions.append(
                {
                    "session_id": session.id,
                    "title": session.title,
                    "project_root": session.project_root,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                    "messages_count": messages_count,
                    "last_message_preview": _preview(last_message) if last_message else None,
                }
            )
        return {"sessions": sessions, "limit": limit, "offset": offset}

    def get_session(self, db: Session, session_id: str) -> AssistantSession | None:
        stmt = (
            select(AssistantSession)
            .where(AssistantSession.id == session_id)
            .options(selectinload(AssistantSession.messages))
        )
        return db.scalars(stmt).first()

    def list_session_messages(self, db: Session, session_id: str, limit: int = 50, offset: int = 0) -> dict | None:
        session_exists = db.scalar(select(func.count(AssistantSession.id)).where(AssistantSession.id == session_id)) or 0
        if session_exists == 0:
            return None
        total = db.scalar(select(func.count(AssistantMessage.id)).where(AssistantMessage.session_id == session_id)) or 0
        stmt = (
            select(AssistantMessage)
            .where(AssistantMessage.session_id == session_id)
            .order_by(AssistantMessage.created_at, AssistantMessage.id)
            .limit(limit)
            .offset(offset)
        )
        return {
            "session_id": session_id,
            "total_messages": total,
            "limit": limit,
            "offset": offset,
            "messages": [_message_to_item(message) for message in db.scalars(stmt).all()],
        }

    async def handle_message(self, db: Session, request: AssistantMessageRequest) -> dict:
        session = self._get_or_create_session(db, request)
        intent = request.mode if request.mode != "auto" else self._detect_intent(request.message)
        self._record_message(db, session, "user", request.message, "input", None)

        if intent == "ask":
            chat_log = await self.rag_service.ask(db, request.message, system_prompt=None, temperature=request.temperature)
            response = {
                "session_id": session.id,
                "type": "answer",
                "answer": chat_log.answer,
                "used_documents": False,
                "sources": [],
                "request_id": str(chat_log.id),
                "safety": _safety(),
                "ui": _ui("answer", "info", chat_log.answer),
            }
        elif intent == "ask_with_docs":
            chat_log = await self.rag_service.ask_with_docs(
                db,
                request.message,
                top_k=request.top_k,
                temperature=request.temperature,
            )
            sources = json.loads(chat_log.used_sources_json or "[]")
            response = {
                "session_id": session.id,
                "type": "answer",
                "answer": chat_log.answer,
                "used_documents": True,
                "sources": sources,
                "request_id": str(chat_log.id),
                "safety": _safety(),
                "ui": _ui("answer", "info", chat_log.answer),
            }
        elif intent == "search":
            results = await self.search_service.search(_clean_search_query(request.message), top_k=request.top_k)
            response = {
                "session_id": session.id,
                "type": "search_results",
                "answer": f"{len(results)}개 검색 결과를 찾았습니다.",
                "data": {"query": _clean_search_query(request.message), "results": results},
                "used_documents": True,
                "sources": _sources_from_results(results),
                "safety": _safety(),
                "ui": _ui("search_results", "info", f"{len(results)}개 검색 결과"),
            }
        elif intent == "index_preview":
            folder_path = request.project_root or session.project_root or _extract_path(request.message)
            if not folder_path:
                response = {
                    "session_id": session.id,
                    "type": "needs_project_root",
                    "answer": "폴더 색인 미리보기를 하려면 project_root가 필요합니다.",
                    "data": {"required_field": "project_root"},
                    "safety": _safety(),
                    "ui": _ui("needs_project_root", "warning", "project root 필요"),
                }
            else:
                preview = self.document_service.preview_index_folder(folder_path, recursive=True)
                response = {
                    "session_id": session.id,
                    "type": "index_preview",
                    "answer": f"색인 미리보기 완료: 파일 {preview['files_count']}개, 예상 chunk {preview['chunks_estimated']}개입니다.",
                    "data": preview,
                    "safety": _safety(),
                    "ui": _ui("index_preview", "info", "색인 미리보기 완료"),
                }
        elif intent == "shell_dry_run":
            command = _extract_shell_command(request.message)
            result = dry_run_shell_command(command)
            response = {
                "session_id": session.id,
                "type": "shell_dry_run",
                "answer": result["reason"],
                "data": result,
                "safety": _safety(shell_status=result["status"]),
                "ui": _ui("shell_dry_run", "warning" if result["status"] == "blocked" else "info", result["status"]),
            }
        elif intent == "agent_plan":
            run = self.agent_service.create_plan(db, request.message)
            response = {
                "session_id": session.id,
                "type": "agent_plan",
                "answer": "실행형 요청은 안전한 agent plan으로만 기록했습니다. 실제 shell/browser/file-write 실행은 하지 않았습니다.",
                "data": self.agent_service.to_response(run),
                "safety": _safety(),
                "ui": _ui("agent_plan", "warning", "실행 대신 계획만 생성"),
            }
        else:
            status = get_project_status()
            response = {
                "session_id": session.id,
                "type": "status",
                "answer": f"현재 차수는 {status['current_phase']['phase']}차입니다.",
                "data": status,
                "safety": _safety(),
                "ui": _ui("status", "info", f"{status['current_phase']['phase']}차"),
            }

        self._record_message(db, session, "assistant", response.get("answer") or "", response["type"], response)
        return response

    def validate_project_root(self, request: ProjectRootValidateRequest) -> dict:
        raw = request.project_root
        try:
            resolved = Path(raw).expanduser().resolve()
        except RuntimeError:
            resolved = Path(raw).expanduser()
        allowed_roots = _allowed_roots(self.settings.agent_allowed_roots)
        inside_allowed = any(_is_relative_to(resolved, root) for root in allowed_roots)
        exists = resolved.exists()
        is_dir = resolved.is_dir()
        safe = exists and is_dir and inside_allowed
        return {
            "project_root": raw,
            "resolved_path": str(resolved),
            "exists": exists,
            "is_dir": is_dir,
            "inside_allowed_roots": inside_allowed,
            "allowed_roots": [str(root) for root in allowed_roots],
            "safe_for_read_only_agent": safe,
            "message": "read-only agent root로 사용할 수 있습니다." if safe else "존재하는 폴더이고 AGENT_ALLOWED_ROOTS 안에 있어야 합니다.",
        }

    def shell_policy(self) -> dict:
        return get_shell_policy()

    def _get_or_create_session(self, db: Session, request: AssistantMessageRequest) -> AssistantSession:
        if request.session_id:
            session = self.get_session(db, request.session_id)
            if session is not None:
                return session
        return self.create_session(db, title=_title_from_message(request.message), project_root=request.project_root)

    def _record_message(
        self,
        db: Session,
        session: AssistantSession,
        role: str,
        content: str,
        message_type: str,
        payload: dict | None,
    ) -> None:
        message = AssistantMessage(
            session_id=session.id,
            role=role,
            content=content,
            message_type=message_type,
            payload_json=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
        )
        db.add(message)
        db.commit()

    def _detect_intent(self, message: str) -> str:
        lowered = message.lower()
        if any(keyword in lowered for keyword in ["상태", "status", "다음", "next", "차수"]):
            return "status"
        if any(keyword in lowered for keyword in ["shell", "터미널", "명령", "command", "실행"]):
            return "shell_dry_run"
        if any(keyword in lowered for keyword in ["색인", "index", "폴더", "folder"]):
            return "index_preview"
        if any(keyword in lowered for keyword in ["검색", "search", "찾아줘", "찾아"]):
            return "search"
        if any(keyword in lowered for keyword in ["브라우저", "browser", "웹 열", "클릭", "삭제", "수정", "저장"]):
            return "agent_plan"
        return "ask_with_docs"


def session_to_response(session: AssistantSession) -> dict:
    messages = sorted(session.messages, key=lambda item: item.created_at)
    return {
        "session_id": session.id,
        "title": session.title,
        "project_root": session.project_root,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "message_type": message.message_type,
                "payload": json.loads(message.payload_json) if message.payload_json else None,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


def _message_to_item(message: AssistantMessage) -> dict:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "message_type": message.message_type,
        "payload": json.loads(message.payload_json) if message.payload_json else None,
        "created_at": message.created_at,
    }


def _safety(shell_status: str = "blocked") -> dict:
    return {
        "shell_execution": "disabled",
        "shell_dry_run": shell_status,
        "browser_interaction": "blocked",
        "file_write_delete": "blocked",
        "folder_index": "preview-only via assistant",
        "external_llm_api": "not-used",
    }


def _ui(response_type: str, severity: str, primary_text: str) -> dict:
    return {
        "response_type": response_type,
        "severity": severity,
        "primary_text": primary_text[:160],
        "display": "message" if response_type == "answer" else "panel",
    }


def _title_from_message(message: str) -> str:
    normalized = " ".join(message.split())
    return normalized[:60] or "New local assistant session"


def _clean_search_query(message: str) -> str:
    query = re.sub(r"^(검색|search)\s*[:：]?", "", message.strip(), flags=re.IGNORECASE)
    return query.strip() or message


def _sources_from_results(results: list[dict]) -> list[dict]:
    return [
        {
            "document_id": result["document_id"],
            "filename": result["filename"],
            "chunk_index": result["chunk_index"],
            "chunk_id": result["chunk_id"],
        }
        for result in results
    ]


def _extract_shell_command(message: str) -> str:
    match = re.search(r"`([^`]+)`", message)
    if match:
        return match.group(1)
    prefixes = ["shell", "터미널", "명령", "command", "실행"]
    lowered = message.lower()
    for prefix in prefixes:
        index = lowered.find(prefix)
        if index >= 0:
            return message[index + len(prefix) :].strip(" :：") or message
    return message


def _extract_path(text: str) -> str | None:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1)
    path_like = re.search(r"((?:~|\.)?/[\w가-힣 ._~\-/]+|(?:\.{1,2}/[\w가-힣 ._~\-/]+))", text)
    return path_like.group(1).strip() if path_like else None


def _allowed_roots(value: str) -> list[Path]:
    roots = []
    for raw_root in value.split(","):
        raw_root = raw_root.strip()
        if raw_root:
            roots.append(Path(raw_root).expanduser().resolve())
    return roots or [Path(".").resolve()]


def _root_summaries(value: str) -> list[dict]:
    return [
        {
            "path": str(root),
            "exists": root.exists(),
            "is_dir": root.is_dir(),
        }
        for root in _allowed_roots(value)
    ]


def _csv_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
