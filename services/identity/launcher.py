"""CloakBrowser / Playwright launcher hooks."""

from __future__ import annotations

import os
from typing import Any

from identity.rotation import DisposableIdentity


def launch_cloakbrowser(identity: DisposableIdentity) -> dict[str, Any]:
    """Launch CloakBrowser when enabled; otherwise return config for Playwright fetcher."""
    enabled = os.environ.get("CLOAKBROWSER_ENABLED", "false").lower() == "true"
    return {
        "engine": "cloakbrowser" if enabled else "playwright",
        "fingerprint_seed": identity.fingerprint_seed,
        "proxy_url": identity.proxy_url,
        "user_agent": identity.user_agent,
    }


async def fetch_with_playwright(url: str, identity: DisposableIdentity) -> str:
    """Fallback fetcher using Playwright (used when CloakBrowser not installed)."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError("playwright not installed") from e

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=identity.user_agent)
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        content = await page.content()
        await browser.close()
        return content
