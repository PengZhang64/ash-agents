from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class DisposableIdentity:
    fingerprint_seed: str
    proxy_url: str | None
    user_agent: str


class IdentityFactory:
    """Rotate a fresh fingerprint + proxy for each check."""

    def __init__(self, proxy_pool: str | None = None) -> None:
        raw = proxy_pool if proxy_pool is not None else os.environ.get("PROXY_POOL", "")
        self._proxies = [p.strip() for p in raw.split(",") if p.strip()]
        self._index = 0

    def _next_proxy(self) -> str | None:
        if not self._proxies:
            return None
        proxy = self._proxies[self._index % len(self._proxies)]
        self._index += 1
        return proxy

    def next_identity(self) -> DisposableIdentity:
        seed = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:16]
        ua_hash = hashlib.sha256(f"ua-{seed}".encode()).hexdigest()[:8]
        user_agent = f"BurnerSentinel/{ua_hash} (disposable check)"
        return DisposableIdentity(
            fingerprint_seed=seed,
            proxy_url=self._next_proxy(),
            user_agent=user_agent,
        )
