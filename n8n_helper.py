
from proposal_automation.portfolio_engine import PortfolioWiki
from gmail_webhook.gmail_watch import get_gmail_service, log
from gmail_webhook.gmail_helper import (
    fetch_thread_id,
    fetch_thread_data,
)
import redis_client


async def fetch_from_gmail():
    service = get_gmail_service()

    # 1. Fetch thread IDs
    try:
        thread_ids = fetch_thread_id(service)

        log.info(
            "Thread IDs found: %s",
            len(thread_ids),
        )

    except Exception as exc:
        log.error(
            "Error fetching thread IDs: %s",
            exc,
        )
        return

    if not thread_ids:
        log.info("No thread found — skipping")
        return

    thread_id = thread_ids[0]

    redis_key = f"processed_gmail_thread:{thread_id}"

    # 2. Atomic deduplication via Redis
    try:
        is_new = await redis_client.redis_client.set(
            redis_key,
            "1",
            nx=True,
            ex=86400,
        )

    except Exception as exc:
        log.error(
            "Redis deduplication error for %s: %s",
            thread_id,
            exc,
        )
        raise

    #Already processed
    if not is_new:
        log.info(
            "Thread %s already processed — skipping duplicate",
            thread_id,
        )
        return

    log.info(
        "Processing new thread: %s",
        thread_id,
    )

    # 3. Fetch thread data
    try:
        result_data = fetch_thread_data(
            service,
            thread_id,
        )
        return result_data

    except Exception as exc:
        log.error(
            "Error fetching thread data for %s: %s",
            thread_id,
            exc,
        )
        return