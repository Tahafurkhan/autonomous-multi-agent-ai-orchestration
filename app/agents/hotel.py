import asyncio

from langchain_core.messages import AIMessage

from app.graph.state import TravelState
from app.mcp.client import tavily_mcp_search
from app.core.logging import get_logger


logger = get_logger(__name__)


def hotel_agent(
    state: TravelState
):

    logger.info(
        "Hotel agent started"
    )

    query = (
        "Best hotels for "
        + state["user_query"]
    )

    try:

        results = asyncio.run(
            tavily_mcp_search(query)
        )

        logger.info(
            "Hotel search completed"
        )

        return {
            "hotel_results": results,
            "messages": [
                AIMessage(
                    content=(
                        "Hotel information processed."
                    )
                )
            ],
        }

    except Exception:

        logger.exception(
            "Hotel MCP search failed"
        )

        return {
            "hotel_results": (
                "Live hotel search is "
                "temporarily unavailable."
            ),
            "messages": [
                AIMessage(
                    content=(
                        "Hotel search temporarily unavailable."
                    )
                )
            ],
        }