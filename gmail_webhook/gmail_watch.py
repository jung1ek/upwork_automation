import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from logger import Logger

log = Logger().get_logger()


# gmail watch setup to receive notifications for new emails in the inbox and send them to the pub/sub topic
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify"]

TOKEN_FILE = "gmail_webhook/token.json"

CREDS_FILE = "gmail_webhook/credentials.json"

PROJECT_ID   = "gmail-webhook-496805"

TOPIC_NAME   = f"projects/{PROJECT_ID}/topics/gmail-notifications"

UPWORK_ALERTS_LABEL = "Label_3145636649811196972"

#TODO renew every week
def get_credentials() -> Credentials:
    """Load saved creds or run OAuth flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )
 
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
 
    return creds


# build gmail service
def get_gmail_service():
    return build(
        "gmail", "v1", 
        credentials=get_credentials()
    )
 

# Gmail watch 
#TODO watch to specific labelIds for upworkalerts. see: documentation
def register_watch():
    """Tell Gmail to push new-message notifications to Pub/Sub."""

    log.info("Registering Gmail watch with topic %s", TOPIC_NAME)
    try:
        service = get_gmail_service()

        response = service.users().watch(
            userId="me",
            body={
                "labelIds": [UPWORK_ALERTS_LABEL],
                "topicName": TOPIC_NAME
            },
        ).execute()
        log.info("Watch registered: %s", response)

        return response
    except Exception as e:
        log.error(f"Error creating webhook watch {e}")
        raise


# stop the watch if it is already registered to avoid duplicate notifications
def stop_watch():
    service = get_gmail_service()
    log.info("Stopping Gmail watch")
    response = service.users().stop(userId="me").execute()
    log.info("Watch stopped: %s", response)
    return response
