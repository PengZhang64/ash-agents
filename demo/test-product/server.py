"""Demo test product page with in-stock / out-of-stock toggle."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Burner Demo Product")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

_state = {"in_stock": False, "title": "Burner Agents Demo Sneaker"}


class StockState(BaseModel):
    in_stock: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stock")
def get_stock() -> dict[str, bool | str]:
    return {"in_stock": _state["in_stock"], "title": _state["title"]}


@app.get("/api/page-summary")
def page_summary() -> dict[str, str | bool]:
    status = "In Stock" if _state["in_stock"] else "Out of Stock"
    return {
        "title": _state["title"],
        "stock_status": status,
        "in_stock": _state["in_stock"],
        "sku": "BURNER-DEMO-001",
        "hint": "Demo storefront for Burner swarm tasks.",
    }


@app.post("/admin/toggle")
def toggle_stock() -> dict[str, bool]:
    _state["in_stock"] = not _state["in_stock"]
    return {"in_stock": _state["in_stock"]}


@app.post("/admin/stock")
def set_stock(body: StockState) -> dict[str, bool]:
    _state["in_stock"] = body.in_stock
    return {"in_stock": _state["in_stock"]}


@app.get("/", response_class=HTMLResponse)
def product_page() -> str:
    status = "In Stock" if _state["in_stock"] else "Out of Stock"
    badge_class = "in-stock" if _state["in_stock"] else "out-of-stock"
    html_path = STATIC / "index.html"
    template = html_path.read_text(encoding="utf-8")
    return (
        template.replace("{{TITLE}}", _state["title"])
        .replace("{{STATUS}}", status)
        .replace("{{BADGE_CLASS}}", badge_class)
        .replace("{{STOCK_FLAG}}", "true" if _state["in_stock"] else "false")
    )
