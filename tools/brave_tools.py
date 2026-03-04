import os
import json
from datetime import datetime
from crewai.tools import tool
import requests


@tool("Brave Search for Market Context")
def search_market_context(query: str, days_back: int = 7) -> str:
    """
    Searches the web using Brave Search API to find recent news, macro-economic events,
    and market context related to the query.

    Args:
        query: A highly specific search query (e.g., 'FPT Vietnam earnings report 2024 macro impact')
        days_back: How many days back to search (default 7)

    Returns:
        A JSON string containing the top search results, including titles, URLs, and snippets.
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return "Error: BRAVE_API_KEY environment variable is not set."

    # Implement caching mechanism to avoid burning API limits (33/day)
    cache_dir = "data/raw/cache"
    os.makedirs(cache_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    cache_file = f"{cache_dir}/{query.replace(' ', '_')}_{today}.json"

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"Accept": "application/json", "X-Subscription-Token": api_key}

    # Calculate freshness based on days_back
    freshness = "pd" if days_back <= 1 else "pw" if days_back <= 7 else "pm"

    params = {
        "q": query,
        "freshness": freshness,
        "count": 10,  # Get top 10 results
        "search_lang": "vi",  # Prioritize Vietnamese context
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        # Extract meaningful results
        results = []
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "age": item.get("age", ""),
                    }
                )

        output_json = json.dumps(results, ensure_ascii=False, indent=2)

        # Save to cache
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(output_json)

        return output_json

    except Exception as e:
        return f"Error executing Brave Search: {str(e)}"
