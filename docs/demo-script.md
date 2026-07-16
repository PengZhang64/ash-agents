# Ash — whitepaper demo script (90s)

## Before stage

```bash
cp config/.env.example .env
# OPENAI_API_KEY required
make -f scripts/Makefile demo
```

Open http://127.0.0.1:8090/

## Narrative (Fig 1)

| Time | Say | Point at |
|------|-----|----------|
| 0:00 | "You never touch the web. You delegate." | **YOU** + intent |
| 0:15 | "Orchestration stays private. Sites never see it." | **ORCHESTRATION · PRIVATE** |
| 0:25 | "Intent stops at the wall." | **THE WALL** |
| 0:35 | "The swarm is disposable strangers." | **SWARM** (fingerprints, lifecycle) |
| 0:50 | "The web only sees unrelated participants." | **THE WEB** feed |
| 1:05 | "Results reconcile on your side." | **RESULT** |
| 1:20 | "Each identity is destroyed. Proof on erase." | RUN.LOG proof lines |

## Action

1. Click **Check demo storefront** or enter intent.
2. **DELEGATE** with 3 agents.
3. Wait for **RESULT** (LLM reconcile).

## Troubleshooting

- 503: missing `OPENAI_API_KEY` in `.env`
- Playwright: `playwright install chromium` in orchestrator venv
- Offline check: `ASH_DEMO_MOCK=1 make -f scripts/Makefile smoke`
