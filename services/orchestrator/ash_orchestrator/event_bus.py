from __future__ import annotations

import asyncio
import json
from typing import Any


class EventBus:
    """In-memory pub/sub for SSE log and swarm state updates."""

    def __init__(self) -> None:
        self._queues: list[asyncio.Queue[dict[str, Any]]] = []
        self._swarm_agents: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    def snapshot_swarm(self) -> list[dict[str, Any]]:
        return list(self._swarm_agents)

    async def set_swarm(self, agents: list[dict[str, Any]]) -> None:
        async with self._lock:
            self._swarm_agents = list(agents)
        await self._broadcast({"type": "swarm", "agents": self._swarm_agents})

    async def log(self, message: str, *, level: str = "info", task_id: str | None = None) -> None:
        payload: dict[str, Any] = {"type": "log", "message": message, "level": level}
        if task_id:
            payload["task_id"] = task_id
        await self._broadcast(payload)

    async def done(self, task_id: str) -> None:
        await self._broadcast({"type": "done", "task_id": task_id, "message": "complete"})

    async def _broadcast(self, event: dict[str, Any]) -> None:
        for queue in list(self._queues):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
        self._queues.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        if queue in self._queues:
            self._queues.remove(queue)

    @staticmethod
    def format_sse(event: dict[str, Any]) -> str:
        return f"data: {json.dumps(event)}\n\n"
