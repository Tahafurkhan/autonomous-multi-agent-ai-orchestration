import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

_tavily_key = os.getenv("TAVILY_API_KEY") or ""
_tavily_key = _tavily_key.strip().strip('\"\'')
client = TavilyClient(api_key=_tavily_key)

def taily_search(query):
    response = client.search(query=query, max_results=5)
    results = []

    for i, result in enumerate(response["results"], 1):
        title = result.get("title", "unknown")
        url = result.get("url", " ")
        snippet = result.get("content"," ").snippet if result.get("content") else "No description available"

        results.append(f"{i}. Title: {title}\n   URL: {url}\n   Snippet: {snippet}\n")

    return "\n\n".join(results)
