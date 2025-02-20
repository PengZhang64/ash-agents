from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from burner_orchestrator.app import create_app
from burner_orchestrator.swarm_runner import identity_proof, PRESETS


def test_identity_proof_format() -> None:
    proof = identity_proof("abc123", "task1", "agent-01")
    assert proof.startswith("0x")
    assert len(proof) == 66


def test_presets_defined() -> None:
    assert "check_product" in PRESETS
    assert "watch_drop" in PRESETS


def test_delegate_requires_intent_or_preset() -> None:
    client = TestClient(create_app())
    r = client.post("/api/delegate", json={"agents": 2})
    assert r.status_code == 400


def test_delegate_with_preset() -> None:
    client = TestClient(create_app())
    r = client.post("/api/delegate", json={"preset": "check_product", "agents": 1})
    assert r.status_code == 200
    data = r.json()
    assert "task_id" in data
    assert len(data["agents"]) == 1
    assert data["agents"][0]["id"] == "agent-01"


def test_console_root() -> None:
    client = TestClient(create_app())
    r = client.get("/")
    assert r.status_code == 200
    assert "BURNER AGENTS" in r.text


def test_dashboard_redirects() -> None:
    client = TestClient(create_app())
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/"
