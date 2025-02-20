# Burner Sentinel

Catch restocks the instant they drop, checking as a different identity every time so the site never sees one watcher to block.

![CI](https://github.com/TryKosm/burner-agents/actions/workflows/ci.yml/badge.svg)

## Why

Ordinary monitors poll from one IP and one browser fingerprint. Stores rate-limit or block that pattern, and you miss the drop. Burner Sentinel rotates a fresh disposable identity on every check and can assist your checkout when stock returns.

## Capabilities

| Capability | What it does |
|------------|--------------|
| Disposable identity per check | New fingerprint and proxy each poll so the site never links checks to one watcher |
| Restock and price detection | Self-hosted changedetection.io watches product pages and diffs stock or price |
| Instant alerts | Discord, Telegram, or webhook when a watch fires |
| Checkout assist | Single-unit add-to-cart handoff under a clean identity, not mass-buy automation |
| Usage metering | Stub $BURNER meter counts watches and buy-assists (chain later) |

## Quickstart

```bash
cp .env.example .env
docker compose up -d
# Wait for http://localhost:5000 and http://localhost:8090/health
./scripts/setup-watch.sh
./scripts/flip-stock.sh
open http://localhost:8090/
```

Console-only demo (no Docker):

```bash
make demo
open http://127.0.0.1:8090/
```

## How it works

```
burner-agents/
├── services/
│   ├── orchestrator/       # restock webhook, swarm console, buy-assist dispatch
│   ├── identity/           # fresh fingerprint + proxy per check, destroyed after
│   └── buy-assist/         # checkout-assist agent under a clean identity
├── demo/
│   ├── test-product/       # local sneaker page with in-stock toggle for demos
│   └── console/            # Burner Agents web UI (launch swarm, live log)
├── scripts/                # setup-watch, flip-stock, smoke, rehearsal
├── docs/                   # spec, demo script, whitepaper
└── docker-compose.yml      # changedetection.io engine + our services
```

- You register a watch on a product URL. changedetection.io polls on a schedule.
- Each poll can run through the identity layer with a new fingerprint and proxy.
- On restock, changedetection notifies the orchestrator via webhook.
- The orchestrator dispatches buy-assist under another disposable identity, then tears it down.

## Demo

**Sentinel (Docker stack)**

1. Demo product starts out of stock.
2. `./scripts/flip-stock.sh` toggles in stock.
3. changedetection fires an alert to your notification channel or webhook.
4. Orchestrator runs buy-assist and reports cart handoff.
5. Identity is destroyed. The next check is a different stranger.

**Burner Agents console**

1. `make demo` starts the console and demo product locally.
2. Open http://127.0.0.1:8090/, choose **Check demo product** or enter a task.
3. Click **LAUNCH SWARM** and watch agents spawn, fetch stock, and vanish with proof hashes.

Step-by-step presenter notes: [`docs/demo-script.md`](docs/demo-script.md). Full design: [`docs/burner-sentinel-spec.md`](docs/burner-sentinel-spec.md). Thesis: [`docs/burner_whitepaper.pdf`](docs/burner_whitepaper.pdf).

## Development

```bash
cd services/orchestrator && python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=.:..:../identity:../buy-assist pytest -q
```

From repo root (matches CI):

```bash
pip install -r services/orchestrator/requirements.txt pytest
PYTHONPATH=services:services/orchestrator:services/identity:services/buy-assist \
  pytest services/orchestrator/tests services/identity/tests -q
```

## Status and licensing

**Prototype.** changedetection.io has Apache-2.0 core plus separate commercial terms. Clarify license before paid or production use.

**Buy-assist only.** This stack monitors, alerts, and assists the user's own checkout. It does not run autonomous mass-purchase or resell automation.

## License

MIT. See [LICENSE](LICENSE). changedetection.io is a separate upstream project. This repo drives it via REST API only.
