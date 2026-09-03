import uuid

from langchain_core.messages import (
    HumanMessage,
)
from langgraph.types import Command

from app.graph.workflow import travel_graph
from app.graph.state import TravelState
from app.utils.helpers import empty_constraints
from app.core.logging import get_logger


logger = get_logger(__name__)


def _interrupt_payload(result):

    interrupts = result.get(
        "__interrupt__",
        []
    )

    if not interrupts:
        return None

    first = interrupts[0]

    payload = getattr(
        first,
        "value",
        first
    )

    if isinstance(
        payload,
        dict
    ):
        return payload

    return {
        "value": payload
    }


def serialize_result(
    result,
    thread_id
):

    interrupt = _interrupt_payload(
        result
    )

    draft = ""

    if interrupt:
        draft = interrupt.get(
            "draft_itinerary",
            ""
        )

    if not draft:
        draft = result.get(
            "itinerary",
            ""
        )

    return {
        "thread_id":
            thread_id,

        "answer":
            result.get(
                "final_response"
            ) or draft or "",

        "itinerary":
            draft,

        "draft_itinerary":
            draft,

        "requires_approval":
            interrupt is not None,

        "approval_request":
            (
                interrupt.get(
                    "approval_request",
                    ""
                )
                if interrupt
                else result.get(
                    "approval_request",
                    ""
                )
            ),

        "interrupt":
            interrupt,

        "selected_agents":
            result.get(
                "selected_agents",
                []
            ),

        "trip_constraints":
            result.get(
                "trip_constraints",
                {}
            ),

        "supervisor_reasoning":
            result.get(
                "supervisor_reasoning",
                ""
            ),

        "guardrail_allowed":
            result.get(
                "guardrail_allowed",
                True
            ),

        "approved":
            result.get(
                "approved"
            ),

        "human_feedback":
            result.get(
                "human_feedback",
                ""
            ),

        "flight_results":
            result.get(
                "flight_results",
                ""
            ),

        "hotel_results":
            result.get(
                "hotel_results",
                ""
            ),

        "weather_results":
            result.get(
                "weather_results",
                ""
            ),

        "budget_results":
            result.get(
                "budget_results",
                ""
            ),

        "llm_calls":
            result.get(
                "llm_calls",
                0
            ),
    }


def run_travel_agent(
    user_input: str,
    thread_id: str | None = None,
):

    if not thread_id:
        thread_id = (
            f"user_{uuid.uuid4().hex}"
        )

    logger.info(
        "Starting travel workflow thread=%s",
        thread_id
    )

    config = {
        "configurable": {
            "thread_id":
                thread_id
        }
    }

    initial_state: TravelState = {

        "messages": [
            HumanMessage(
                content=user_input
            )
        ],

        "user_query":
            user_input,

        "guardrail_allowed":
            True,

        "guardrail_reason":
            "",

        "selected_agents":
            [],

        "trip_constraints":
            empty_constraints(),

        "supervisor_reasoning":
            "",

        "flight_results":
            "",

        "hotel_results":
            "",

        "weather_results":
            "",

        "budget_results":
            "",

        "itinerary":
            "",

        "approval_request":
            "",

        "approved":
            False,

        "human_feedback":
            "",

        "final_response":
            "",

        "llm_calls":
            0,
    }

    try:

        result = travel_graph.invoke(
            initial_state,
            config=config
        )

        logger.info(
            "Travel workflow completed thread=%s",
            thread_id
        )

        return serialize_result(
            result,
            thread_id
        )

    except Exception:

        logger.exception(
            "Travel workflow failed thread=%s",
            thread_id
        )

        raise


def resume_travel_agent(
    thread_id: str,
    approved: bool,
    feedback: str = "",
):

    logger.info(
        "Resuming travel workflow thread=%s approved=%s",
        thread_id,
        approved
    )

    config = {
        "configurable": {
            "thread_id":
                thread_id
        }
    }

    try:

        result = travel_graph.invoke(
            Command(
                resume={
                    "approved":
                        approved,

                    "feedback":
                        feedback.strip(),
                }
            ),
            config=config
        )

        return serialize_result(
            result,
            thread_id
        )

    except Exception:

        logger.exception(
            "Workflow resume failed thread=%s",
            thread_id
        )

        raise