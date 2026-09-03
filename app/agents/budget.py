from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)

from app.graph.state import TravelState
from app.llm.client import llm
from app.core.logging import get_logger


logger = get_logger(__name__)


def budget_agent(
    state: TravelState
):

    logger.info(
        "Budget agent started"
    )

    prompt = f"""
Analyze whether this trip is realistic.

User Query:
{state["user_query"]}

Trip Constraints:
{state.get("trip_constraints", {})}

Flight Results:
{state.get("flight_results", "")}

Hotel Results:
{state.get("hotel_results", "")}

Weather:
{state.get("weather_results", "")}

Provide:

1. Estimated costs
2. Budget risks
3. Money-saving suggestions
4. Overall feasibility

Clearly label approximate prices.
"""

    try:

        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a practical "
                        "travel budget analyst."
                    )
                ),
                HumanMessage(
                    content=prompt
                ),
            ]
        )

        return {
            "budget_results": response.content,
            "messages": [
                AIMessage(
                    content=(
                        "Budget assessment generated."
                    )
                )
            ],
            "llm_calls": (
                state.get("llm_calls", 0) + 1
            ),
        }

    except Exception:

        logger.exception(
            "Budget agent failed"
        )

        return {
            "budget_results": (
                "Budget analysis is "
                "temporarily unavailable."
            )
        }