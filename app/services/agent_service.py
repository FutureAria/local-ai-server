import json

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.models import AgentRun


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
        }

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
