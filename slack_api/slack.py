import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from logger import Logger

log = Logger().get_logger()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

client = None


def get_client():
    global client
    try:
        if not client:
            client = WebClient(token=SLACK_BOT_TOKEN)

        log.info("Slack client connected successfully.")
        return client
    except SlackApiError as se:
        log.error(f"Error starting slack bot client{se}")
