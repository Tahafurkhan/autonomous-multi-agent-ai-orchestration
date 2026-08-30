import os
import re

import airportsdata
import requests
from dotenv import load_dotenv


load_dotenv()

# Accept common env var names (typos in .env are common). Strip surrounding quotes.
_api_key = os.getenv("AVIATION_API_KEY") or os.getenv("AVIATTIONSATCK_API_KEY") or os.getenv("AVIATIONSTACK_API_KEY")
if _api_key:
    _api_key = _api_key.strip().strip('"\'')
API_KEY = _api_key

BASE_URL = "https://aviationstack.com/api/v1/flights"

AIRPORTS = airportsdata.load("IATA")


def get_airport_code(value):
    """Find an IATA airport code from a city, airport, or IATA code."""

    if not value:
        return None

    value = value.strip().lower()

    # Direct IATA code
    if len(value) == 3:
        for iata, airport in AIRPORTS.items():
            if iata.lower() == value:
                return iata

    # City or airport name
    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower()
        name = str(airport.get("name", "")).lower()

        if value == city or value == name:
            return iata

    return None


def find_country_airport(country):
    """Find a commonly used airport for a country."""

    country = country.lower().strip()

    country_airports = {
        "india": "DEL",
        "japan": "NRT",
        "united states": "JFK",
        "usa": "JFK",
        "uk": "LHR",
        "united kingdom": "LHR",
        "france": "CDG",
        "germany": "FRA",
        "italy": "FCO",
        "spain": "MAD",
        "singapore": "SIN",
        "thailand": "BKK",
        "uae": "DXB",
        "dubai": "DXB",
        "australia": "SYD",
        "canada": "YYZ",
    }

    return country_airports.get(country)


def extract_locations(query):
    """
    Extract origin and destination from natural language.

    Examples:
        "trip from india to japan"
        "flights from Delhi to Tokyo"
        "travel from Mumbai to Dubai"
    """

    query = query.lower().strip()

    match = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\s+for\s+|\s+on\s+|\s*$)",
        query,
    )

    if not match:
        return None, None

    origin = match.group(1).strip()
    destination = match.group(2).strip()

    return origin, destination


def resolve_location(value):
    """Resolve a location to an airport IATA code."""

    if not value:
        return None

    # Try country first
    airport = find_country_airport(value)

    if airport:
        return airport

    # Try airport/city
    return get_airport_code(value)


def search_flights(query, limit=10):
    """
    Search flights using a natural-language query.

    Example:
        search_flights("plan 7 days to japan trip from india")
    """

    if not API_KEY:
        return {
            "success": False,
            "error": (
                "AVIATION API key missing. Set AVIATION_API_KEY in your .env "
                "(or fix the variable name if it is misspelled, e.g. AVIATTIONSATCK_API_KEY)."
            ),
        }

    if not query or not isinstance(query, str):
        return {
            "success": False,
            "error": "Please provide a valid flight search request",
        }

    origin, destination = extract_locations(query)

    if not origin or not destination:
        return {
            "success": False,
            "error": (
                "Could not understand the flight route. "
                "Please specify something like "
                "'flights from India to Japan'."
            ),
        }

    origin_code = resolve_location(origin)
    destination_code = resolve_location(destination)

    if not origin_code:
        return {
            "success": False,
            "error": f"Could not find airport for '{origin}'",
        }

    if not destination_code:
        return {
            "success": False,
            "error": f"Could not find airport for '{destination}'",
        }

    params = {
        "access_key": API_KEY,
        "dep_iata": origin_code,
        "arr_iata": destination_code,
        "limit": min(limit, 100),
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            return {
                "success": False,
                "error": data["error"].get("message", "Flight API error"),
            }

        flights = data.get("data", [])
        if not flights:
            return {
                "success": False,
                "error": "No live flights returned by the API for this route/date.",
                "origin": origin_code,
                "destination": destination_code,
                "flights": [],
            }

        return {
            "success": True,
            "origin": origin_code,
            "destination": destination_code,
            "flights": flights,
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": str(error),
        }

