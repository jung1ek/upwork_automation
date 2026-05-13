from playwright.async_api import Page

from utils import get_shadow_iframes, get_check_box
from scraping_upwork.logger import Logger

CF_IFRAME_SRC  = 'https://challenges.cloudflare.com/cdn-cgi/challenge-platform/'
CF_CHECKBOX    = 'input[type="checkbox"]'  

logger = Logger().get_logger()

async def click_cf_checkbox(page: Page):
    # give JS components time to mount (shadow DOM, CF widget, etc.)
    await page.wait_for_timeout(3000)

    # get cloudflare iframe
    try:
        cf_iframes = await get_shadow_iframes(page,CF_IFRAME_SRC)
        cf_frame = cf_iframes[0]
    except Exception as e:
        logger.error(f"")
    
    # get iframe checkbox and click
    try:
        checkbox = await get_check_box(cf_frame,CF_CHECKBOX)
        await cf_frame.wait_for_timeout(5000)
        await checkbox.click()
    except Exception as e:
        logger.error(f"")