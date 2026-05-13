from playwright.async_api import async_playwright
from playwright.async_api import (
    Playwright, Browser, BrowserContext
)

PORT = "9222"

_p: Playwright = None
_bw: Browser = None
_ctx: BrowserContext = None

async def get_context():
    global _bw, _ctx, _p
    if _ctx is None:
        _p = await async_playwright().start()
        _bw = await _p.chromium.connect_over_cdp(f"http://localhost:{PORT}")
        _ctx = _bw.contexts[0]
    return _ctx

async def close_browser():
    global _p, _bw, _ctx
    if _ctx:
        await _ctx.close()
    if _bw:
        await _bw.close()
    if _p:
        await _p.stop()