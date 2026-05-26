from typing import Literal

from pathlib import Path

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI

from logger import Logger

log = Logger().get_logger()


class ValidateJobSchema(BaseModel):
    verdict: Literal["APPLY", "SKIP"]
    score:   float         = Field(ge=0, le=100)
    flags:   list[str]     = Field(default_factory=list)

filter_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", Path("FILTER_PROMPT.md").read_text())
    ]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def build_filter_prompt(job: dict) -> str:
    fields = {
        "job_title":     job.get("job_title", ""),
        "description":   job.get("description", ""),
        "client_rating": job.get("client_rating", ""),
        "hire_rate":     job.get("hire_rate", ""),
        "total_spent":   job.get("total_spent") or "empty",
        "hires":         job.get("hires", ""),
        "location":      job.get("location", ""),
        "budget":        job.get("budget", ""),
        "proposals":     job.get("proposals", "unknown"),
    }
    try:
        return filter_prompt.format_messages(**fields)
    except Exception as e:
        log.error(f"Error formatting filter prompt: {e}")
        raise

def invoke_filter(job: dict) -> ValidateJobSchema:
    try:
        prompt = build_filter_prompt(job)
        structured_llm = llm.with_structured_output(ValidateJobSchema, timeout=10)
        return structured_llm.invoke(prompt)
    except Exception as e:
        log.error(f"Error invoking LLM filter: {e}")
        raise

