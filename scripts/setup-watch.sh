#!/usr/bin/env bash
# Register a restock watch on the demo product via orchestrator + changedetection API.
set -euo pipefail
ORCH="${ORCHESTRATOR_URL:-http://localhost:8090}"
PRODUCT="${TEST_PRODUCT_URL:-http://localhost:8088}"
curl -sf -X POST "$ORCH/api/watches" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$PRODUCT/\", \"title\": \"Burner demo sneaker\"}"
