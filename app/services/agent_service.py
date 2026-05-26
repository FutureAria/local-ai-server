import json
import ipaddress
import re
import socket
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.models import AgentRun

SENSITIVE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".netrc",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}
SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".crt", ".cer"}
SENSITIVE_PATH_PARTS = {".ssh", ".gnupg", ".aws", ".config/gcloud"}


class AgentService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def create_plan(self, db: Session, instruction: str) -> AgentRun:
        actions = self._plan_actions(instruction)
        risk_level = self._overall_risk(actions)
        plan = {
            "actions": actions,
            "note": "preview-only agent plan입니다. 실제 웹 이동, 폴더 열기, shell 실행은 수행하지 않습니다.",
        }
        run = AgentRun(
            instruction=instruction,
            status="planned",
            risk_level=risk_level,
            plan_json=json.dumps(plan, ensure_ascii=False),
            execution_enabled=1 if self.settings.agent_execution_enabled else 0,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def list_runs(self, db: Session, limit: int = 20, offset: int = 0) -> list[AgentRun]:
        stmt = select(AgentRun).order_by(desc(AgentRun.created_at)).limit(limit).offset(offset)
        return list(db.scalars(stmt).all())

    def get_run(self, db: Session, run_id: int) -> AgentRun | None:
        return db.get(AgentRun, run_id)

    def approve_run(self, db: Session, run_id: int) -> AgentRun | None:
        run = self.get_run(db, run_id)
        if run is None:
            return None
        if run.status == "rejected":
            raise ValueError("거절된 agent run은 승인할 수 없습니다.")
        if run.status == "planned":
            run.status = "approved_pending_execution"
            db.commit()
            db.refresh(run)
        return run

    def reject_run(self, db: Session, run_id: int) -> AgentRun | None:
        run = self.get_run(db, run_id)
        if run is None:
            return None
        if run.status == "approved_pending_execution":
            raise ValueError("이미 승인된 agent run은 거절할 수 없습니다.")
        if run.status == "planned":
            run.status = "rejected"
            db.commit()
            db.refresh(run)
        return run

    def execute_run(self, db: Session, run_id: int) -> AgentRun | None:
        run = self.get_run(db, run_id)
        if run is None:
            return None
        if run.status != "approved_pending_execution":
            raise ValueError("승인 대기 상태의 agent run만 실행할 수 있습니다.")

        plan = json.loads(run.plan_json)
        results = []
        all_completed = True
        for action in plan["actions"]:
            result = self._execute_action(action)
            result["action_index"] = len(results)
            results.append(result)
            if result["status"] != "completed":
                all_completed = False

        plan["execution_results"] = results
        plan["note"] = "실행 엔진이 결과를 기록했습니다. 기본 설정에서는 고위험 도구가 blocked 됩니다."
        run.plan_json = json.dumps(plan, ensure_ascii=False)
        run.status = "completed" if all_completed else "blocked"
        db.commit()
        db.refresh(run)
        return run

    def dry_run(self, db: Session, run_id: int) -> AgentRun | None:
        run = self.get_run(db, run_id)
        if run is None:
            return None
        if run.status in {"rejected", "completed"}:
            raise ValueError("거절되었거나 완료된 agent run은 dry-run할 수 없습니다.")

        plan = json.loads(run.plan_json)
        dry_run_results = []
        for action in plan["actions"]:
            result = self._dry_run_action(action)
            result["action_index"] = len(dry_run_results)
            dry_run_results.append(result)

        plan["dry_run_results"] = dry_run_results
        plan["note"] = "dry-run 결과를 기록했습니다. dry-run은 실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작을 수행하지 않습니다."
        run.plan_json = json.dumps(plan, ensure_ascii=False)
        db.commit()
        db.refresh(run)
        return run

    def to_response(self, run: AgentRun) -> dict:
        plan = json.loads(run.plan_json)
        return {
            "run_id": run.id,
            "status": run.status,
            "risk_level": run.risk_level,
            "execution_enabled": bool(run.execution_enabled),
            "actions": plan["actions"],
            "note": plan["note"],
        }

    def to_summary(self, run: AgentRun) -> dict:
        return {
            "id": run.id,
            "instruction_preview": _preview(run.instruction),
            "status": run.status,
            "risk_level": run.risk_level,
            "execution_enabled": bool(run.execution_enabled),
            "created_at": run.created_at,
        }

    def to_detail(self, run: AgentRun) -> dict:
        plan = json.loads(run.plan_json)
        return {
            **self.to_summary(run),
            "instruction": run.instruction,
            "actions": plan["actions"],
            "dry_run_results": plan.get("dry_run_results", []),
            "execution_results": plan.get("execution_results", []),
        }

    def get_results(self, db: Session, run_id: int) -> list[dict] | None:
        run = self.get_run(db, run_id)
        if run is None:
            return None
        plan = json.loads(run.plan_json)
        return plan.get("execution_results", [])

    def get_actions(self, db: Session, run_id: int) -> list[dict] | None:
        run = self.get_run(db, run_id)
        if run is None:
            return None
        plan = json.loads(run.plan_json)
        dry_run_by_index = {
            result.get("action_index"): result for result in plan.get("dry_run_results", [])
        }
        execution_by_index = {
            result.get("action_index"): result for result in plan.get("execution_results", [])
        }
        actions = []
        for index, action in enumerate(plan["actions"]):
            actions.append(
                {
                    "action_index": index,
                    **action,
                    "status": _action_status(index, dry_run_by_index, execution_by_index),
                    "dry_run_result": dry_run_by_index.get(index),
                    "execution_result": execution_by_index.get(index),
                }
            )
        return actions

    def _plan_actions(self, instruction: str) -> list[dict]:
        lowered = instruction.lower()
        actions: list[dict] = []
        if any(keyword in lowered for keyword in ["웹", "사이트", "브라우저", "url", "http", "페이지"]):
            actions.append(
                _action(
                    tool="browser",
                    action="open_preview",
                    target=instruction,
                    risk_level="high",
                    reason="브라우저 이동/클릭은 외부 사이트와 사용자 세션에 영향을 줄 수 있어 승인 기반 preview로만 계획합니다.",
                )
            )
        if any(keyword in lowered for keyword in ["검색", "찾아", "search"]):
            actions.append(
                _action(
                    tool="web_search",
                    action="search_preview",
                    target=instruction,
                    risk_level="medium",
                    reason="외부 검색 결과는 신뢰할 수 없는 입력이므로 실제 실행 전 검토가 필요합니다.",
                )
            )
        if any(keyword in lowered for keyword in ["폴더", "파일", "finder", "열어", "저장"]):
            actions.append(
                _action(
                    tool="file",
                    action="file_preview",
                    target=instruction,
                    risk_level="high",
                    reason="로컬 파일/폴더 접근은 workspace 경계와 개인정보 확인이 필요해 실제 열기 전 승인이 필요합니다.",
                )
            )
        if any(keyword in lowered for keyword in ["shell", "터미널", "명령", "실행", "삭제", "설치"]):
            actions.append(
                _action(
                    tool="shell",
                    action="shell_preview",
                    target=instruction,
                    risk_level="high",
                    reason="shell 실행은 시스템 변경 가능성이 있어 기본 비활성화하고 preview만 제공합니다.",
                )
            )
        if not actions:
            actions.append(
                {
                    "tool": "rag",
                    "action": "answer_with_context",
                    "target": instruction,
                    "risk_level": "low",
                    "requires_approval": False,
                    "execution_enabled": False,
                    "reason": "실행 도구가 필요하지 않은 지식형 요청으로 분류했습니다.",
                }
            )
        return actions

    def _overall_risk(self, actions: list[dict]) -> str:
        if any(action["risk_level"] == "high" for action in actions):
            return "high"
        if any(action["risk_level"] == "medium" for action in actions):
            return "medium"
        return "low"

    def _execute_action(self, action: dict) -> dict:
        if action["tool"] == "rag":
            return {
                "tool": action["tool"],
                "action": action["action"],
                "status": "completed",
                "message": "지식형 요청으로 분류되어 별도 실행 도구 없이 완료 처리했습니다.",
            }

        if not self.settings.agent_execution_enabled:
            return {
                "tool": action["tool"],
                "action": action["action"],
                "status": "blocked",
                "message": "AGENT_EXECUTION_ENABLED=false 상태라 실제 실행을 차단했습니다.",
            }

        if action["tool"] == "file":
            return self._execute_file_action(action)
        if action["tool"] in {"browser", "web_search"}:
            return self._execute_web_action(action)

        return {
            "tool": action["tool"],
            "action": action["action"],
            "status": "blocked",
            "message": "이 도구의 실제 실행기는 아직 연결되지 않았습니다. allowlist와 sandbox 정책이 필요합니다.",
        }

    def _dry_run_action(self, action: dict) -> dict:
        if action["tool"] == "rag":
            return {
                "tool": action["tool"],
                "action": action["action"],
                "status": "allowed",
                "execution_mode": "no_tool_execution",
                "requires_approval": False,
                "would_execute": False,
                "message": "지식형 요청입니다. 별도 로컬 실행 도구 없이 처리할 수 있습니다.",
            }

        if action["tool"] == "file":
            return self._dry_run_file_action(action)
        if action["tool"] in {"browser", "web_search"}:
            return self._dry_run_web_action(action)
        if action["tool"] == "shell":
            return {
                "tool": action["tool"],
                "action": action["action"],
                "status": "disabled",
                "execution_mode": "blocked_shell",
                "requires_approval": True,
                "would_execute": False,
                "message": "shell 실행기는 2차 A단계에서 비활성화되어 있습니다. 명령 실행은 수행하지 않습니다.",
            }

        return {
            "tool": action["tool"],
            "action": action["action"],
            "status": "disabled",
            "execution_mode": "unsupported_tool",
            "requires_approval": True,
            "would_execute": False,
            "message": "지원하지 않는 agent tool입니다.",
        }

    def _dry_run_file_action(self, action: dict) -> dict:
        base = {
            "tool": action["tool"],
            "action": action["action"],
            "requires_approval": True,
            "execution_mode": "read_only_file_preview",
            "would_execute": False,
            "execute_phase_would_run": bool(self.settings.agent_execution_enabled),
        }
        if not self.settings.agent_execution_enabled:
            return {
                **base,
                "status": "disabled",
                "would_execute": False,
                "message": "AGENT_EXECUTION_ENABLED=false 상태라 실제 파일/폴더 접근은 차단됩니다.",
            }

        requested_path = _extract_path(action["target"]) or "."
        try:
            resolved_path = Path(requested_path).expanduser().resolve()
        except RuntimeError:
            return {**base, "status": "blocked", "would_execute": False, "message": "요청 경로를 해석할 수 없습니다."}

        allowed_roots = _allowed_roots(self.settings.agent_allowed_roots)
        if not any(_is_relative_to(resolved_path, root) for root in allowed_roots):
            return {
                **base,
                "status": "blocked",
                "would_execute": False,
                "path": str(resolved_path),
                "message": "허용된 root 밖의 파일/폴더 접근은 실행 전 정책에서 차단됩니다.",
            }
        if not resolved_path.exists():
            return {
                **base,
                "status": "blocked",
                "would_execute": False,
                "path": str(resolved_path),
                "message": "요청한 파일/폴더가 존재하지 않아 실행할 수 없습니다.",
            }
        if _is_sensitive_path(resolved_path):
            return {
                **base,
                "status": "blocked",
                "would_execute": False,
                "path": str(resolved_path),
                "message": "민감 파일 또는 민감 폴더로 보여 실행 전 정책에서 차단됩니다.",
            }
        if resolved_path.is_dir():
            return {
                **base,
                "status": "allowed",
                "path": str(resolved_path),
                "operation": "list_directory",
                "message": "허용 root 안의 폴더 목록을 read-only로 조회할 수 있습니다.",
            }

        extension = resolved_path.suffix.lower()
        allowed_extensions = _csv_set(self.settings.agent_file_preview_extensions)
        if extension not in allowed_extensions:
            return {
                **base,
                "status": "blocked",
                "would_execute": False,
                "path": str(resolved_path),
                "operation": "preview_file",
                "message": f"파일 preview가 허용되지 않은 확장자입니다: {extension or '(no extension)'}",
            }
        size_bytes = resolved_path.stat().st_size
        if size_bytes > self.settings.agent_file_preview_max_bytes:
            return {
                **base,
                "status": "blocked",
                "would_execute": False,
                "path": str(resolved_path),
                "operation": "preview_file",
                "size_bytes": size_bytes,
                "message": "파일이 AGENT_FILE_PREVIEW_MAX_BYTES보다 커서 실행 전 정책에서 차단됩니다.",
            }
        return {
            **base,
            "status": "allowed",
            "path": str(resolved_path),
            "operation": "preview_file",
            "extension": extension,
            "size_bytes": size_bytes,
            "message": "허용 root 안의 텍스트 파일을 read-only로 preview할 수 있습니다.",
        }

    def _dry_run_web_action(self, action: dict) -> dict:
        base = {
            "tool": action["tool"],
            "action": action["action"],
            "requires_approval": True,
            "execution_mode": "read_only_url_fetch",
            "would_execute": bool(self.settings.agent_execution_enabled and self.settings.agent_web_fetch_enabled),
        }
        url = _extract_url(action["target"])
        if not url:
            return {
                **base,
                "status": "blocked",
                "would_execute": False,
                "message": "명시적인 http 또는 https URL이 없어 URL fetch를 실행할 수 없습니다.",
            }
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return {**base, "status": "blocked", "would_execute": False, "url": url, "message": "http/https URL만 허용합니다."}
        if not self.settings.agent_execution_enabled:
            return {
                **base,
                "status": "disabled",
                "would_execute": False,
                "url": url,
                "message": "AGENT_EXECUTION_ENABLED=false 상태라 URL fetch가 차단됩니다.",
            }
        if not self.settings.agent_web_fetch_enabled:
            return {
                **base,
                "status": "disabled",
                "would_execute": False,
                "url": url,
                "message": "AGENT_WEB_FETCH_ENABLED=false 상태라 URL fetch가 차단됩니다.",
            }
        return {
            **base,
            "status": "allowed",
            "url": url,
            "operation": "fetch_url_preview",
            "max_bytes": self.settings.agent_web_fetch_max_bytes,
            "message": "명시 URL을 read-only로 fetch할 수 있습니다. 브라우저 클릭/로그인/입력은 수행하지 않습니다.",
        }

    def _execute_file_action(self, action: dict) -> dict:
        requested_path = _extract_path(action["target"]) or "."
        try:
            resolved_path = Path(requested_path).expanduser().resolve()
        except RuntimeError:
            return _blocked_result(action, "요청 경로를 해석할 수 없습니다.")

        allowed_roots = _allowed_roots(self.settings.agent_allowed_roots)
        if not any(_is_relative_to(resolved_path, root) for root in allowed_roots):
            return _blocked_result(action, "허용된 root 밖의 파일/폴더 접근은 차단했습니다.")

        if not resolved_path.exists():
            return _blocked_result(action, "요청한 파일/폴더가 존재하지 않습니다.")

        if _is_sensitive_path(resolved_path):
            return _blocked_result(action, "민감 파일 또는 민감 폴더로 보이는 경로는 read-only preview에서도 차단했습니다.")

        if resolved_path.is_dir():
            items = []
            for child in sorted(resolved_path.iterdir(), key=lambda item: item.name.lower())[:50]:
                items.append(
                    {
                        "name": child.name,
                        "type": "dir" if child.is_dir() else "file",
                        "sensitive": _is_sensitive_path(child),
                    }
                )
            return {
                "tool": action["tool"],
                "action": action["action"],
                "status": "completed",
                "message": "허용된 root 안의 폴더 목록을 read-only로 조회했습니다.",
                "path": str(resolved_path),
                "items": items,
            }

        extension = resolved_path.suffix.lower()
        allowed_extensions = _csv_set(self.settings.agent_file_preview_extensions)
        if extension not in allowed_extensions:
            return _blocked_result(action, f"파일 preview가 허용되지 않은 확장자입니다: {extension or '(no extension)'}")

        size_bytes = resolved_path.stat().st_size
        if size_bytes > self.settings.agent_file_preview_max_bytes:
            return _blocked_result(action, "파일이 AGENT_FILE_PREVIEW_MAX_BYTES보다 커서 내용 preview를 차단했습니다.")

        try:
            raw = resolved_path.read_bytes()
        except OSError as exc:
            return _blocked_result(action, f"파일을 읽을 수 없습니다: {exc}")
        if _looks_binary(raw):
            return _blocked_result(action, "binary 파일로 보여 내용 preview를 차단했습니다.")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            return _blocked_result(action, "UTF-8 텍스트 파일만 preview할 수 있습니다.")

        return {
            "tool": action["tool"],
            "action": action["action"],
            "status": "completed",
            "message": "허용된 root 안의 파일 내용을 read-only로 preview했습니다.",
            "path": str(resolved_path),
            "extension": extension,
            "size_bytes": size_bytes,
            "line_count": content.count("\n") + (1 if content else 0),
            "content_preview": content[:2000],
            "truncated": len(content) > 2000,
        }

    def _execute_web_action(self, action: dict) -> dict:
        url = _extract_url(action["target"])
        if not url:
            return _blocked_result(action, "명시적인 http 또는 https URL이 없어 웹 fetch를 차단했습니다.")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return _blocked_result(action, "http/https URL만 허용합니다.")
        host_block_reason = _public_http_host_block_reason(url)
        if host_block_reason:
            return _blocked_result(action, host_block_reason)
        if not self.settings.agent_web_fetch_enabled:
            return _blocked_result(action, "AGENT_WEB_FETCH_ENABLED=false 상태라 웹 fetch를 차단했습니다.")

        try:
            with httpx.stream("GET", url, timeout=10.0, follow_redirects=False) as response:
                final_url = str(response.url)
                final_host_block_reason = _public_http_host_block_reason(final_url)
                if final_host_block_reason:
                    return _blocked_result(action, final_host_block_reason)
                if 300 <= response.status_code < 400:
                    redirect_target = response.headers.get("location")
                    if redirect_target:
                        redirect_url = urljoin(final_url, redirect_target)
                        redirect_block_reason = _public_http_host_block_reason(redirect_url)
                        if redirect_block_reason:
                            return _blocked_result(action, f"redirect target blocked: {redirect_block_reason}")
                    return _blocked_result(action, "redirect 응답은 자동으로 따라가지 않습니다. redirect target 검증 후 별도 승인된 URL만 fetch하세요.")
                content_type = response.headers.get("content-type", "")
                chunks = []
                bytes_read = 0
                truncated = False
                for chunk in response.iter_bytes():
                    bytes_read += len(chunk)
                    if bytes_read > self.settings.agent_web_fetch_max_bytes:
                        remaining = self.settings.agent_web_fetch_max_bytes - sum(len(item) for item in chunks)
                        if remaining > 0:
                            chunks.append(chunk[:remaining])
                        truncated = True
                        break
                    chunks.append(chunk)
                body = b"".join(chunks)
                status_code = response.status_code
        except httpx.HTTPError as exc:
            return _blocked_result(action, f"웹 fetch 실패: {exc}")

        text_preview = ""
        title = ""
        links: list[dict] = []
        if "text" in content_type or "html" in content_type:
            decoded = body.decode(response.encoding or "utf-8", errors="replace")
            if "html" in content_type:
                html_summary = _extract_html_summary(decoded, final_url)
                title = html_summary["title"]
                links = html_summary["links"]
                text_preview = html_summary["text_preview"]
            else:
                text_preview = decoded[:1000]

        return {
            "tool": action["tool"],
            "action": action["action"],
            "status": "completed",
            "message": "명시 URL을 read-only로 fetch했습니다. 브라우저 클릭/로그인/입력은 수행하지 않았습니다.",
            "url": final_url,
            "status_code": status_code,
            "content_type": content_type,
            "bytes_read": len(body),
            "truncated": truncated,
            "title": title,
            "links": links,
            "text_preview": text_preview,
        }


def _action(tool: str, action: str, target: str, risk_level: str, reason: str) -> dict:
    return {
        "tool": tool,
        "action": action,
        "target": target,
        "risk_level": risk_level,
        "requires_approval": True,
        "execution_enabled": False,
        "reason": reason,
    }


def _preview(text: str, max_length: int = 120) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def _blocked_result(action: dict, message: str) -> dict:
    return {
        "tool": action["tool"],
        "action": action["action"],
        "status": "blocked",
        "message": message,
    }


def _action_status(index: int, dry_run_by_index: dict, execution_by_index: dict) -> str:
    if index in execution_by_index:
        return execution_by_index[index].get("status", "executed")
    if index in dry_run_by_index:
        dry_status = dry_run_by_index[index].get("status", "dry_run")
        return f"dry_run_{dry_status}"
    return "pending"


def _allowed_roots(value: str) -> list[Path]:
    roots = []
    for raw_root in value.split(","):
        raw_root = raw_root.strip()
        if raw_root:
            roots.append(Path(raw_root).expanduser().resolve())
    return roots or [Path(".").resolve()]


def _csv_set(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def _is_sensitive_path(path: Path) -> bool:
    name = path.name.lower()
    suffix = path.suffix.lower()
    lowered_parts = [part.lower() for part in path.parts]
    if name in SENSITIVE_FILE_NAMES or suffix in SENSITIVE_SUFFIXES:
        return True
    if any(part in SENSITIVE_PATH_PARTS for part in lowered_parts):
        return True
    return any(keyword in name for keyword in ["secret", "token", "credential", "password", "passwd"])


def _looks_binary(raw: bytes) -> bool:
    if not raw:
        return False
    sample = raw[:2048]
    if b"\x00" in sample:
        return True
    control_bytes = sum(1 for byte in sample if byte < 9 or (13 < byte < 32))
    return control_bytes / len(sample) > 0.10


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _extract_url(text: str) -> str | None:
    match = re.search(r"https?://[^\s\"']+", text)
    return match.group(0) if match else None


def _public_http_host_block_reason(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "http/https URL만 허용합니다."
    if not parsed.hostname:
        return "URL hostname을 확인할 수 없어 웹 fetch를 차단했습니다."

    try:
        addresses = _resolve_host_ips(parsed.hostname)
    except OSError as exc:
        return f"URL hostname을 해석할 수 없어 웹 fetch를 차단했습니다: {exc}"

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return "private, loopback, link-local IP로 해석되는 URL은 웹 fetch에서 차단됩니다."
    return None


def _resolve_host_ips(hostname: str) -> set[str]:
    try:
        return {str(ipaddress.ip_address(hostname))}
    except ValueError:
        pass

    addresses = set()
    for item in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM):
        addresses.add(item[4][0])
    return addresses


def _extract_path(text: str) -> str | None:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1)
    path_like = re.search(r"((?:~|\.)?/[\w가-힣 ._~\-/]+|(?:\.{1,2}/[\w가-힣 ._~\-/]+))", text)
    return path_like.group(1).strip() if path_like else None


class _HTMLSummaryParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.links: list[dict] = []
        self._parts: list[str] = []
        self._ignored_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1
        if normalized == "title":
            self._in_title = True
        if normalized == "a":
            href = dict(attrs).get("href")
            if href and len(self.links) < 20:
                self.links.append({"url": urljoin(self.base_url, href), "text": ""})
        if normalized in {"p", "br", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1
        if normalized == "title":
            self._in_title = False
        if normalized in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title and not self.title:
            self.title = text
        if self._ignored_depth:
            return
        self._parts.append(text)

    def summary(self) -> dict:
        lines = [" ".join(line.split()) for line in "".join(self._parts).splitlines()]
        text = "\n".join(line for line in lines if line).strip()
        return {"title": self.title, "text_preview": text[:1000], "links": self.links}


def _extract_html_summary(html: str, base_url: str) -> dict:
    parser = _HTMLSummaryParser(base_url)
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        return {"title": "", "text_preview": html[:1000], "links": []}
    return parser.summary()
