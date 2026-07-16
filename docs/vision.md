# Vision

Ash is described in the [whitepaper](ash_whitepaper.pdf). You delegate intent. The web sees strangers, not you.

## The model

```
     YOU                THE WALL              THE WEB
  (delegate)      (orchestration private)   (strangers only)
```

## Three layers (shipped in demo)

| Layer | Whitepaper | Demo implementation |
|-------|------------|---------------------|
| Isolation | Separable browser context per agent | Playwright context per agent + identity rotation |
| Reasoning | NL → plan → perceive → act | **LLM required** (`OPENAI_API_KEY`) |
| Orchestration | Decompose, fan-out, reconcile privately | `POST /api/delegate` + console panels |

## Run the demo

```bash
cp config/.env.example .env
# set OPENAI_API_KEY=sk-...
make -f scripts/Makefile demo
```

CI and smoke use `ASH_DEMO_MOCK=1` (no API key). Production demos need a real key.

## Roadmap

- CloakBrowser integration
- Arbitrary target URLs with guardrails
- On-chain metering
