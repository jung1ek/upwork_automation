# ref repo: https://github.com/calebmwelsh/Upwork-Job-Scraper.git

from typing import Union, List, Optional

from playwright.async_api import(
    Page, Frame, Locator,
    ElementHandle
)

from logger import Logger

logger = Logger().get_logger()


async def patch_closed_shadow_roots(page: Page) -> None:
    """
    Intercept Element.attachShadow at the CDP level to force all shadow roots
    to open mode, exposing them via node.shadowRootUnl before the page loads.
    Must be called before page.goto().
    """
    await page.add_init_script("""
        (() => {
            const _attachShadow = Element.prototype.attachShadow;
            Element.prototype.attachShadow = function(init) {
                const root = _attachShadow.call(this, { ...init, mode: 'open' });
                this.shadowRootUnl = root;
                return root;
            };
        })();
    """)
    logger.debug('Closed shadow root patch applied.')


async def get_shadow_roots(
        page: Union[Page, Frame, Locator]
)-> List[Union[ElementHandle,Locator]]:
    """
    Recursively collect all shadow roots (open or patched-closed).
    patch_closed_shadow_roots() must have been called before page.goto().
    """
    js = """
    () => {
        const roots = [];
        function collectShadowRoots(node) {
            if (!node) return;
            const shadowRoot = node.shadowRoot || node.shadowRootUnl;
            if (shadowRoot) {
                roots.push(shadowRoot);
                for (const el of shadowRoot.querySelectorAll('*')) {
                    collectShadowRoots(el);
                }
            }
            if (typeof node.querySelectorAll === 'function') {
                for (const el of node.querySelectorAll('*')) {
                    if (el.shadowRoot || el.shadowRootUnl) {
                        collectShadowRoots(el);
                    }
                }
            }
        }
        collectShadowRoots(document);
        return roots;
    }
    """
    js_handle = await page.evaluate_handle(js)

    # list of elementhandle
    properties = await js_handle.get_properties()

    shadow_roots = []
    for prop_handle in properties.values():
        element = prop_handle.as_element()
        if element:
            shadow_roots.append(element)
    return shadow_roots


async def search_shadow_root_elements(
        page: Union[Page, Frame, Locator],
        selector: str
)-> List[Locator]:
    """
    Find all elements matching a css selector inside every shadow root.
    """
    elements = []
    try:
        shadow_roots = await get_shadow_roots(page)
        for shadow_root in shadow_roots:
            try:
                result_handle = await shadow_root.evaluate_handle(
                    f"shadow => Array.from(shadow.querySelectorAll('{selector}'))"
                )
                props = await result_handle.get_properties()
                for prop in props.values():
                    element = prop.as_element()
                    if element:
                        elements.append(element)
            except Exception as e:
                logger.debug
            except Exception as e:
                logger.debug(f"Error querying shadow root: {e}")
    except Exception as e:
        logger.debug(f"Error in search_shadow_root_elements: {e}")
    return elements


async def get_shadow_iframes(
        page: Union[Page, Frame, Locator],
        src_filter: str,
)-> Optional[List[Frame]]:
    """
    Find all iframes inside shadow roots whose src contains src_filter.
    """
    matched_iframes = []
    try:
        iframe_elements = await search_shadow_root_elements(page, 'iframe')
        logger.debug(f'Found {len(iframe_elements)} iframe(s) in shadow roots')

        for iframe_element in iframe_elements:
            try:
                src_prop = await iframe_element.get_property('src')
                src = await src_prop.json_value()
                logger.debug(f'iframe src: {src}')

                if src_filter in src:
                    cf_iframe = await iframe_element.content_frame()
                    if cf_iframe is None or cf_iframe.is_detached():
                        logger.debug(f'Skipping detached or null iframe: {src}')
                        continue
                    logger.debug(f'Matched iframe: {src}')
                    matched_iframes.append(cf_iframe)
            except Exception as e:
                logger.debug(f'Error processing iframe element: {e}')
    except Exception as e:
        logger.debug(f'Error in search_shadow_root_iframes: {e}')
    return matched_iframes


async def get_check_box(
    frame: Frame,
    checkbox_selector: str,
    timeout=30_000
)-> Optional[Locator]:
    try:
        await frame.wait_for_selector(checkbox_selector,timeout=timeout)
        logger.info(f"Found checkbox [{checkbox_selector}] in frame {frame.url}")
        return frame.locator(checkbox_selector)
    except Exception as e:
        logger.debug(f"Failed to load check box [{checkbox_selector}]\
                     in frame {frame.url}: {e}")

