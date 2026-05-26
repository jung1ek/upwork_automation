from __future__ import annotations

from slack_sdk.errors import SlackApiError

from slack_api.slack import get_client
from logger import Logger

log = Logger().get_logger()


# SEND INITIAL MESSAGE
def send_via_bot(
    channel: str,
    blocks: list,
):
    try:
        client = get_client()
        response = client.chat_postMessage(
            channel=channel,
            text="Upwork Job Proposal",
            blocks=blocks,
        )

        log.info(f"Message sent: {response["ts"]}")
        return response

    except SlackApiError as e:
        log.error(f"Slack Error: {e.response["error"]}")
        raise
