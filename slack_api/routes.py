from __future__ import annotations
import json
import threading

from fastapi import Form
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from slack_api.slack import get_client
from slack_api.message import send_via_bot
from slack_api.helper import (
    create_manual_edit_view,
    create_feedback_view,
)
from proposal_automation.app import feedback_proposal
from logger import Logger

log = Logger().get_logger()

router = APIRouter()

slack_channel_id = "#feedback-proposal"


# SLACK INTERACTIONS, called by slack buttons
@router.post("/slack/actions")
async def slack_actions(payload: str = Form(...)):
    """Slack button actions endpoint"""
    try:
        payload_data = json.loads(payload)
    except Exception as e:
        log.error("Error parsing Slack payload: %s", e)
        return JSONResponse(content={}, status_code=400)

    client = get_client()

    # BUTTON ACTIONS
    if payload_data["type"] == "block_actions":

        action = payload_data["actions"][0]
        action_id = action["action_id"]

        # Manual edit button
        if action_id == "edit_human":
            try:
                current_proposal = action["value"]

                channel_id = payload_data["channel"]["id"]
                message_ts = payload_data["message"]["ts"]

                client.conversations_join(channel=channel_id)
                result = client.conversations_history(
                    channel=channel_id,
                    oldest=message_ts,
                    latest=message_ts,
                    inclusive=True,
                    limit=1,
                )

                client.views_open(
                    trigger_id=payload_data["trigger_id"],
                    view=create_manual_edit_view(
                        channel_id, message_ts, current_proposal
                    ),
                )
            except Exception as e:
                log.error("Error opening manual edit modal: %s", e)
            return JSONResponse(content={})

        # feedback ai edit button
        elif action_id == "edit_ai":
            try:

                channel_id = payload_data["channel"]["id"]
                message_ts = payload_data["message"]["ts"]

                client.views_open(
                    trigger_id=payload_data["trigger_id"],
                    view=create_feedback_view(
                        channel_id, message_ts
                    ),
                )
            except Exception as e:
                log.error("Error opening AI feedback modal: %s", e)
            return JSONResponse(content={})

    # modal submit actions
    elif payload_data["type"] == "view_submission":
        callback_id = payload_data["view"]["callback_id"]

        # manual edit save
        if callback_id == "proposal_modal":
            try:
                updated_proposal = payload_data["view"]["state"]["values"][
                    "proposal_block"
                ]["proposal_input"]["value"]

                metadata = json.loads(payload_data["view"]["private_metadata"])

                channel_id = metadata["channel_id"]
                message_ts = metadata["message_ts"]

                client.conversations_join(channel=channel_id)
                result = client.conversations_history(
                    channel=channel_id,
                    oldest=message_ts,
                    latest=message_ts,
                    inclusive=True,
                    limit=1,
                )

                blocks = result["messages"][0]["blocks"]

                # UPDATE PROPOSAL TEXT
                for block in blocks:

                    # proposal section
                    if block.get("block_id") == "proposal_section":

                        block["text"]["text"] = f"*📝 Proposal:*\n{updated_proposal}"

                    # update button values
                    if block.get("block_id") == "action_buttons":

                        for element in block["elements"]:

                            if element["action_id"] in [
                                "edit_human",
                                "edit_ai",
                            ]:
                                element["value"] = updated_proposal

                # UPDATE SAME MESSAGE
                client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    text="Updated Proposal",
                    blocks=blocks,
                )
            except Exception as e:
                log.error("Error updating proposal: %s", e)

            # CLOSE MODAL
            return JSONResponse(content={"response_action": "clear"})

        # feedback ai submit
        elif callback_id == "ai_feedback_modal":
            try:
                metadata = json.loads(payload_data["view"]["private_metadata"])

                channel_id = metadata["channel_id"]
                message_ts = metadata["message_ts"]
                feedback = payload_data["view"]["state"]["values"]["feedback_block"][
                    "feedback_input"
                ]["value"]
            except Exception as e:
                log.error("Error parsing AI feedback: %s", e)

            try:
                thread = threading.Thread(
                    target=process_in_background,
                    args=(client, channel_id, message_ts, feedback),
                )
                thread.start()
            except Exception as e:
                log.error("Thread Error: %s", e)

            return JSONResponse(content={"response_action": "clear"})

    return JSONResponse(content={})


# background threading method
def process_in_background(client, channel_id, message_ts, feedback):
    
    client.conversations_join(channel=channel_id)
    result = client.conversations_history(
        channel=channel_id,
        oldest=message_ts,
        latest=message_ts,
        inclusive=True,
        limit=1,
    )

    blocks = result["messages"][0]["blocks"]

    proposal = None
    for block in blocks:
        if block.get("block_id") == "proposal_section":
            text = block["text"]["text"]
            proposal = text.split("\n", 1)[1] if "\n" in text else text
            break

    if not proposal:
        return

    new_proposal = feedback_proposal(feedback, proposal)  # AI call happens here

    for block in blocks:
        if block.get("block_id") == "proposal_section":
            block["text"]["text"] = f"*📝 Proposal:*\n{new_proposal}"

    for block in blocks:
        if block.get("block_id") == "action_buttons":
            for element in block["elements"]:
                if element.get("action_id") in ["edit_human", "edit_ai"]:
                    element["value"] = new_proposal

    send_via_bot(channel=slack_channel_id, blocks=blocks)
