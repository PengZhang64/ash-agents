#!/usr/bin/env bash
set -euo pipefail

ORCH="${ORCH_URL:-http://127.0.0.1:8090}"
PRODUCT="${PRODUCT_URL:-http://127.0.0.1:8088}"
export ASH_DEMO_MOCK="${ASH_DEMO_MOCK:-1}"

echo "==> health"
curl -sf "$ORCH/health" | grep -q ok
curl -sf "$PRODUCT/health" | grep -q ok

echo "==> page-summary"
curl -sf "$PRODUCT/api/page-summary" | grep -q stock_status

echo "==> delegate preset"
RESP=$(curl -sf -X POST "$ORCH/api/delegate" \
  -H "Content-Type: application/json" \
  -d '{"preset":"check_storefront","agents":1}')
echo "$RESP" | grep -q task_id
TASK_ID=$(python3 -c "import json,sys; print(json.load(sys.stdin)['task_id'])" <<<"$RESP")

echo "==> wait for task"
for i in $(seq 1 30); do
  if curl -sf "$ORCH/api/swarm" | grep -q destroyed; then
    break
  fi
  sleep 1
done

echo "==> console"
curl -sf "$ORCH/" | grep -q ASH

echo "==> smoke ok (task $TASK_ID)"
