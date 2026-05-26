from proposal_automation.utils.prompt_builder import build_feedback_proposal
from proposal_automation.portfolio_engine import PortfolioWiki
from logger import Logger

log = Logger().get_logger()

intel_wiki = PortfolioWiki("proposal_automation","gpt-4o-mini")


def generate_proposal(
    job_title: str, 
    job_description: str,
    tone: str
):
    return intel_wiki.write_proposal(
        job_title=job_title,
        job_description=job_description,
        tone=tone
    )


def feedback_proposal(
    feedback: str,
    old_proposal: str
):
    new_proposal_prompt = build_feedback_proposal(
        old_proposal=old_proposal,
        feedback=feedback
    )
    try:
        intel_wiki.llm.temperature = 0.7
        response = intel_wiki.llm.invoke(new_proposal_prompt)
        return response.content
    except Exception as e:
        log.error("Error while generating feedback proposal")
        raise