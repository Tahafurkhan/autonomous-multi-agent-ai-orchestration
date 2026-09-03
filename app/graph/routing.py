from app.graph.state import TravelState
from app.utils.helpers import (
    AGENT_ORDER,
    selected_agents,
)


ROUTE_MAP = {
    "guardrail_blocked":
        "guardrail_blocked",

    "flight_agent":
        "flight_agent",

    "hotel_agent":
        "hotel_agent",

    "weather_agent":
        "weather_agent",

    "budget_agent":
        "budget_agent",

    "itinerary_agent":
        "itinerary_agent",
}


def route_from_supervisor(
    state: TravelState
) -> str:

    if not state.get(
        "guardrail_allowed",
        True
    ):
        return "guardrail_blocked"

    agents = selected_agents(
        state
    )

    return (
        agents[0]
        if agents
        else "itinerary_agent"
    )


def route_after_agent(
    current_agent: str
):

    def route(
        state: TravelState
    ) -> str:

        agents = selected_agents(
            state
        )

        current_index = (
            AGENT_ORDER.index(
                current_agent
            )
        )

        for agent in AGENT_ORDER[
            current_index + 1:
        ]:

            if agent in agents:
                return agent

        return "itinerary_agent"

    return route