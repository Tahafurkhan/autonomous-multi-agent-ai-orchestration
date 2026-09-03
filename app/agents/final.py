from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)

from app.graph.state import TravelState
from app.llm.client import llm
from app.core.logging import get_logger


logger = get_logger(__name__)


def final_agent(
    state: TravelState
):

    logger.info(
        "Final agent started"
    )

    if state.get("approved"):

        review = (
            "The user approved the draft. "
            "Preserve the decisions and "
            "polish the response."
        )

    else:

        review = f"""
The user requested a revision.

Feedback:
{state.get("human_feedback", "")}
"""

    prompt = f"""
Generate the final travel response.

User:
{state["user_query"]}

Review:
{review}

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

Draft:
{state.get("itinerary", "")}

Use these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Weather Information
5. Day-by-Day Itinerary
6. Estimated Budget
7. Final Recommendations

Clearly distinguish live information
from estimates.
"""

    try:

        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a professional "
                        "AI travel assistant."
                    )
                ),
                HumanMessage(
                    content=prompt
                ),
            ]
        )

        return {
            "final_response":
                response.content,

            "messages": [
                AIMessage(
                    content=response.content
                )
            ],

            "llm_calls":
                state.get(
                    "llm_calls",
                    0
                ) + 1,
        }

    except Exception:

        logger.exception(
            "Final response generation failed"
        )

        raise