from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.checkpoint.postgres import (
    PostgresSaver,
)

from app.graph.state import TravelState
from app.graph.routing import (
    ROUTE_MAP,
    route_from_supervisor,
    route_after_agent,
)

from app.agents.supervisor import (
    supervisor_agent,
)

from app.agents.flight import (
    flight_agent,
)

from app.agents.hotel import (
    hotel_agent,
)

from app.agents.weather import (
    weather_agent,
)

from app.agents.budget import (
    budget_agent,
)

from app.agents.itinerary import (
    itinerary_agent,
)

from app.agents.human_approval import (
    human_approval_agent,
)

from app.agents.final import (
    final_agent,
)

from app.core.logging import get_logger
from app.database.postgres import (
    get_checkpointer,
)


logger = get_logger(__name__)


def build_graph():

    graph = StateGraph(
        TravelState
    )

    graph.add_node(
        "supervisor",
        supervisor_agent
    )

    graph.add_node(
        "guardrail_blocked",
        lambda state: {
            "final_response":
                state.get(
                    "guardrail_reason",
                    "Request blocked."
                )
        }
    )

    graph.add_node(
        "flight_agent",
        flight_agent
    )

    graph.add_node(
        "hotel_agent",
        hotel_agent
    )

    graph.add_node(
        "weather_agent",
        weather_agent
    )

    graph.add_node(
        "budget_agent",
        budget_agent
    )

    graph.add_node(
        "itinerary_agent",
        itinerary_agent
    )

    graph.add_node(
        "human_approval",
        human_approval_agent
    )

    graph.add_node(
        "final_agent",
        final_agent
    )

    graph.add_edge(
        START,
        "supervisor"
    )

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        ROUTE_MAP
    )

    graph.add_conditional_edges(
        "flight_agent",
        route_after_agent(
            "flight_agent"
        ),
        ROUTE_MAP
    )

    graph.add_conditional_edges(
        "hotel_agent",
        route_after_agent(
            "hotel_agent"
        ),
        ROUTE_MAP
    )

    graph.add_conditional_edges(
        "weather_agent",
        route_after_agent(
            "weather_agent"
        ),
        ROUTE_MAP
    )

    graph.add_conditional_edges(
        "budget_agent",
        route_after_agent(
            "budget_agent"
        ),
        ROUTE_MAP
    )

    graph.add_edge(
        "itinerary_agent",
        "human_approval"
    )

    graph.add_edge(
        "human_approval",
        "final_agent"
    )

    graph.add_edge(
        "final_agent",
        END
    )

    graph.add_edge(
        "guardrail_blocked",
        END
    )

    checkpointer = get_checkpointer()

    return graph.compile(
        checkpointer=checkpointer
    )


travel_graph = build_graph()