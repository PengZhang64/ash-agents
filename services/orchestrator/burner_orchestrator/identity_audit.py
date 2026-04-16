from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class IdentityRecord:
    fingerprint_seed: str
    proxy_url: str | None
    user_agent: str
    check_index: int


class IdentityAuditLog:
    def __init__(self, maxlen: int = 50) -> None:
        self._records: deque[IdentityRecord] = deque(maxlen=maxlen)
        self._lock = Lock()
        self._check_counter = 0

    def record(self, fingerprint_seed: str, proxy_url: str | None, user_agent: str) -> IdentityRecord:
        with self._lock:
            self._check_counter += 1
            rec = IdentityRecord(
                fingerprint_seed=fingerprint_seed,
                proxy_url=proxy_url,
                user_agent=user_agent,
                check_index=self._check_counter,
            )
            self._records.append(rec)
            return rec

    def recent(self, n: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            items = list(self._records)[-n:]
            return [
                {
                    "check_index": r.check_index,
                    "fingerprint_seed": r.fingerprint_seed,
                    "proxy_url": r.proxy_url,
                    "user_agent": r.user_agent,
                }
                for r in items
            ]

    def consecutive_differ(self) -> bool:
        with self._lock:
            if len(self._records) < 2:
                return False
            a, b = self._records[-2], self._records[-1]
            return a.fingerprint_seed != b.fingerprint_seed or a.proxy_url != b.proxy_url
