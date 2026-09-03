from typing import Any


AGENT_ORDER = [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
]


KNOWN_AGENTS = set(AGENT_ORDER)


def empty_constraints() -> dict[str, Any]:

    return {
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": [],
    }


def selected_agents(
    state
) -> list[str]:

    selected = state.get(
        "selected_agents",
        []
    )

    return [
        agent
        for agent in AGENT_ORDER
        if agent in selected
    ]