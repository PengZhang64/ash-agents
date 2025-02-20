from __future__ import annotations

from pydantic import BaseModel, Field


class DelegateBody(BaseModel):
    intent: str | None = None
    preset: str | None = None
    agents: int = Field(default=3, ge=1, le=5)


class DelegateResponse(BaseModel):
    task_id: str
    agents: list[dict[str, str]]
    intent: str
