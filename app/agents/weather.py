import asyncio

from langchain_core.messages import AIMessage

from app.graph.state import TravelState
from app.mcp.client import (
    weather_mcp_search,
    forecast_mcp_search,
    extract_destination,
)
from app.core.logging import get_logger


logger = get_logger(__name__)


def weather_agent(
    state: TravelState
):

    city = extract_destination(
        state["user_query"]
    )

    logger.info(
        "Weather agent started city=%s",
        city
    )

    try:

        current = asyncio.run(
            weather_mcp_search(city)
        )

        forecast = asyncio.run(
            forecast_mcp_search(city)
        )

        result = f"""
Current Weather:
{current}

Forecast:
{forecast}
"""

        return {
            "weather_results": result,
            "messages": [
                AIMessage(
                    content=(
                        "Weather information processed."
                    )
                )
            ],
        }

    except Exception:

        logger.exception(
            "Weather MCP request failed"
        )

        return {
            "weather_results": (
                f"Live weather information "
                f"for {city} is unavailable."
            ),
            "messages": [
                AIMessage(
                    content=(
                        "Weather service unavailable."
                    )
                )
            ],
        }