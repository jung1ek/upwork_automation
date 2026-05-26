from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from proposal_automation.utils.prompt import *
from proposal_automation.utils.schema import *
from proposal_automation.utils.helper import *

def build_ingest_prompt(
    index_content: str,
    doc_type: str,
    content: str
) -> ChatPromptTemplate:
    """Build the prompt for ingesting a new document."""
    try:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(INGEST_PROMPT)
        ]).format_messages(
            source_text=content,
            doc_type=doc_type,
            index_content=index_content
        )
    except Exception as e:
        logger.error(f"Error building ingest prompt: {e}")
        raise


def build_select_pages_prompt(
    index_content: str,
    job_title: str,
    job_description: str,
) -> ChatPromptTemplate:
    """Build the prompt for selecting which pages to create/update based on the ingested document."""
    try:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(PAGE_SELECTOR_PROMPT)
        ]).format_messages(
            index_content=index_content,
            job_title=job_title,
            job_description=job_description
        )
    except Exception as e:
        logger.error(f"Error building select pages prompt: {e}")
        raise


def build_proposal_prompt(
    selected_pages_content: str,
    job_title: str,
    job_description: str,
    tone: str
) -> ChatPromptTemplate:
    """Build the prompt for generating a cover letter based on the selected pages and job description."""
    try:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(PROPOSAL_PROMPT)
        ]).format_messages(
            job_title=job_title,
            job_description=job_description,
            wiki_content=selected_pages_content,
            tone=tone
        )
    except Exception as e:
        logger.error(f"Error building cover letter prompt: {e}")
        raise


def build_feedback_proposal(
    old_proposal: str,
    feedback: str,
)-> List:
    try:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(PROPOSAL_IMPROVEMENT_PROMPT),
        ]).format_messages(
            old_proposal=old_proposal,
            feedback=feedback
        )
    except Exception as e:
        logger.error(f"Error building feedback proposal prompt: {e}")
        raise
