import json


# blocks builder
def create_blocks(
    job_title: str,
    proposal: str,
    budget: str,
    client_rating: str,
    location: str,
    hire_rate: str,
    avg_rate: str,
    apply_url: str,
) -> dict:
    return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🗂️ Job Proposal: {job_title}",
                },
            },
            {"type": "divider"},
            # CLIENT INFO
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*👤 Client Info:*",
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*🌍 Location:*\n{location}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*💰 Budget:*\n{budget}",
                    },
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*🌟 Client Rating:*\n{client_rating}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🤝 Hire Rate:*\n{hire_rate}",
                    },
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📈 Avg Rate:*\n{avg_rate}",
                    },
                ],
            },
            {"type": "divider"},
            # PROPOSAL
            {
                "type": "section",
                "block_id": "proposal_section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*✍️ Proposal:*\n{proposal}",
                },
            },
            {"type": "divider"},
            # ACTION BUTTONS
            {
                "type": "actions",
                "block_id": "action_buttons",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✏️ Manual Edit",
                        },
                        "style": "primary",
                        "action_id": "edit_human",
                        "value": proposal,
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 AI Rewrite",
                        },
                        "style": "primary",
                        "action_id": "edit_ai",
                        "value": proposal,
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🚀 Apply Now",
                        },
                        "url": apply_url,
                        "style": "primary",
                    },
                ],
            },
    ]
    

# creates the manual edit view
def create_manual_edit_view(
    channel_id, message_ts, current_proposal
) -> dict:
    return {
        "type": "modal",
        "callback_id": "proposal_modal",
        "private_metadata": json.dumps(
            {
                "channel_id": channel_id,
                "message_ts": message_ts,
            }
        ),
        "title": {
            "type": "plain_text",
            "text": "Edit Proposal",
        },
        "submit": {
            "type": "plain_text",
            "text": "Save",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "proposal_block",
                "label": {
                    "type": "plain_text",
                    "text": "Proposal",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "proposal_input",
                    "multiline": True,
                    "initial_value": current_proposal,
                },
            }
        ],
    }


# create the feedback action view
def create_feedback_view(
    channel_id, message_ts
) -> dict:
    return {
        "type": "modal",
        "callback_id": "ai_feedback_modal",
        "private_metadata": json.dumps(
            {
                "channel_id": channel_id,
                "message_ts": message_ts,
            }
        ),
        "title": {
            "type": "plain_text",
            "text": "AI Improve Proposal",
        },
        "submit": {
            "type": "plain_text",
            "text": "Generate",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "feedback_block",
                "label": {
                    "type": "plain_text",
                    "text": "What should AI improve?",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "feedback_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Example: Make it shorter and more confident",
                    },
                },
            }
        ],
    }
