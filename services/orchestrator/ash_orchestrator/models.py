from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RestockAlert(BaseModel):
    watch_uuid: str = ""
    watch_url: str = ""
    title: str = ""
    message: str = ""
    current_snapshot: str | None = None
    previous_snapshot: str | None = None


def parse_changedetection_notification(payload: dict[str, Any]) -> RestockAlert:
    """Parse webhook/notification payload from changedetection.io."""
    return RestockAlert(
        watch_uuid=str(payload.get("uuid") or payload.get("watch_uuid") or ""),
        watch_url=str(payload.get("watch_url") or payload.get("url") or ""),
        title=str(payload.get("title") or "Restock alert"),
        message=str(payload.get("message") or payload.get("body") or ""),
        current_snapshot=payload.get("current_snapshot"),
        previous_snapshot=payload.get("previous_snapshot"),
    )


class WatchRegistration(BaseModel):
    url: str
    title: str = "Ash Agents restock watch"
    tag: str = "ash-sentinel"
    proxy: str | None = None


class AssistPolicy(BaseModel):
    max_quantity: int = Field(default=1, le=1, description="Assist-only: single unit handoff")
    allow_autonomous_checkout: bool = False
