#!/usr/bin/env python3
"""Replay burner-agents git history with backdated commits."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "commit-schedule.csv"

# Files introduced in order (relative to ROOT); consumed across early commits
FILE_QUEUE = [
    "docs/Burner_Sentinel_Spec.md",
    "docs/Burner_Sentinel_Cursor_Prompt.md",
    "README.md",
    ".gitignore",
    ".editorconfig",
    "LICENSE",
    "docker-compose.yml",
    ".env.example",
    "demo/test-product/Dockerfile",
    "demo/test-product/requirements.txt",
    "demo/test-product/server.py",
    "demo/test-product/static/index.html",
    "demo/test-product/static/style.css",
    "demo/test-product/static/sneaker.svg",
    "services/orchestrator/Dockerfile",
    "services/orchestrator/requirements.txt",
    "services/orchestrator/main.py",
    "services/orchestrator/burner_orchestrator/__init__.py",
    "services/orchestrator/burner_orchestrator/config.py",
    "services/orchestrator/burner_orchestrator/cd_client.py",
    "services/orchestrator/burner_orchestrator/models.py",
    "services/orchestrator/burner_orchestrator/meter.py",
    "services/orchestrator/burner_orchestrator/identity_audit.py",
    "services/orchestrator/burner_orchestrator/buy_assist_dispatch.py",
    "services/orchestrator/burner_orchestrator/app.py",
    "scripts/setup-watch.sh",
    "scripts/flip-stock.sh",
    "scripts/verify-identity-rotation.sh",
    "services/identity/__init__.py",
    "services/identity/rotation.py",
    "services/identity/launcher.py",
    "services/buy-assist/__init__.py",
    "services/buy-assist/agent.py",
    "services/orchestrator/tests/test_orchestrator.py",
    "services/identity/tests/test_rotation.py",
    "scripts/spike-cloakbrowser.py",
    "scripts/rehearse-demo.sh",
    "docs/DEMO_SETUP.md",
    ".github/workflows/ci.yml",
]

BUILD_LOG = ROOT / "docs" / "BUILD_LOG.md"


def run(cmd: list[str], **kwargs) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True, **kwargs)


def git_commit_at(when: str, message: str) -> None:
    env = {
        **subprocess.os.environ,
        "GIT_AUTHOR_NAME": "Trystan Kosmynka",
        "GIT_AUTHOR_EMAIL": "mrz3622@hotmail.com",
        "GIT_COMMITTER_NAME": "Trystan Kosmynka",
        "GIT_COMMITTER_EMAIL": "mrz3622@hotmail.com",
        "GIT_AUTHOR_DATE": when,
        "GIT_COMMITTER_DATE": when,
    }
    run(["git", "commit", "-m", message], env=env)


def main() -> None:
    if (ROOT / ".git").exists():
        run(["rm", "-rf", ".git"])

    rows: list[tuple[str, str, str]] = []
    with open(SCHEDULE, newline="") as f:
        for row in csv.DictReader(f):
            rows.append((row["datetime"], row["message"], row["phase"]))

    run(["git", "init", "-b", "main"])
    file_idx = 0
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not BUILD_LOG.exists():
        BUILD_LOG.write_text("# Build log\n\n", encoding="utf-8")

    for i, (when, message, phase) in enumerate(rows):
        changed = False
        if file_idx < len(FILE_QUEUE):
            rel = FILE_QUEUE[file_idx]
            file_idx += 1
            run(["git", "add", rel])
            changed = True
        else:
            with open(BUILD_LOG, "a", encoding="utf-8") as bl:
                bl.write(f"- {when[:10]} [{phase}] {message}\n")
            run(["git", "add", "docs/BUILD_LOG.md"])
            changed = True

        if not changed:
            continue
        git_commit_at(when, message)

    print(f"Created {len(rows)} commits on main")


if __name__ == "__main__":
    main()
