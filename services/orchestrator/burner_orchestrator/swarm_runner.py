from __future__ import annotations

import asyncio
import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import httpx

from burner_orchestrator.config import settings
from burner_orchestrator.event_bus import EventBus

try:
    from identity.rotation import DisposableIdentity, IdentityFactory  # type: ignore
except ImportError:
    DisposableIdentity = None  # type: ignore
    IdentityFactory = None  # type: ignore


PRESETS: dict[str, str] = {
    "check_product": "Check the demo product for stock and report status.",
    "watch_drop": "Watch the demo product for a restock drop and report when availability changes.",
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
    """Run disposable agents against the demo product (no Docker required)."""

    def __init__(
        self,
        bus: EventBus,
        *,
        identity_factory: Callable[[], Any] | None = None,
        product_base_url: str | None = None,
    ) -> None:
        self._bus = bus
        self._factory = identity_factory or (IdentityFactory() if IdentityFactory else None)
        self._product_url = (product_base_url or settings.test_product_url).rstrip("/")
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def resolve_intent(self, body: DelegateRequest) -> str:
        if body.preset:
            if body.preset not in PRESETS:
                raise ValueError(f"unknown preset: {body.preset}")
            return PRESETS[body.preset]
        if body.intent and body.intent.strip():
            return body.intent.strip()
        raise ValueError("intent or preset required")

    def start(self, body: DelegateRequest) -> tuple[str, list[dict[str, str]]]:
        count = max(1, min(5, body.agents))
        intent = self.resolve_intent(body)
        task_id = uuid.uuid4().hex[:12]
        agent_rows = [{"id": f"agent-{i:02d}", "state": "idle"} for i in range(1, count + 1)]
        self._tasks[task_id] = asyncio.create_task(self._run(task_id, intent, agent_rows, body.preset))
        return task_id, agent_rows

    async def _run(
        self,
        task_id: str,
        intent: str,
        agent_rows: list[dict[str, str]],
        preset: str | None,
    ) -> None:
        try:
            await self._bus.set_swarm(agent_rows)
            await self._bus.log(f"{_ts()} task accepted", task_id=task_id)
            await self._bus.log(f"{_ts()} intent: {intent}", level="dim", task_id=task_id)
            await self._bus.log(
                f"{_ts()} orchestration private — {len(agent_rows)} agents fan-out",
                level="dim",
                task_id=task_id,
            )

            for row in agent_rows:
                await self._run_agent(task_id, row, agent_rows, preset)

            await self._bus.log(
                f"{_ts()} swarm complete — the site saw strangers",
                task_id=task_id,
            )
            idle = [{"id": a["id"], "state": "idle"} for a in agent_rows]
            await self._bus.set_swarm(idle)
        except Exception as exc:  # noqa: BLE001 — demo must surface errors in log
            await self._bus.log(f"{_ts()} error: {exc}", task_id=task_id)
        finally:
            await self._bus.done(task_id)
            self._tasks.pop(task_id, None)

    async def _run_agent(
        self,
        task_id: str,
        row: dict[str, str],
        agent_rows: list[dict[str, str]],
        preset: str | None,
    ) -> None:
        agent_id = row["id"]
        row["state"] = "spawning"
        await self._bus.set_swarm(agent_rows)
        await self._bus.log(f"{_ts()} {agent_id} instantiating identity…", task_id=task_id)

        seed = "anon"
        ua = "BurnerAgents/disposable"
        proxy: str | None = None
        if self._factory:
            identity: DisposableIdentity = self._factory.next_identity()
            seed = identity.fingerprint_seed
            ua = identity.user_agent
            proxy = identity.proxy_url

        row["state"] = "running"
        await self._bus.set_swarm(agent_rows)
        proxy_label = proxy or "none"
        await self._bus.log(
            f"{_ts()} {agent_id} born  seed={seed[:8]}… proxy={proxy_label}",
            task_id=task_id,
        )

        stock = await self._fetch_stock(ua)
        status = "in stock" if stock.get("in_stock") else "out of stock"
        title = stock.get("title", "demo product")
        await self._bus.log(
            f"{_ts()} {agent_id} fetch {self._product_url}/api/stock → {title}: {status}",
            task_id=task_id,
        )

        if preset == "watch_drop":
            await self._bus.log(
                f"{_ts()} {agent_id} watch_drop: monitoring delegated (Sentinel preset)",
                level="dim",
                task_id=task_id,
            )

        proof = identity_proof(seed, task_id, agent_id)
        row["state"] = "destroyed"
        await self._bus.set_swarm(agent_rows)
        await self._bus.log(f"{_ts()} {agent_id} identity destroyed", task_id=task_id)
        await self._bus.log(f"{_ts()} proof {proof}", level="proof", task_id=task_id)
        await asyncio.sleep(0.15)

    async def _fetch_stock(self, user_agent: str) -> dict[str, Any]:
        url = f"{self._product_url}/api/stock"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers={"User-Agent": user_agent})
            response.raise_for_status()
            return response.json()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")
