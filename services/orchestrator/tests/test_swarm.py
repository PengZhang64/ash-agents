from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from ash_orchestrator.app import create_app
from ash_orchestrator.swarm_runner import identity_proof, PRESETS


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASH_DEMO_MOCK", "1")


def test_identity_proof_format() -> None:
    proof = identity_proof("abc123", "task1", "agent-01")
    assert proof.startswith("0x")
    assert len(proof) == 66


def test_presets_defined() -> None:
    assert "check_storefront" in PRESETS


def test_delegate_requires_intent_or_preset() -> None:
    client = TestClient(create_app())
    r = client.post("/api/delegate", json={"agents": 2})
    assert r.status_code == 400


def test_delegate_with_preset_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_start(self, body):  # noqa: ANN001
        return "taskmock01", [{"id": "agent-01", "state": "idle", "fingerprint": ""}]

    monkeypatch.setattr(
        "ash_orchestrator.swarm_runner.SwarmRunner.start",
        fake_start,
    )
    client = TestClient(create_app())
    r = client.post("/api/delegate", json={"preset": "check_storefront", "agents": 1})
    assert r.status_code == 200
    data = r.json()
    assert "task_id" in data


def test_delegate_requires_api_key_without_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ASH_DEMO_MOCK", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(create_app())
    r = client.post("/api/delegate", json={"preset": "check_storefront", "agents": 1})
    assert r.status_code == 503


def test_console_root() -> None:
    client = TestClient(create_app())
    r = client.get("/")
    assert r.status_code == 200
    assert "ASH" in r.text
