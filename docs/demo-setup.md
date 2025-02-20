## Step 1 — Demo backbone

1. `docker compose -f deploy/docker-compose.yml up -d`
2. Open changedetection.io at http://localhost:5000
3. `./scripts/setup-watch.sh`
4. Configure notification webhook (Discord/Telegram) in changedetection UI pointing to orchestrator if desired
5. `./scripts/flip-stock.sh` and confirm detection in changedetection history

## Step 2 — Identity rotation

1. Set `PROXY_POOL` in `.env`
2. `./scripts/verify-identity-rotation.sh`
3. Confirm `consecutive_differ: true` in orchestrator status

## Step 3 — Buy-assist

1. `./scripts/rehearse-demo.sh` simulates restock webhook → buy-assist
