from __future__ import annotations

from typing import Any

from identity.rotation import DisposableIdentity


class AgentSession:
    """Isolated Playwright browser context for one disposable agent task."""

    def __init__(self, identity: DisposableIdentity) -> None:
        self.identity = identity
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None
        self.url: str = ""

    async def start(self) -> None:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("playwright not installed; run: playwright install chromium") from exc

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context(user_agent=self.identity.user_agent)
        self._page = await self._context.new_page()

    async def goto(self, url: str) -> None:
        if not self._page:
            raise RuntimeError("session not started")
        self.url = url
        await self._page.goto(url, wait_until="domcontentloaded", timeout=20000)

    async def click(self, selector: str) -> None:
        if not self._page:
            raise RuntimeError("session not started")
        await self._page.click(selector, timeout=10000)

    async def snapshot(self) -> str:
        if not self._page:
            return ""
        title = await self._page.title()
        try:
            badge = await self._page.locator("#stock-badge").inner_text()
        except Exception:
            badge = ""
        try:
            heading = await self._page.locator("h1").inner_text()
        except Exception:
            heading = ""
        try:
            buy_disabled = await self._page.locator("#buy-btn").is_disabled()
        except Exception:
            buy_disabled = True
        return (
            f"url={self.url}\ntitle={title}\nproduct={heading}\nstock_badge={badge}\n"
            f"buy_button_disabled={buy_disabled}"
        )

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
