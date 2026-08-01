import os
import json
import re
import tempfile
from datetime import datetime
import requests
from dotenv import load_dotenv


load_dotenv()

SESSION_BRAVE_BUDGET = 3


def search_market_context(query: str, days_back: int = 7) -> str:
    """
    Searches the web using Brave Search API to find recent news, macro-economic events,
    and market context related to the query.

    Thin budget-free wrapper around `_brave_search`. Kept for legacy callers
    (e.g. tools/report_finder_tools.py, src/stockiv/cli.py) that must not be
    affected by the session budget.

    Args:
        query: A highly specific search query (e.g., 'FPT Vietnam earnings report 2024 macro impact')
        days_back: How many days back to search (default 7)

    Returns:
        A Markdown string containing the top search results.
    """
    return _brave_search(query, days_back)[0]


def _brave_search(query: str, days_back: int = 7) -> tuple[str, bool, bool]:
    """
    Execute a Brave Search (with 7-day TTL cache), returning rich status flags.

    Returns:
        (markdown, from_cache, api_attempted)
          - cache hit            -> (md, True,  False)
          - API attempted        -> (md, False, True)   (any HTTP outcome, incl. exception)
          - missing API key      -> (error_md, False, False)  (early return, no HTTP)
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return ("Error: BRAVE_API_KEY environment variable is not set.", False, False)

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
                return (_format_to_markdown(query, raw_results), True, False)
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

        return (_format_to_markdown(query, results), False, True)

    except Exception as e:
        return (f"Error executing Brave Search: {str(e)}", False, True)


def _format_to_markdown(query: str, results: list[dict]) -> str:
    """Formats raw search results into a clean, LLM-friendly Markdown string."""
    if not results:
        return f'### Search Results for: "{query}"\nNo results found.'

    md = [f'### Search Results for: "{query}"']
    for item in results:
        title = item.get("title", "No Title")
        url = item.get("url", "#")
        snippet = item.get("snippet", "").strip()
        age = item.get("age", "recent")

        md.append(f"*   **[{title}]({url})** (published: {age})")
        if snippet:
            indented_snippet = "\n".join(
                f"    > {line}" for line in snippet.split("\n")
            )
            md.append(indented_snippet)

    return "\n".join(md)


# ---------------------------------------------------------------------------
# Session budget engine
# ---------------------------------------------------------------------------


def _budget_file_path():
    """Return the path to scout_budget.json. Imported inside so tests can monkeypatch."""
    from stockiv.config.paths import RAW_CACHE_DIR

    return RAW_CACHE_DIR / "scout_budget.json"


def _load_budget() -> dict:
    """Load the budget file, tolerating missing/corrupt files by returning a fresh shell."""
    try:
        path = _budget_file_path()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "scopes" not in data:
            return {"scopes": {}}
        return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"scopes": {}}


def _atomic_write_budget(data: dict) -> None:
    """Atomically write the budget file via tmp + os.replace."""
    path = _budget_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix="scout_budget_", suffix=".json", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_name, path)
    except Exception:
        # Best-effort cleanup of the tmp file if something went wrong.
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _fresh_scope_record() -> dict:
    return {
        "budget": SESSION_BRAVE_BUDGET,
        "used": 0,
        "session_started": datetime.now().isoformat(),
        "queries": [],
        "resets": [],
    }


def reset_budget(scope: str) -> dict:
    """
    Reset a scope's budget to a fresh record. Appends an audit timestamp to
    `resets`. Atomic write. Returns the new record.
    """
    data = _load_budget()
    record = _fresh_scope_record()
    record["resets"].append(datetime.now().isoformat())
    data.setdefault("scopes", {})[scope] = record
    _atomic_write_budget(data)
    return record


def budget_status(scope: str) -> dict:
    """
    Return a status summary for a scope. Auto-initializes a fresh zero record
    if the scope is missing (no reset required before first use).
    """
    data = _load_budget()
    scopes = data.setdefault("scopes", {})
    record = scopes.get(scope)
    if record is None:
        record = _fresh_scope_record()
        scopes[scope] = record
        _atomic_write_budget(data)
    used = record.get("used", 0)
    budget = record.get("budget", SESSION_BRAVE_BUDGET)
    return {
        "scope": scope,
        "used": used,
        "remaining": max(0, budget - used),
        "queries_used": record.get("queries", []),
    }


def scout_search(query: str, scope: str, days_back: int = 7) -> tuple[str, dict]:
    """
    Budget-aware Brave search. Decrements the session budget only when an actual
    HTTP API call is attempted (cache hits and missing-key are free).

    Returns:
        (markdown, status_dict)
        - exhausted -> ("", {"status": "exhausted", ...}) with NO HTTP call
        - ok        -> (markdown, {"status": "ok", "cache_hit": bool, ...})
    """
    data = _load_budget()
    scopes = data.setdefault("scopes", {})
    record = scopes.get(scope)
    if record is None:
        record = _fresh_scope_record()
        scopes[scope] = record

    used = record.get("used", 0)
    budget = record.get("budget", SESSION_BRAVE_BUDGET)
    queries_used = record.get("queries", [])

    if used >= budget:
        return (
            "",
            {
                "status": "exhausted",
                "scope": scope,
                "used": used,
                "remaining": 0,
                "queries_used": queries_used,
                "directive": "Switch to websearch/webfetch for remaining critical topics (max 2).",
            },
        )

    markdown, from_cache, api_attempted = _brave_search(query, days_back=days_back)

    queries_used = record.setdefault("queries", [])
    queries_used.append(
        {
            "q": query,
            "ts": datetime.now().isoformat(),
            "cache_hit": from_cache,
        }
    )
    if api_attempted:
        record["used"] = used + 1

    _atomic_write_budget(data)

    return (
        markdown,
        {
            "status": "ok",
            "scope": scope,
            "used": record["used"],
            "remaining": max(0, budget - record["used"]),
            "cache_hit": from_cache,
        },
    )
