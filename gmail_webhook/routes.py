from __future__ import annotations

from fastapi.routing import APIRouter
from fastapi import Request, BackgroundTasks
from fastapi.responses import JSONResponse

from redis.asyncio import Redis

from gmail_webhook.gmail_watch import get_gmail_service, log
from gmail_webhook.gmail_helper import (
    fetch_thread_id,
    fetch_thread_data,
)
from proposal_automation.app import generate_proposal
from slack_api.message import send_via_bot
from slack_api.helper import create_blocks
import redis_client

router = APIRouter()

slack_channel_id = "#upwork-proposal"


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    bg_tasks: BackgroundTasks,
):
    """
    Gmail push webhook endpoint.
    Immediately ACKs request and processes in background.
    """

    try:
        await request.json()
    except Exception:
        pass

    bg_tasks.add_task(background_process)

    return JSONResponse(
        content={"status": "ok"},
        status_code=200,
    )


async def background_process():
    """
    Processes latest Gmail thread and sends proposal to Slack.
    Deduplication is handled atomically via Redis.
    """

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

    # Already processed
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

    except Exception as exc:
        log.error(
            "Error fetching thread data for %s: %s",
            thread_id,
            exc,
        )
        return

    if not result_data:
        log.info(
            "Thread %s is not an Upwork job — skipping",
            thread_id,
        )
        return

    # 4. Generate proposal
    try:
        job_title = result_data.get("job_title")
        job_description = result_data.get("description")

        proposal = generate_proposal(
            job_description=job_description,
            job_title=job_title,
            tone="formal",
        )

        log.info(
            "Proposal generated for: %s",
            job_title,
        )

    except Exception as exc:
        log.error(
            "Error generating proposal for %s: %s",
            thread_id,
            exc,
        )
        return

    # 5. Build Slack blocks
    try:
        slack_msg_blocks = create_blocks(
            job_title,
            proposal,
            result_data.get("budget", "Not Given"),
            result_data.get("client_rating", ""),
            result_data.get("location", "Not Given"),
            result_data.get("hire_rate", ""),
            result_data.get("avg_rate", "Not Given"),
            result_data.get("apply_url", ""),
        )

    except Exception as exc:
        log.error(
            "Error creating Slack blocks for %s: %s",
            thread_id,
            exc,
        )
        return

    # 6. Send to Slack
    try:
        send_via_bot(
            slack_channel_id,
            slack_msg_blocks,
        )

        log.info(
            "Slack message sent for: %s",
            job_title,
        )

    except Exception as exc:
        log.error(
            "Error sending Slack message for %s: %s",
            thread_id,
            exc,
        )
        return
