#!/usr/bin/env bash
# Prove consecutive checks use different identity seeds (via orchestrator audit log).
set -euo pipefail
ORCH="${ORCHESTRATOR_URL:-http://localhost:8090}"
for _ in 1 2; do
  curl -sf -X POST "$ORCH/api/watches" \
    -H "Content-Type: application/json" \
    -d '{"url": "http://example.com/product", "title": "rotation test"}' >/dev/null
done
curl -sf "$ORCH/api/identities/recent" | python3 -m json.tool
curl -sf "$ORCH/api/status" | python3 -c "import sys,json; d=json.load(sys.stdin); print('consecutive_differ:', d.get('identities_differ'))"
