# Contributing

Thanks for helping improve Burner Agents.

## Local setup

```bash
git clone https://github.com/NotPBShaw/burner-agents.git
cd burner-agents
make -f scripts/Makefile demo
```

Console: http://127.0.0.1:8090/

## Tests

```bash
cd services/orchestrator && python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=.:..:../identity:../buy-assist pytest -q
```

## Pull requests

- Keep changes focused. Presentation and docs PRs should not change runtime behavior unless agreed.
- Ensure `pytest` passes.
- No em dashes in README or user-facing copy.
- Platform name is **Burner Agents**. **Restock sentinel** is one application on the platform.
