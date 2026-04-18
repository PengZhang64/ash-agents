#!/usr/bin/env bash
# Flip demo product to in-stock (triggers restock detection when watch is configured).
set -euo pipefail
PRODUCT="${TEST_PRODUCT_URL:-http://localhost:8088}"
curl -sf -X POST "$PRODUCT/admin/toggle" | python3 -m json.tool
