from playwright.async_api import Page

from search_jobs.utils import build_search_url
from logger import Logger

logger = Logger().get_logger()


async def scrape_jobs_cards(page: Page):
    """Scraping search results job cards list."""

    selector = '[data-test="JobsList"]'
    jobs = []
    try:
        await page.wait_for_selector(selector)
        list_cont =  page.locator(selector).first
        cards = list_cont.locator("article[data-test='JobTile']")
        for i in range(await cards.count()):
            card = cards.nth(i)

            try:
                # posted time
                posted_el = card.locator('small[data-test="job-pubilshed-date"] span').last
                posted_raw = (await posted_el.inner_text()).strip()

                # title
                title_el = card.locator('a[data-test="job-tile-title-link UpLink"]')
                title_txt = (await title_el.inner_text()).strip()

                # job url
                href = await title_el.get_attribute("href")
                learn_more = (
                    href if href.startswith("http")
                    else f"https://www.upwork.com{href}"
                )

                # description
                desc_el = card.locator('div[data-test="UpCLineClamp JobDescription"] p')
                description = (await desc_el.inner_text()).strip()

                # skills/tokens
                skills = []

                skill_els = card.locator(
                    'div[data-test="TokenClamp JobAttrs"] button[data-test="token"]'
                )

                skill_count = await skill_els.count()

                for j in range(skill_count):
                    skill = (
                        await skill_els.nth(j).inner_text()
                    ).strip()

                    if skill:
                        skills.append(skill)

                # job info
                info_items = await card.locator(
                    'ul[data-test="JobInfo"] li'
                ).all_inner_texts()

                jobs.append({
                    "posted": posted_raw,
                    "title": title_txt,
                    "url": learn_more,
                    "description": description[:200],
                    "skills": skills,
                    "info": info_items,
                })

            except Exception as e:
                logger.error("ERROR:", e)
        return jobs
    except Exception as e:
        logger.error(f"Error for selector JobsList")


async def scrape_job_detail(page: Page):
    """Scrape Job detail of specific job."""

    job = {}
    try:
        # Title
        title_el = page.locator('h1.h4')
        job['title'] = (await title_el.inner_text()).strip()

        # Posted time
        posted_el = page.locator('.posted-on-line span')
        job['posted'] = (await posted_el.inner_text()).strip()

        # Description
        desc_el = page.locator('div[data-test="Description"] p')
        job['description'] = (await desc_el.inner_text()).strip()

        # Job info items (type, duration, experience, remote, project type)
        info = {}
        info_items = page.locator('ul.features li')
        count = await info_items.count()
        for i in range(count):
            item = info_items.nth(i)
            strong = item.locator('strong')
            desc_div = item.locator('.description')
            if await strong.count():
                value = (await strong.inner_text()).strip()
                label = (await desc_div.inner_text()).strip() if await desc_div.count() else ""
                info[label or f"item_{i}"] = value
        job['info'] = info

        # Skills (mandatory - visible ones)
        skills = []
        skill_els = page.locator(
            'section[data-v-3b2c2248] .skills-list .air3-badge'
        )
        skill_count = await skill_els.count()
        for i in range(skill_count):
            t = (await skill_els.nth(i).inner_text()).strip()
            if t:
                skills.append(t)
        job['skills'] = skills

        # Activity
        activity = {}
        activity_items = page.locator('ul.visitor.client-activity-items li.ca-item')
        act_count = await activity_items.count()
        for i in range(act_count):
            item = activity_items.nth(i)
            label = (await item.locator('.title').inner_text()).strip().rstrip(':')
            value = (await item.locator('.value').inner_text()).strip()
            activity[label] = value
        job['activity'] = activity

        # Client info
        client = {}
        location_el = page.locator('[data-qa="client-location"] strong')
        if await location_el.count():
            client['location'] = (await location_el.inner_text()).strip()

        member_since_el = page.locator('[data-qa="client-contract-date"] small')
        if await member_since_el.count():
            client['member_since'] = (await member_since_el.inner_text()).strip()

        job['client'] = client

    except Exception as e:
        print("ERROR:", e)

    return job

async def search_query_url(params: dict):
    """build search url bind with search parameters"""
    full_url = build_search_url(params)
    return full_url
