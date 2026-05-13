from typing import List, Optional, Union
from playwright.async_api import ElementHandle, Frame, Page, async_playwright

from captcha.utils import *
from setup import *
from search_jobs.utils import *
from search_jobs.run_job_search import *

try:
    from logger import Logger
    logger = Logger().get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)


UPWORK_SEARCH_URL = "https://www.upwork.com/nx/search/jobs/"
JOB_PAGE_URL = "https://www.upwork.com/freelance-jobs/apply/Multilingual-WhatsApp-Telegram-Chatbot-for-Agency-Lead-Communication-Automation_~022054189827018457550/"

CF_IFRAME_SRC  = 'https://challenges.cloudflare.com/cdn-cgi/challenge-platform/'
CF_CHECKBOX    = 'input[type="checkbox"]'  

async def main():
    context = await get_context()
    page = await context.new_page()
    # full_search_url = build_search_url({"query":"ai", "per_page":20, "sort":"recency"})
    await page.goto(url=JOB_PAGE_URL,wait_until="domcontentloaded")

    # await scrape_jobs_cards(page)
    await scrape_job_detail(page)
    await close_browser()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())