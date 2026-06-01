import os
import json
import re
from datetime import datetime
import requests


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
    from stockiv.config.paths import RAW_CACHE_DIR

    safe_query = re.sub(r"[^a-zA-Z0-9_\-]", "_", query)
    if len(safe_query) > 150:
        safe_query = safe_query[:150]

    # Look for existing cache file within 7 days TTL
    found_cache = None
    for cache_path in RAW_CACHE_DIR.glob(f"{safe_query}_*.json"):
        filename = cache_path.name
        date_str = filename.replace(f"{safe_query}_", "").replace(".json", "")
        try:
            cache_date = datetime.strptime(date_str, "%Y-%m-%d")
            if (datetime.now() - cache_date).days < 7:
                found_cache = cache_path
                break
        except ValueError:
            pass

    if found_cache:
        try:
            with open(found_cache, "r", encoding="utf-8") as f:
                raw_results = json.load(f)
                return _format_to_markdown(query, raw_results)
        except Exception:
            pass

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

        # Save to cache
        today = datetime.now().strftime("%Y-%m-%d")
        cache_file = RAW_CACHE_DIR / f"{safe_query}_{today}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return _format_to_markdown(query, results)

    except Exception as e:
        return f"Error executing Brave Search: {str(e)}"


def _format_to_markdown(query: str, results: list[dict]) -> str:
    """Formats raw search results into a clean, LLM-friendly Markdown string."""
    if not results:
        return f"### Search Results for: \"{query}\"\nNo results found."

    md = [f"### Search Results for: \"{query}\""]
    for item in results:
        title = item.get("title", "No Title")
        url = item.get("url", "#")
        snippet = item.get("snippet", "").strip()
        age = item.get("age", "recent")

        md.append(f"*   **[{title}]({url})** (published: {age})")
        if snippet:
            indented_snippet = "\n".join(f"    > {line}" for line in snippet.split("\n"))
            md.append(indented_snippet)

    return "\n".join(md)

