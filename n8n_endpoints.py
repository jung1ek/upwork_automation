from __future__ import annotations

from pydantic import BaseModel
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from n8n_helper import fetch_from_gmail
from proposal_automation.proposal_app import generate_proposal
from slack_api.helper import create_blocks
from slack_api.message import send_via_bot, log

router = APIRouter()


@router.get("/get-job")
async def get_job():
    job_result = await fetch_from_gmail()
    if job_result:
        return JSONResponse(
            content=job_result,
            status_code=200
        )
    return JSONResponse(
        content={
            "status": "error"
        },
        status_code=500
    )


@router.post("/write-proposal")
async def write_proposal(job: JobDetail):
    job_data =  job.model_dump()

    proposal = generate_proposal(
        job_title=job.title,
        job_description=job.description,
        tone="natural"
    )

    job_data["proposal"] = proposal

    return JSONResponse(
        content=job_data,
        status_code=200
    )


@router.put("/send-slack")
async def send_msg_slack(job: JobDetailWithProp):

    slack_channel_id = "#upwork-proposal"

    try:
        slack_msg_blocks = create_blocks(
            job.title, job.proposal,
            job.budget, job.client_rating,
            job.location, job.hire_rate,
            job.avg_rate, job.apply_url
        )

    except Exception as exc:
        log.error(
            "Error creating Slack blocks for %s: %s",
            exc,
        )
        raise

    try:
        send_via_bot(
            slack_channel_id,
            slack_msg_blocks,
        )

        log.info(
            "Slack message sent for: %s",
            job.title,
        )
    except Exception as exc:
        log.error(
            "Error sending Slack message : %s",
            exc,
        )
        raise

    

class JobDetail(BaseModel):
    title: str
    description: str
    budget: str
    client_rating: str
    location: str
    hire_rate: str
    total_spent: str
    avg_rate: str
    hires: str
    apply_url: str
    view_url: str


class JobDetailWithProp(BaseModel):
    title: str
    description: str
    budget: str
    client_rating: str
    location: str
    hire_rate: str
    total_spent: str
    avg_rate: str
    hires: str
    apply_url: str
    view_url: str
    proposal: str



    