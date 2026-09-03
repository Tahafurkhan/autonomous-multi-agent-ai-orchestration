from langchain_core.messages import AIMessage

from app.graph.state import TravelState
from app.llm.prompts import (
    llm_text,
    json_from_llm,
)
from app.utils.helpers import (
    AGENT_ORDER,
    KNOWN_AGENTS,
    empty_constraints,
)
from app.core.logging import get_logger


logger = get_logger(__name__)


def supervisor_agent(
    state: TravelState
):

    query = state["user_query"]

    logger.info(
        "Supervisor started"
    )

    # -------------------------
    # Guardrail
    # -------------------------

    guardrail_prompt = f"""
Determine whether the following request belongs
to travel planning or travel information.

Valid requests include:

- destinations
- flights
- hotels
- weather
- budgets
- transportation
- sightseeing
- food
- packing
- itineraries

Block clearly unrelated or harmful requests.

Return strict JSON:

{{
    "allowed": true,
    "reason": ""
}}

User request:
{query}
"""

    try:

        raw = llm_text(
            "You are a travel application guardrail.",
            guardrail_prompt
        )

        result = json_from_llm(raw)

        allowed = bool(
            result.get("allowed", True)
        )

        reason = str(
            result.get("reason", "")
        )

    except Exception:

        logger.exception(
            "Guardrail processing failed"
        )

        allowed = True
        reason = (
            "Guardrail fallback allowed request."
        )

    if not allowed:

        logger.warning(
            "Request blocked by guardrail"
        )

        return {
            "guardrail_allowed": False,
            "guardrail_reason": reason,
            "selected_agents": [],
            "trip_constraints": empty_constraints(),
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [
                AIMessage(
                    content=reason
                )
            ],
        }

    # -------------------------
    # Agent routing
    # -------------------------

    supervisor_prompt = f"""
You are the supervisor of a multi-agent
travel planning system.

Available agents:

flight_agent
hotel_agent
weather_agent
budget_agent
itinerary_agent

Select only the agents required.

itinerary_agent must always be selected.

Return strict JSON:

{{
    "selected_agents": [],
    "trip_constraints": {{
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": []
    }},
    "reasoning": ""
}}

User request:
{query}
"""

    try:

        raw = llm_text(
            "You are the TripMate supervisor.",
            supervisor_prompt
        )

        result = json_from_llm(raw)

        requested_agents = result.get(
            "selected_agents",
            []
        )

        selected = [
            agent
            for agent in AGENT_ORDER
            if agent in requested_agents
            and agent in KNOWN_AGENTS
        ]

        if "itinerary_agent" not in selected:
            selected.append(
                "itinerary_agent"
            )

        constraints = empty_constraints()

        parsed_constraints = result.get(
            "trip_constraints",
            {}
        )

        if isinstance(
            parsed_constraints,
            dict
        ):
            constraints.update(
                parsed_constraints
            )

        reasoning = str(
            result.get(
                "reasoning",
                ""
            )
        )

        logger.info(
            "Supervisor selected agents=%s",
            selected
        )

    except Exception:

        logger.exception(
            "Supervisor routing failed"
        )

        selected = AGENT_ORDER.copy()
        constraints = empty_constraints()

        reasoning = (
            "Supervisor failed. "
            "Full workflow selected."
        )

    return {
        "guardrail_allowed": True,
        "guardrail_reason": reason,
        "selected_agents": selected,
        "trip_constraints": constraints,
        "supervisor_reasoning": reasoning,
        "messages": [
            AIMessage(
                content=(
                    "Supervisor created "
                    "the agent plan."
                )
            )
        ],
    }