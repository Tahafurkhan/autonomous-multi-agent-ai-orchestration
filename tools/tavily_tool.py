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
        content = result.get("content")
        if content:
            if isinstance(content, dict):
                snippet = content.get("snippet") or content.get("text") or str(content)
            elif hasattr(content, "snippet"):
                snippet = getattr(content, "snippet")
            else:
                snippet = str(content)
        else:
            snippet = "No description available"

        results.append(f"{i}. Title: {title}\n   URL: {url}\n   Snippet: {snippet}\n")

    return "\n\n".join(results)
