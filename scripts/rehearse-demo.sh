#!/usr/bin/env bash
# Rehearse flip -> alert -> buy-assist (requires stack running + watch configured).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/scripts/flip-stock.sh"
echo "Waiting for changedetection check cycle..."
sleep 15
curl -sf -X POST "${ORCHESTRATOR_URL:-http://localhost:8090}/api/webhooks/changedetection" \
  -H "Content-Type: application/json" \
  -H "x-ash-secret: ${ORCHESTRATOR_WEBHOOK_SECRET:-dev-secret-change-me}" \
  -d '{"uuid":"demo","watch_url":"http://test-product:8088/","title":"Demo restock","message":"Back in stock"}' \
  | python3 -m json.tool
