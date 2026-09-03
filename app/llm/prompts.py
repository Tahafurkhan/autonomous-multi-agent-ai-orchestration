from typing import Any

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from app.llm.client import llm
from app.core.logging import get_logger
from app.core.exceptions import LLMException


logger = get_logger(__name__)


def llm_text(
    system_prompt: str,
    user_prompt: str,
) -> str:

    try:

        response = llm.invoke(
            [
                SystemMessage(
                    content=system_prompt
                ),
                HumanMessage(
                    content=user_prompt
                ),
            ]
        )

        return str(response.content)

    except Exception as exc:

        logger.exception(
            "LLM invocation failed"
        )

        raise LLMException(
            "LLM request failed.",
            "LLM_INVOCATION_ERROR"
        ) from exc


def json_from_llm(text: str) -> dict[str, Any]:

    import json

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise LLMException(
            "LLM did not return valid JSON.",
            "INVALID_LLM_JSON"
        )

    try:

        return json.loads(
            text[start:end + 1]
        )

    except json.JSONDecodeError as exc:

        raise LLMException(
            "Unable to parse LLM JSON response.",
            "JSON_PARSE_ERROR"
        ) from exc