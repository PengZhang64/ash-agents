# Vision

Burner Agents is the platform described in the [whitepaper](burner_whitepaper.pdf). You delegate work to a swarm. The web sees strangers, not you.

## The problem

Every normal interaction ties back to one profile: IP, fingerprint, cookies, behavior. Sites build a persistent picture of you. Automation and monitoring from a single identity get rate-limited, blocked, or linked across sessions.

## The model

```
     YOU                THE WALL              THE WEB
  (delegate)      (orchestration stays        (sees only
                   private)                    strangers)
      |                    |                        ^
      v                    v                        |
  intent in -------->  swarm of agents -------->  requests
                       each disposable
                       destroyed after task
```

You never touch the site directly. Coordination stays behind the wall. Multiplicity is visible to the web, not to the operator.

## Three layers

| Layer | Idea | In this repo |
|-------|------|----------------|
| **Isolation** | Disposable browser context per task | [`services/identity/`](../services/identity/) rotation (seed, user agent, proxy) |
| **Reasoning** | Natural language becomes actions on the live web | Console intent + presets; scripted runner today (LLM on the roadmap) |
| **Orchestration** | Fan-out, private coordination | [`services/orchestrator/`](../services/orchestrator/) delegate API, SSE log, swarm state |

## What you can run today

```bash
make -f scripts/Makefile demo
open http://127.0.0.1:8090/
```

- Launch a swarm from the console
- Watch agents instantiate, fetch the demo product, and destroy with proof hashes
- Optional **restock sentinel** stack via Docker (see [burner-sentinel-spec.md](burner-sentinel-spec.md))

## Roadmap

- LLM-backed intent parsing and multi-step plans
- CloakBrowser / Playwright isolation on every agent run
- On-chain $BURNER metering (stub meter exists today)
- More first-party applications on the same orchestration core
