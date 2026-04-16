from __future__ import annotations

from typing import Any

import httpx

from burner_orchestrator.config import settings


class ChangedetectionClient:
    """Drive changedetection.io via REST API — we do not vendor its source."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = (base_url or settings.changedetection_url).rstrip("/")
        self.api_key = api_key or settings.changedetection_api_key
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        self._headers = headers

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, headers=self._headers, timeout=30.0)

    def health(self) -> dict[str, Any]:
        with self._client() as c:
            r = c.get("/")
            r.raise_for_status()
            return {"reachable": True, "status_code": r.status_code}

    def create_watch(
        self,
        url: str,
        *,
        title: str = "Burner watch",
        tag: str = "burner-sentinel",
        fetch_backend: str = "html_webdriver",
        proxy: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "url": url,
            "tag": tag,
            "title": title,
            "fetch_backend": fetch_backend,
            "processor": "restock_diff",
        }
        if proxy:
            payload["proxy_url"] = proxy
        with self._client() as c:
            r = c.post("/api/v1/watch", json=payload)
            r.raise_for_status()
            return r.json()

    def list_watches(self) -> list[dict[str, Any]]:
        with self._client() as c:
            r = c.get("/api/v1/watch")
            r.raise_for_status()
            data = r.json()
            return list(data.values()) if isinstance(data, dict) else data

    def update_watch_proxy(self, watch_uuid: str, proxy_url: str) -> dict[str, Any]:
        with self._client() as c:
            r = c.put(f"/api/v1/watch/{watch_uuid}", json={"proxy_url": proxy_url})
            r.raise_for_status()
            return r.json()
