from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    action: Literal["goto", "click", "extract_text", "done", "failed"]
    url: str | None = None
    selector: str | None = None
    thought: str = ""
    result: str | None = None


class SubtaskPlan(BaseModel):
    agent_id: str
    goal: str
    start_url: str


class TaskPlan(BaseModel):
    intent: str
    subtasks: list[SubtaskPlan]


class AgentResult(BaseModel):
    agent_id: str
    goal: str
    success: bool
    summary: str
    fingerprint_seed: str


class ReconcileResult(BaseModel):
    summary: str
