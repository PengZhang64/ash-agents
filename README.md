# Burner Sentinel

Restock monitor with **disposable identities per check** — alert and checkout assist on the drop.

![CI](https://github.com/TryKosm/burner-agents/actions/workflows/ci.yml/badge.svg)

## What it does

Burner Sentinel watches a product page for restocks. Each check runs under a **fresh fingerprint and IP** so the site never sees one persistent watcher. On restock it fires an alert and can **assist your checkout** (single-unit handoff — not mass-buy).

## Architecture

```
Burner Sentinel (orchestrator + API)
        |
   changedetection.io (Docker, REST API only)
        +-- Playwright fetcher + CloakBrowser / identity rotation
        +-- notifications -> webhook -> buy-assist agent
```

See [`docs/Burner_Sentinel_Spec.md`](docs/Burner_Sentinel_Spec.md) for the full design.

## Hard gates (read before commercial use)

1. **changedetection.io license** — Apache-2.0 core plus separate commercial terms. This repo is a **prototype** until license is clarified for paid use.
2. **Buy-assist only** — MONITOR + ALERT + ASSIST checkout. No autonomous mass-purchase or resell automation.

## Quickstart

```bash
cp .env.example .env
docker compose up -d
# Wait for http://localhost:5000 (changedetection) and http://localhost:8090/health
./scripts/setup-watch.sh
./scripts/flip-stock.sh   # toggle demo product in-stock
open http://localhost:8090/dashboard
```

Configure Discord/Telegram notifications in the changedetection.io UI (`http://localhost:5000`).

## Demo script

1. Dashboard shows watch on demo product (out of stock).
2. `./scripts/flip-stock.sh` — product goes in stock.
3. Alert fires via changedetection notification (configure webhook in UI).
4. Orchestrator receives webhook → buy-assist under new identity → checkout handoff.
5. Identity vanishes; next check is a different stranger.

## Development

```bash
cd services/orchestrator && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=..:../identity:../buy-assist pytest -q
```

## Supply chain

Dependencies are pinned in `requirements.txt` files. Run `pip audit` before production deploys.

## License

MIT — see [LICENSE](LICENSE). changedetection.io is a separate upstream project; we drive it via REST API only.
