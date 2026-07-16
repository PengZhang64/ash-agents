from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse

from ash_orchestrator.buy_assist_dispatch import BuyAssistDispatcher
from ash_orchestrator.cd_client import ChangedetectionClient
from ash_orchestrator.config import settings
from ash_orchestrator.delegate_models import DelegateBody, DelegateResponse
from ash_orchestrator.event_bus import EventBus
from ash_orchestrator.identity_audit import IdentityAuditLog
from ash_orchestrator.meter import AshMeter
from ash_orchestrator.models import WatchRegistration, parse_changedetection_notification
from ash_orchestrator.swarm_runner import DelegateRequest, SwarmRunner
from fastapi.staticfiles import StaticFiles

try:
    from identity.rotation import IdentityFactory  # type: ignore
except ImportError:
    IdentityFactory = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[3]
CONSOLE_DIR = REPO_ROOT / "demo" / "console"
DOCS_DIR = REPO_ROOT / "docs"


def create_app() -> FastAPI:
    app = FastAPI(title="Ash", version="0.3.0")
    meter = AshMeter(stub_balance=settings.ash_meter_stub_balance)
    audit = IdentityAuditLog()
    dispatcher = BuyAssistDispatcher()
    cd = ChangedetectionClient()
    bus = EventBus()
    swarm = SwarmRunner(bus)

    if CONSOLE_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=CONSOLE_DIR), name="console_static")

    if DOCS_DIR.is_dir():
        app.mount("/docs", StaticFiles(directory=DOCS_DIR), name="docs_static")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "ash-agents"}

    @app.get("/")
    def console() -> FileResponse:
        index = CONSOLE_DIR / "index.html"
        if not index.is_file():
            raise HTTPException(status_code=404, detail="console not found")
        return FileResponse(index)

    @app.get("/dashboard")
    def dashboard_redirect() -> RedirectResponse:
        return RedirectResponse(url="/", status_code=302)

    @app.get("/api/status")
    def status() -> dict:
        return {
            "product": "ash-agents",
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

    @app.get("/api/swarm")
    def get_swarm() -> dict:
        return {"agents": bus.snapshot_swarm()}

    @app.post("/api/delegate", response_model=DelegateResponse)
    async def delegate(body: DelegateBody) -> DelegateResponse:
        try:
            from reasoning.planner import PlannerError  # type: ignore
        except ImportError:
            PlannerError = Exception  # type: ignore

        try:
            req = DelegateRequest(
                intent=body.intent,
                preset=body.preset,
                agents=body.agents,
            )
            intent = swarm.resolve_intent(req)
            task_id, agents = swarm.start(req)
            meter.record_watch()
            return DelegateResponse(task_id=task_id, agents=agents, intent=intent)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except PlannerError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/api/events/stream")
    async def event_stream(task_id: str | None = None) -> StreamingResponse:
        queue = bus.subscribe()

        async def generate() -> AsyncIterator[str]:
            try:
                while True:
                    event = await queue.get()
                    if task_id:
                        evt_task = event.get("task_id")
                        if evt_task and evt_task != task_id:
                            continue
                    yield EventBus.format_sse(event)
                    if event.get("type") == "done" and (
                        not task_id or event.get("task_id") == task_id
                    ):
                        break
            finally:
                bus.unsubscribe(queue)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

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
        secret = request.headers.get("x-ash-secret", "")
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

    @app.get("/legacy/dashboard", response_class=HTMLResponse)
    def legacy_dashboard() -> str:
        m = meter.snapshot()
        ids = audit.recent(5)
        rows = "".join(
            f"<li><code>{i['check_index']}</code> seed={i['fingerprint_seed'][:8]}… "
            f"proxy={i['proxy_url'] or 'none'}</li>"
            for i in ids
        )
        return f"""<!DOCTYPE html>
<html><head><title>Ash — legacy meter</title>
<style>body{{font-family:monospace;background:#000;color:#fff;padding:2rem}}
a{{color:#fff}}</style></head><body>
<h1>Legacy meter</h1>
<p><a href="/">← Ash Agents console</a></p>
<p>Balance: {m['stub_balance']} · Watches: {m['watches']} · Buy-assists: {m['buy_assists']}</p>
<ul>{rows or '<li>No checks yet</li>'}</ul>
</body></html>"""

    return app
