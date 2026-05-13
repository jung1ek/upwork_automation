from typing import Literal, Union

from playwright.async_api import Page, Frame, Locator
from playwright._impl._errors import Error as PlaywrightException

from logger import Logger

logger = Logger().get_logger()

# selectors for detecting Cloudflare interstitial challenge (page)
CF_INTERSTITIAL_INDICATORS_SELECTORS = [
    'script[src*="/cdn-cgi/challenge-platform/"]',
]

# selectors for detecting Cloudflare turnstile challenge (small embedded captcha)
CF_TURNSTILE_INDICATORS_SELECTORS = [
    'input[name="cf-turnstile-response"]',
    'script[src*="challenges.cloudflare.com/turnstile/v0"]',
]

async def detect_cloudflare_challenge(
        page: Union[Page, Frame, Locator],
        challenge_type:Literal['turnstile', 'interstitial']="turnstile"
)-> bool:
    selectors = CF_INTERSTITIAL_INDICATORS_SELECTORS if challenge_type == \
        'interstitial' else CF_TURNSTILE_INDICATORS_SELECTORS
    for selector in selectors:
        try:
            await page.wait_for_load_state("domcontentloaded")
            element = await page.query_selector(selector)
        except PlaywrightException as e:
            raise

        if not element:
            continue
        logger.info(f" 🛡️  CF challenge (type: {challenge_type})")
        return True
    return False



async def detect_expected_content(
        page: Union[Page, Frame, Locator],
        expected_content_selector: str
):
    if not expected_content_selector:
        return False
    
    element = await page.locator(expected_content_selector).count()
    return bool(element)