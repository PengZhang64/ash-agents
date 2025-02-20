from __future__ import annotations

import asyncio

from reasoning.models import AgentResult
from reasoning.planner import MockBurnerPlanner


def test_mock_decompose() -> None:
    planner = MockBurnerPlanner()
    plan = asyncio.run(planner.decompose("check stock", 2, "http://localhost:8088"))
    assert len(plan.subtasks) == 2
    assert plan.subtasks[0].agent_id == "agent-01"


def test_mock_reconcile() -> None:
    planner = MockBurnerPlanner()
    results = [
        AgentResult(
            agent_id="agent-01",
            goal="g",
            success=True,
            summary="in stock",
            fingerprint_seed="abc",
        )
    ]
    out = asyncio.run(planner.reconcile("check stock", results))
    assert "check stock" in out.summary
