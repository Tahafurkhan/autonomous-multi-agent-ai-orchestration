from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from app.graph.state import TravelState
from app.core.logging import get_logger


logger = get_logger(__name__)


def human_approval_agent(
    state: TravelState
):

    draft = state.get(
        "itinerary",
        ""
    )

    logger.info(
        "Waiting for human approval"
    )

    if not state.get(
        "approved",
        False
    ):

        payload = {
            "question":
                "Do you approve this draft itinerary?",

            "approval_request":
                state.get(
                    "approval_request",
                    "Please review the itinerary."
                ),

            "draft_itinerary":
                draft,

            "selected_agents":
                state.get(
                    "selected_agents",
                    []
                ),

            "supervisor_reasoning":
                state.get(
                    "supervisor_reasoning",
                    ""
                ),
        }

        response = interrupt(
            payload
        )

        approved = bool(
            response.get(
                "approved",
                False
            )
        )

        feedback = str(
            response.get(
                "feedback",
                ""
            )
        )

    else:

        approved = True

        feedback = state.get(
            "human_feedback",
            ""
        )

    logger.info(
        "Human approval completed approved=%s",
        approved
    )

    return {
        "approved": approved,
        "human_feedback": feedback,
        "messages": [
            AIMessage(
                content=(
                    "Human review completed."
                )
            )
        ],
    }