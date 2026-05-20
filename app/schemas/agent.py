from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AgentTool = Literal["web_search", "browser", "file", "shell", "rag"]
RiskLevel = Literal["low", "medium", "high"]


class AgentPlanRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=4000)


class AgentAction(BaseModel):
    tool: AgentTool
    action: str
    target: str
    risk_level: RiskLevel
    requires_approval: bool
    execution_enabled: bool = False
    reason: str


class AgentPlanResponse(BaseModel):
    run_id: int
    status: str
    risk_level: RiskLevel
    execution_enabled: bool
    actions: list[AgentAction]
    note: str


class AgentRunSummary(BaseModel):
    id: int
    instruction_preview: str
    status: str
    risk_level: RiskLevel
    execution_enabled: bool
    created_at: datetime


class AgentRunDetail(AgentRunSummary):
    instruction: str
    actions: list[AgentAction]
    dry_run_results: list[dict] = Field(default_factory=list)
    execution_results: list[dict] = Field(default_factory=list)
