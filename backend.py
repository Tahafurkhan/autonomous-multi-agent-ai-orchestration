import os
import certifi
from dotenv import load_dotenv


load_dotenv()

from typing import TypedDict, Annotated
import operator
import uuid

import psycopg
from psycopg.rows import DictRow

from langgraph.graph import StateGraph,START,END
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage


from langchain_groq import ChatGroq

from tools.flight_tool import search_flights
from tools.tavily_tool import taily_search

from langgraph.checkpoint.postgres import PostgresSaver




def get_database_url() -> str:
    """Retrieve the database URL from environment variables."""
    db_url = os.getenv("postgres_url")
    if not db_url:
        raise ValueError("Database URL not found in environment variables.")
    return db_url


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")


class Travelstate(TypedDict):
    """TypedDict entire agent state flow."""
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results:str
    hotel_results:str
    itinerary: str
    llm_calls:int

def flight_agents(state: Travelstate) -> Travelstate:
    """Flight search agent."""
    user_query = state["user_query"]
    flight_data = search_flights(user_query)
    return {"flight_results": flight_data, "messages": [AIMessage("Flight results fetched")], "llm_calls": state["llm_calls"] + 1}


def hotel_agents(state: Travelstate) -> Travelstate:
    """Hotel search agent."""
    user_query = state["user_query"]
    refined_query = f"Find best hotels in {user_query}"
    hotel_data = taily_search(refined_query)
    return {"hotel_results": hotel_data, "messages": [AIMessage("Hotel results fetched")], "llm_calls": state["llm_calls"] + 1}

def itinerary_agents(state: Travelstate) -> Travelstate:
    """Itinerary generation agent."""

    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

Combine all the above information to create a detailed travel itinerary for the user.
"""

    # Your LLM call goes here
    response = llm.invoke([SystemMessage(content="You are an expert travel planner."), HumanMessage(content=prompt)])

    return {"itinerary": response.content, "messages": [response], "llm_calls": state["llm_calls"] + 1}


def final_agent (state: Travelstate) -> Travelstate:
    """Final agent to summarize and present the itinerary."""
    final_prompt = f"""
Generate the final travel response for the user.

User Request:
{state['user_query']}

Flights:
{state.get('flight_results', '')}

Hotels:
{state.get('hotel_results', '')}


Draft Itinerary:
{state.get('itinerary', '')}

Format the final answer beautifully using these sections:
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight APIs may not provide ticket prices when pricing is unavailable.
- Include weather-based travel advice.
- Keep the response useful for real travel planning.
- Provide the final recommendations in a concise and actionable manner.

"""
     
    # Your LLM call goes here
    response = llm.invoke([SystemMessage(content="You are a professional travel planner agent."), HumanMessage(content=final_prompt)])

    return { "messages": [response], "llm_calls": state["llm_calls"] + 1}


# Build the state graph

graph = StateGraph(Travelstate)
graph.add_node("flight_search", flight_agents)
graph.add_node("hotel_search", hotel_agents)
graph.add_node("itinerary_generation", itinerary_agents)
graph.add_node("final_summary", final_agent)

graph.add_edge(START, "flight_search")
graph.add_edge("flight_search", "hotel_search")
graph.add_edge("hotel_search", "itinerary_generation")
graph.add_edge("itinerary_generation", "final_summary")
graph.add_edge("final_summary", END)


# Checkpoint postgres

DATABASE_URL = get_database_url()
_Conn = None
checkpointer = None
try:
    _Conn = psycopg.connect(DATABASE_URL, autocommit=True, row_factory=DictRow)
    checkpointer = PostgresSaver(_Conn)
    checkpointer.setup()
except Exception as e:
    import warnings

    warnings.warn(f"Database connection/setup failed: {e}. Continuing without checkpointing.")

travel_graph = graph.compile(checkpointer=checkpointer)


def run_travel_agent(user_query: str, thread_id: str | None = None) -> Travelstate:
    """Main function to run the travel agent."""

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable":{"thread_id": thread_id}}
      

    result = travel_graph.invoke (
        {
         "messages":[HumanMessage(content=user_query)],
         "user_query": user_query, 
         "flight_results": "",
         "hotel_results": "",  
         "itinerary": "",
         "llm_calls": 0
        },config=config
    )

    final_answer = result["messages"][-1].content if result["messages"] else "No response generated."

    return {
        "thread_id": thread_id, 
        "answer": final_answer,
        "llm_calls": result["llm_calls"],
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", "")    
    }

