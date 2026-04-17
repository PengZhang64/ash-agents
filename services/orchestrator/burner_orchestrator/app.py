from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

from burner_orchestrator.buy_assist_dispatch import BuyAssistDispatcher
from burner_orchestrator.cd_client import ChangedetectionClient
from burner_orchestrator.config import settings
from burner_orchestrator.identity_audit import IdentityAuditLog
from burner_orchestrator.meter import BurnerMeter
from burner_orchestrator.models import WatchRegistration, parse_changedetection_notification

try:
    from identity.rotation import IdentityFactory  # type: ignore
except ImportError:
    IdentityFactory = None  # type: ignore


def create_app() -> FastAPI:
    app = FastAPI(title="Burner Sentinel Orchestrator", version="0.1.0")
    meter = BurnerMeter(stub_balance=settings.burner_meter_stub_balance)
    audit = IdentityAuditLog()
    dispatcher = BuyAssistDispatcher()
    cd = ChangedetectionClient()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "burner-orchestrator"}

    @app.get("/api/status")
    def status() -> dict:
        return {
            "changedetection_url": settings.changedetection_url,
            "test_product_url": settings.test_product_url,
            "cloakbrowser_enabled": settings.cloakbrowser_enabled,
            "meter": meter.snapshot(),
            "recent_identities": audit.recent(5),
            "identities_differ": audit.consecutive_differ(),
        }

    @app.get("/api/meter")
    def get_meter() -> dict[str, int]:
        return meter.snapshot()

    @app.get("/api/identities/recent")
    def recent_identities() -> dict:
        return {"identities": audit.recent(10), "consecutive_differ": audit.consecutive_differ()}

    @app.post("/api/watches")
    def register_watch(body: WatchRegistration) -> dict:
        meter.record_watch()
        proxy = body.proxy
        if IdentityFactory and not proxy:
            identity = IdentityFactory().next_identity()
            audit.record(identity.fingerprint_seed, identity.proxy_url, identity.user_agent)
            proxy = identity.proxy_url
        result = cd.create_watch(body.url, title=body.title, tag=body.tag, proxy=proxy)
        return {"watch": result, "meter": meter.snapshot()}

    @app.post("/api/webhooks/changedetection")
    async def changedetection_webhook(request: Request) -> dict:
        secret = request.headers.get("x-burner-secret", "")
        if secret != settings.orchestrator_webhook_secret:
            raise HTTPException(status_code=401, detail="invalid webhook secret")
        payload = await request.json()
        alert = parse_changedetection_notification(payload)
        meter.record_buy_assist()
        result = dispatcher.dispatch(alert)
        return {"alert": alert.model_dump(), "assist": result, "meter": meter.snapshot()}

    @app.get("/api/assist/history")
    def assist_history() -> dict:
        return {"runs": dispatcher.history()}

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard() -> str:
        m = meter.snapshot()
        ids = audit.recent(5)
        rows = "".join(
            f"<li><code>{i['check_index']}</code> seed={i['fingerprint_seed'][:8]}… proxy={i['proxy_url'] or 'none'}</li>"
            for i in ids
        )
        return f"""<!DOCTYPE html>
<html><head><title>Burner Sentinel</title>
<style>body{{font-family:system-ui;background:#0f1115;color:#e8eaed;padding:2rem}}
.card{{background:#1a1d24;border-radius:12px;padding:1rem;margin:1rem 0}}
a{{color:#818cf8}}</style></head><body>
<h1>Burner Sentinel</h1>
<p>Thin dashboard — watches live in <a href="{settings.changedetection_url}" target="_blank">changedetection.io</a>.</p>
<div class="card"><h2>$BURNER meter (stub)</h2>
<p>Balance: {m['stub_balance']} · Watches: {m['watches']} · Buy-assists: {m['buy_assists']}</p></div>
<div class="card"><h2>Recent disposable identities</h2><ul>{rows or '<li>No checks yet</li>'}</ul></div>
</body></html>"""

    return app
