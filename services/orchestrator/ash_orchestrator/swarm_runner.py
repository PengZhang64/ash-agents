from __future__ import annotations

import asyncio
import hashlib
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from ash_orchestrator.config import settings
from ash_orchestrator.event_bus import EventBus

try:
    from identity.rotation import DisposableIdentity, IdentityFactory  # type: ignore
    from identity.agent_session import AgentSession  # type: ignore
except ImportError:
    DisposableIdentity = None  # type: ignore
    IdentityFactory = None  # type: ignore
    AgentSession = None  # type: ignore

try:
    from reasoning.models import AgentAction, AgentResult, TaskPlan  # type: ignore
    from reasoning.planner import AshPlanner, PlannerError, get_planner  # type: ignore
except ImportError:
    AshPlanner = None  # type: ignore
    PlannerError = Exception  # type: ignore
    get_planner = None  # type: ignore


PRESETS: dict[str, str] = {
    "check_storefront": "Check the demo storefront and report stock status.",
}


def identity_proof(seed: str, task_id: str, agent_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = hashlib.sha256(f"{seed}:{task_id}:{agent_id}:{ts}".encode()).hexdigest()
    return f"0x{digest}"


@dataclass
class DelegateRequest:
    intent: str | None = None
    preset: str | None = None
    agents: int = 3


class SwarmRunner:
    """Whitepaper-aligned orchestration: LLM plan, isolated agents, reconcile."""

    def __init__(
        self,
        bus: EventBus,
        *,
        identity_factory: Callable[[], Any] | None = None,
        product_base_url: str | None = None,
        planner: AshPlanner | None = None,
    ) -> None:
        self._bus = bus
        self._factory = identity_factory or (IdentityFactory() if IdentityFactory else None)
        self._product_url = (product_base_url or settings.test_product_url).rstrip("/")
        self._planner = planner
        self._max_steps = int(os.environ.get("ASH_MAX_AGENT_STEPS", "8"))
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def _get_planner(self) -> AshPlanner:
        if self._planner is not None:
            return self._planner
        if get_planner is None:
            raise PlannerError("reasoning module not available")
        return get_planner()

    def resolve_intent(self, body: DelegateRequest) -> str:
        if body.preset:
            if body.preset not in PRESETS:
                raise ValueError(f"unknown preset: {body.preset}")
            return PRESETS[body.preset]
        if body.intent and body.intent.strip():
            return body.intent.strip()
        raise ValueError("intent or preset required")

    def ensure_llm_ready(self) -> None:
        if os.environ.get("ASH_DEMO_MOCK", "").lower() in ("1", "true", "yes"):
            return
        if not os.environ.get("OPENAI_API_KEY"):
            raise PlannerError("OPENAI_API_KEY is required (set in .env at repo root)")

    def start(self, body: DelegateRequest) -> tuple[str, list[dict[str, str]]]:
        self.ensure_llm_ready()
        count = max(1, min(5, body.agents))
        intent = self.resolve_intent(body)
        task_id = uuid.uuid4().hex[:12]
        agent_rows = [
            {"id": f"agent-{i:02d}", "state": "idle", "fingerprint": ""} for i in range(1, count + 1)
        ]
        self._tasks[task_id] = asyncio.create_task(self._run(task_id, intent, agent_rows, count))
        return task_id, agent_rows

    async def _emit(self, event: dict[str, Any], task_id: str) -> None:
        event.setdefault("task_id", task_id)
        await self._bus._broadcast(event)

    async def _run(self, task_id: str, intent: str, agent_rows: list[dict[str, str]], count: int) -> None:
        try:
            await self._bus.set_swarm(agent_rows)
            await self._emit(
                {"type": "layer", "layer": "you", "message": "Intent received. You do not touch the web."},
                task_id,
            )
            await self._bus.log(f"{_ts()} intent: {intent}", level="dim", task_id=task_id)

            planner = self._get_planner()
            await self._emit(
                {
                    "type": "layer",
                    "layer": "orchestration",
                    "message": "Decomposing task (private coordination)…",
                },
                task_id,
            )
            plan: TaskPlan = await planner.decompose(intent, count, self._product_url)
            for st in plan.subtasks:
                await self._emit(
                    {
                        "type": "reasoning",
                        "agent": st.agent_id,
                        "thought": f"Subtask: {st.goal}",
                        "action": "assign",
                    },
                    task_id,
                )

            results = await asyncio.gather(
                *[self._run_agent(task_id, st, agent_rows) for st in plan.subtasks]
            )

            await self._emit(
                {"type": "layer", "layer": "orchestration", "message": "Reconciling swarm results…"},
                task_id,
            )
            reconcile = await planner.reconcile(intent, list(results))
            await self._emit({"type": "reconcile", "summary": reconcile.summary}, task_id)
            await self._bus.log(f"{_ts()} reconcile: {reconcile.summary}", task_id=task_id)
            await self._emit(
                {
                    "type": "layer",
                    "layer": "you",
                    "message": "Result returned. Coordination stayed behind the wall.",
                },
                task_id,
            )

            idle = [{"id": a["id"], "state": "idle", "fingerprint": ""} for a in agent_rows]
            await self._bus.set_swarm(idle)
        except PlannerError as exc:
            await self._bus.log(f"{_ts()} error: {exc}", task_id=task_id)
            raise
        except Exception as exc:  # noqa: BLE001
            await self._bus.log(f"{_ts()} error: {exc}", task_id=task_id)
        finally:
            await self._bus.done(task_id)
            self._tasks.pop(task_id, None)

    async def _run_agent(self, task_id: str, subtask: Any, agent_rows: list[dict[str, str]]) -> AgentResult:
        agent_id = subtask.agent_id
        row = next((r for r in agent_rows if r["id"] == agent_id), None)
        if row:
            row["state"] = "instantiate"
            await self._bus.set_swarm(agent_rows)

        seed = "anon"
        ua = "Ash/disposable"
        if not self._factory or not AgentSession:
            return AgentResult(
                agent_id=agent_id,
                goal=subtask.goal,
                success=False,
                summary="identity or playwright unavailable",
                fingerprint_seed=seed,
            )

        identity: DisposableIdentity = self._factory.next_identity()
        seed = identity.fingerprint_seed
        if row:
            row["fingerprint"] = seed[:8] + "…"
            row["state"] = "operate"
            await self._bus.set_swarm(agent_rows)

        await self._emit(
            {"type": "lifecycle", "agent": agent_id, "phase": "instantiate", "seed": seed[:8]},
            task_id,
        )
        await self._bus.log(f"{_ts()} {agent_id} born seed={seed[:8]}…", task_id=task_id)

        session = AgentSession(identity)
        summary = ""
        success = False
        try:
            await session.start()
            await session.goto(subtask.start_url)
            await self._emit(
                {
                    "type": "web_observed",
                    "agent": agent_id,
                    "fingerprint": seed[:8],
                    "url": subtask.start_url,
                },
                task_id,
            )

            planner = self._get_planner()
            url = subtask.start_url
            for step in range(self._max_steps):
                snap = await session.snapshot()
                action: AgentAction = await planner.next_action(subtask.goal, url, snap)
                await self._emit(
                    {
                        "type": "reasoning",
                        "agent": agent_id,
                        "thought": action.thought,
                        "action": action.action,
                    },
                    task_id,
                )
                await self._bus.log(
                    f"{_ts()} {agent_id} {action.action}: {action.thought[:60]}",
                    level="dim",
                    task_id=task_id,
                )

                if action.action == "done":
                    summary = action.result or subtask.goal
                    success = True
                    break
                if action.action == "failed":
                    summary = action.result or "failed"
                    break
                if action.action == "goto" and action.url:
                    url = action.url
                    await session.goto(url)
                    await self._emit(
                        {
                            "type": "web_observed",
                            "agent": agent_id,
                            "fingerprint": seed[:8],
                            "url": url,
                        },
                        task_id,
                    )
                elif action.action == "click" and action.selector:
                    await session.click(action.selector)
                elif action.action == "extract_text" and action.selector:
                    if session._page:
                        try:
                            summary = await session._page.locator(action.selector).inner_text()
                        except Exception:
                            summary = "could not extract"
                else:
                    summary = snap[:200]
                    success = True
                    break
            else:
                summary = "max steps reached"
        finally:
            await session.close()

        proof = identity_proof(seed, task_id, agent_id)
        if row:
            row["state"] = "destroyed"
            await self._bus.set_swarm(agent_rows)
        await self._emit(
            {"type": "lifecycle", "agent": agent_id, "phase": "destroy", "proof": proof},
            task_id,
        )
        await self._bus.log(f"{_ts()} {agent_id} destroyed proof {proof[:18]}…", level="proof", task_id=task_id)

        return AgentResult(
            agent_id=agent_id,
            goal=subtask.goal,
            success=success,
            summary=summary or subtask.goal,
            fingerprint_seed=seed,
        )


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")
