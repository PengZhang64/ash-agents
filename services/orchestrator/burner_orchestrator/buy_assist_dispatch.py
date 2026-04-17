from __future__ import annotations

from typing import Any

from burner_orchestrator.config import settings
from burner_orchestrator.models import RestockAlert


class BuyAssistDispatcher:
    """Dispatch assist-only checkout on restock — never mass-buy."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def dispatch(self, alert: RestockAlert) -> dict[str, Any]:
        try:
            from buy_assist.agent import run_buy_assist  # type: ignore
        except ImportError:
            run_buy_assist = None

        if run_buy_assist is None:
            result = {
                "status": "simulated",
                "message": "Buy-assist agent not loaded; simulated handoff at checkout.",
                "watch_url": alert.watch_url,
                "checkout_handoff": True,
            }
        else:
            result = run_buy_assist(alert.watch_url, max_quantity=1)

        self._history.append({"alert": alert.model_dump(), "result": result})
        return result

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    @staticmethod
    def reject_mass_buy(quantity: int) -> None:
        if quantity > 1:
            raise ValueError("Mass-buy rejected: assist-only policy allows quantity=1")
