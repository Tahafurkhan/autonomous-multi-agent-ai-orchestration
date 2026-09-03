from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)

from app.graph.state import TravelState
from app.llm.client import llm
from app.core.logging import get_logger


logger = get_logger(__name__)


def itinerary_agent(
    state: TravelState
):

    logger.info(
        "Itinerary agent started"
    )

    prompt = f"""
Create a complete travel itinerary.

User:
{state["user_query"]}

Constraints:
{state.get("trip_constraints", {})}

Flights:
{state.get("flight_results", "")}

Hotels:
{state.get("hotel_results", "")}

Weather:
{state.get("weather_results", "")}

Budget:
{state.get("budget_results", "")}

Create a practical,
budget-aware day-by-day itinerary.

This is a draft and will be
reviewed by a human.
"""

    try:

        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an expert travel planner."
                    )
                ),
                HumanMessage(
                    content=prompt
                ),
            ]
        )

        itinerary = str(
            response.content
        )

        approval_request = (
            "Please review the generated "
            "draft itinerary. Approve it "
            "or provide revision feedback."
        )

        return {
            "itinerary": itinerary,
            "approval_request": approval_request,
            "messages": [
                AIMessage(
                    content=(
                        "Draft itinerary created "
                        "for human review."
                    )
                )
            ],
            "llm_calls": (
                state.get("llm_calls", 0) + 1
            ),
        }

    except Exception:

        logger.exception(
            "Itinerary generation failed"
        )

        raise