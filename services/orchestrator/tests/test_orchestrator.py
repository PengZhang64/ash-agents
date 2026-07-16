from __future__ import annotations

import pytest

from ash_orchestrator.models import parse_changedetection_notification
from ash_orchestrator.meter import AshMeter
from ash_orchestrator.buy_assist_dispatch import BuyAssistDispatcher


def test_parse_notification() -> None:
    alert = parse_changedetection_notification(
        {"uuid": "abc", "watch_url": "http://example.com", "title": "Restock"}
    )
    assert alert.watch_uuid == "abc"
    assert alert.watch_url == "http://example.com"


def test_meter_counts() -> None:
    m = AshMeter(stub_balance=100)
    m.record_watch()
    m.record_buy_assist()
    snap = m.snapshot()
    assert snap["watches"] == 1
    assert snap["buy_assists"] == 1
    assert snap["stub_balance"] == 94


def test_mass_buy_rejected() -> None:
    with pytest.raises(ValueError):
        BuyAssistDispatcher.reject_mass_buy(5)
