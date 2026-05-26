from typing import Type

from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage

from logger import Logger
logger = Logger().get_logger()

def invoke_llm(
    llm: ChatOpenAI,
    messages: list[SystemMessage | HumanMessage],
    schema: Type[BaseModel]
) -> Type[BaseModel]:
    """Invoke the LLM with a prompt and parse the response into a Pydantic model."""
    try:
        structured_llm = llm.with_structured_output(schema)
        return structured_llm.invoke(messages)
    except Exception as e:
        logger.error(f"Error invoking LLM: {e}")
        raise