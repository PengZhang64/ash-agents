from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class AshMeter:
    """Stub $ASH meter — counts watches and buy-assists."""

    stub_balance: int = 1000
    watches: int = 0
    buy_assists: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def record_watch(self) -> None:
        with self._lock:
            self.watches += 1
            self.stub_balance = max(0, self.stub_balance - 1)

    def record_buy_assist(self) -> None:
        with self._lock:
            self.buy_assists += 1
            self.stub_balance = max(0, self.stub_balance - 5)

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return {
                "stub_balance": self.stub_balance,
                "watches": self.watches,
                "buy_assists": self.buy_assists,
            }
