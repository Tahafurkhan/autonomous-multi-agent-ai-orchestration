import asyncio

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)

from app.graph.state import TravelState
from app.llm.client import llm
from app.mcp.client import aviation_mcp_call
from app.core.logging import get_logger


logger = get_logger(__name__)


def flight_agent(
    state: TravelState
):

    logger.info(
        "Flight agent started"
    )

    try:

        airports = asyncio.run(
            aviation_mcp_call(
                "list_airports"
            )
        )

        airlines = asyncio.run(
            aviation_mcp_call(
                "list_airlines"
            )
        )

        prompt = f"""
User Query:
{state["user_query"]}

Airport Information:
{str(airports)[:3000]}

Airline Information:
{str(airlines)[:3000]}

Provide:

1. Departure airport
2. Arrival airport
3. Airlines
4. Typical duration
5. Estimated airfare
6. Peak season warning
7. Booking advice

Clearly distinguish estimates
from live information.
"""

        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a flight planning expert."
                    )
                ),
                HumanMessage(
                    content=prompt
                ),
            ]
        )

        result = str(
            response.content
        )

        logger.info(
            "Flight agent completed"
        )

        return {
            "flight_results": result,
            "messages": [
                AIMessage(
                    content=(
                        "Flight recommendations generated."
                    )
                )
            ],
            "llm_calls": (
                state.get("llm_calls", 0) + 1
            ),
        }

    except Exception as exc:

        logger.exception(
            "Flight agent failed"
        )

        return {
            "flight_results": (
                "Flight information is "
                "temporarily unavailable."
            ),
            "messages": [
                AIMessage(
                    content=(
                        "Flight agent encountered "
                        "an error."
                    )
                )
            ],
        }