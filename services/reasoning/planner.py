from __future__ import annotations

import os
from typing import Protocol

from reasoning.client import LLMClientError, OpenAICompatibleClient
from reasoning.models import AgentAction, AgentResult, ReconcileResult, SubtaskPlan, TaskPlan
from reasoning.prompts import (
    DECOMPOSE_SYSTEM,
    DECOMPOSE_USER,
    NEXT_ACTION_SYSTEM,
    NEXT_ACTION_USER,
    RECONCILE_SYSTEM,
    RECONCILE_USER,
)


class PlannerError(Exception):
    pass


class AshPlanner(Protocol):
    async def decompose(self, intent: str, n_agents: int, base_url: str) -> TaskPlan: ...
    async def next_action(
        self, goal: str, url: str, snapshot: str
    ) -> AgentAction: ...
    async def reconcile(self, intent: str, results: list[AgentResult]) -> ReconcileResult: ...


class LLMAshPlanner:
    def __init__(self, client: OpenAICompatibleClient | None = None) -> None:
        self._client = client or OpenAICompatibleClient()

    async def decompose(self, intent: str, n_agents: int, base_url: str) -> TaskPlan:
        user = DECOMPOSE_USER.format(intent=intent, n_agents=n_agents, base_url=base_url.rstrip("/"))
        try:
            data = await self._client.chat_json(DECOMPOSE_SYSTEM, user)
        except LLMClientError as exc:
            raise PlannerError(str(exc)) from exc
        subtasks = []
        for i, raw in enumerate(data.get("subtasks", [])[:n_agents]):
            agent_id = raw.get("agent_id") or f"agent-{i + 1:02d}"
            subtasks.append(
                SubtaskPlan(
                    agent_id=agent_id,
                    goal=raw.get("goal", intent),
                    start_url=raw.get("start_url", f"{base_url.rstrip('/')}/"),
                )
            )
        while len(subtasks) < n_agents:
            idx = len(subtasks) + 1
            subtasks.append(
                SubtaskPlan(
                    agent_id=f"agent-{idx:02d}",
                    goal=intent,
                    start_url=f"{base_url.rstrip('/')}/",
                )
            )
        return TaskPlan(intent=intent, subtasks=subtasks[:n_agents])

    async def next_action(self, goal: str, url: str, snapshot: str) -> AgentAction:
        user = NEXT_ACTION_USER.format(goal=goal, url=url, snapshot=snapshot[:4000])
        try:
            data = await self._client.chat_json(NEXT_ACTION_SYSTEM, user)
        except LLMClientError as exc:
            raise PlannerError(str(exc)) from exc
        return AgentAction(
            action=data.get("action", "failed"),
            url=data.get("url"),
            selector=data.get("selector"),
            thought=data.get("thought", ""),
            result=data.get("result"),
        )

    async def reconcile(self, intent: str, results: list[AgentResult]) -> ReconcileResult:
        lines = "\n".join(
            f"- {r.agent_id} ({r.fingerprint_seed[:8]}…): {r.summary}" for r in results
        )
        user = RECONCILE_USER.format(intent=intent, results=lines or "(no results)")
        try:
            data = await self._client.chat_json(RECONCILE_SYSTEM, user)
        except LLMClientError as exc:
            raise PlannerError(str(exc)) from exc
        return ReconcileResult(summary=data.get("summary", "Task completed."))


class MockAshPlanner:
    """Deterministic planner for CI and ASH_DEMO_MOCK=1."""

    async def decompose(self, intent: str, n_agents: int, base_url: str) -> TaskPlan:
        base = base_url.rstrip("/")
        goals = [
            "Read the stock badge and report availability",
            "Read the product title on the storefront",
            "Check whether the buy button is enabled",
            "Summarize the demo product page state",
            "Verify SKU line is visible",
        ]
        subtasks = [
            SubtaskPlan(
                agent_id=f"agent-{i + 1:02d}",
                goal=goals[i % len(goals)],
                start_url=f"{base}/",
            )
            for i in range(n_agents)
        ]
        return TaskPlan(intent=intent, subtasks=subtasks)

    async def next_action(self, goal: str, url: str, snapshot: str) -> AgentAction:
        if snapshot.strip() and ("stock" in snapshot.lower() or "product=" in snapshot.lower()):
            return AgentAction(
                action="done",
                thought="Page loaded with stock information visible.",
                result=f"{goal}: {snapshot[:120]}",
            )
        return AgentAction(
            action="goto",
            url=url,
            thought="Navigate to the demo storefront.",
        )

    async def reconcile(self, intent: str, results: list[AgentResult]) -> ReconcileResult:
        parts = "; ".join(r.summary for r in results if r.summary)
        return ReconcileResult(
            summary=f"Delegated: {intent}. The swarm reported: {parts or 'completed checks on the demo storefront.'}"
        )


def get_planner() -> AshPlanner:
    if os.environ.get("ASH_DEMO_MOCK", "").lower() in ("1", "true", "yes"):
        return MockAshPlanner()
    return LLMAshPlanner()
