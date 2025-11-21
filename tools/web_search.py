"""
Web search tool for agents (real version using SerpAPI).
"""
import os
from typing import Annotated
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def web_search_tool(
    query: Annotated[str, "Search query to look up"]
) -> Annotated[str, "Search results"]:
    """Search the web for information using SerpAPI."""
    try:
        search = GoogleSearch({
            "q": query,
            "engine": "google",
            "api_key": SERPAPI_API_KEY,
            "num": 3
        })
        results = search.get_dict()

        snippets = []
        for i, r in enumerate(results.get("organic_results", [])[:3]):
            snippets.append(
                f"{i+1}. {r.get('title','')}\n{r.get('snippet','')}\nURL: {r.get('link','')}\n"
            )

        if not snippets:
            return f"No results found for '{query}'."

        return f'Search results for "{query}":\n\n' + "\n".join(snippets)

    except Exception as e:
        return f"Error while searching: {e}"
