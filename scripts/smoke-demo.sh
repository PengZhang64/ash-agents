#!/usr/bin/env bash
set -euo pipefail

ORCH="${ORCH_URL:-http://127.0.0.1:8090}"
PRODUCT="${PRODUCT_URL:-http://127.0.0.1:8088}"

echo "==> health"
curl -sf "$ORCH/health" | grep -q ok
curl -sf "$PRODUCT/health" | grep -q ok

echo "==> delegate preset"
RESP=$(curl -sf -X POST "$ORCH/api/delegate" \
  -H "Content-Type: application/json" \
  -d '{"preset":"check_product","agents":2}')
echo "$RESP" | grep -q task_id

echo "==> console"
curl -sf "$ORCH/" | grep -q "BURNER AGENTS"

echo "==> smoke ok"
