.PHONY: demo demo-stop smoke install-orchestrator install-product

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
PYTHON ?= python3.11
ORCH_DIR := $(ROOT)/services/orchestrator
PRODUCT_DIR := $(ROOT)/demo/test-product
ORCH_PORT := 8090
PRODUCT_PORT := 8088

install-orchestrator:
	cd $(ORCH_DIR) && $(PYTHON) -m venv .venv && . .venv/bin/activate && pip install -q -r requirements.txt

install-product:
	cd $(PRODUCT_DIR) && $(PYTHON) -m venv .venv && . .venv/bin/activate && pip install -q -r requirements.txt 2>/dev/null || \
		(. .venv/bin/activate && pip install -q fastapi uvicorn)

demo: install-orchestrator install-product
	@echo "Starting demo product on :$(PRODUCT_PORT) and Burner Agents on :$(ORCH_PORT)…"
	@cd $(PRODUCT_DIR) && . .venv/bin/activate && \
		uvicorn server:app --host 127.0.0.1 --port $(PRODUCT_PORT) & echo $$! > /tmp/burner-product.pid
	@sleep 1
	@cd $(ORCH_DIR) && . .venv/bin/activate && \
		PYTHONPATH=..:../identity:../buy-assist \
		TEST_PRODUCT_URL=http://127.0.0.1:$(PRODUCT_PORT) \
		uvicorn main:app --host 127.0.0.1 --port $(ORCH_PORT) & echo $$! > /tmp/burner-orch.pid
	@sleep 2
	@echo ""
	@echo "  Burner Agents console: http://127.0.0.1:$(ORCH_PORT)/"
	@echo "  Demo product:          http://127.0.0.1:$(PRODUCT_PORT)/"
	@echo ""
	@echo "Run: make -f scripts/Makefile smoke"
	@command -v open >/dev/null && open "http://127.0.0.1:$(ORCH_PORT)/" || true

demo-stop:
	@-kill $$(cat /tmp/burner-product.pid 2>/dev/null) 2>/dev/null; rm -f /tmp/burner-product.pid
	@-kill $$(cat /tmp/burner-orch.pid 2>/dev/null) 2>/dev/null; rm -f /tmp/burner-orch.pid
	@echo "Demo stopped."

smoke:
	@$(ROOT)/scripts/smoke-demo.sh
