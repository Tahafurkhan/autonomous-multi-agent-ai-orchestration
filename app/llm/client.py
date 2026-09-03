from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMException


logger = get_logger(__name__)


def create_llm() -> ChatGroq:

    try:

        logger.info(
            "Initializing LLM model=%s",
            settings.LLM_MODEL
        )

        return ChatGroq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            max_tokens=settings.LLM_MAX_TOKENS,
            reasoning_effort=settings.LLM_REASONING_EFFORT,
            reasoning_format="hidden",
        )

    except Exception as exc:

        logger.exception(
            "Failed to initialize LLM"
        )

        raise LLMException(
            "Unable to initialize LLM.",
            "LLM_INIT_ERROR"
        ) from exc


llm = create_llm()