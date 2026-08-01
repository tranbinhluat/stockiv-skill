import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import brave_tools  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    """Point RAW_CACHE_DIR at tmp_path for the duration of the test."""
    import stockiv.config.paths as paths

    monkeypatch.setattr(paths, "RAW_CACHE_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def fake_brave_json():
    return {
        "web": {
            "results": [
                {
                    "title": "FPT posts record profit",
                    "url": "https://example.com/fpt",
                    "description": "FPT Corporation reported record profit.",
                    "age": "2h",
                },
                {
                    "title": "VN-INDEX rises",
                    "url": "https://example.com/vnindex",
                    "description": "VN-INDEX closed higher on strong breadth.",
                    "age": "1d",
                },
            ]
        }
    }


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _mock_get_ok(fake_json):
    """Return a callable that makes requests.get return fake_json."""
    return lambda *a, **k: _FakeResponse(fake_json)


def _seed_cache(cache_dir, query, results=None):
    """Write a fresh cache file for `query` dated today (within 7-day TTL)."""
    if results is None:
        results = [
            {
                "title": "cached",
                "url": "https://cached.example",
                "snippet": "x",
                "age": "1d",
            }
        ]
    safe_query = "".join(c if c.isalnum() or c in "-_" else "_" for c in query)
    today = datetime.now().strftime("%Y-%m-%d")
    p = cache_dir / f"{safe_query}_{today}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(results, f)
    return p


# ---------------------------------------------------------------------------
# 1. Characterization
# ---------------------------------------------------------------------------


def test_characterization_search_market_context_returns_str(cache_dir, monkeypatch):
    """Characterization: search_market_context returns a str containing the markdown header."""
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(
        brave_tools.requests,
        "get",
        lambda *a, **k: _FakeResponse({"web": {"results": []}}),
    )
    result = brave_tools.search_market_context("test query", days_back=7)
    assert isinstance(result, str)
    assert "### Search Results for:" in result


# ---------------------------------------------------------------------------
# 2. Real API call increments used
# ---------------------------------------------------------------------------


def test_real_api_call_increments_used(cache_dir, fake_brave_json, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))
    md, status = brave_tools.scout_search("FPT earnings", scope="macro")
    assert status["status"] == "ok"
    assert status["used"] == 1
    assert status["remaining"] == 2
    assert status["cache_hit"] is False
    assert "### Search Results for:" in md


# ---------------------------------------------------------------------------
# 3. Cache hit does NOT increment used
# ---------------------------------------------------------------------------


def test_cache_hit_does_not_increment_used(cache_dir, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    called = {"n": 0}

    def _get(*a, **k):
        called["n"] += 1
        return _FakeResponse({"web": {"results": []}})

    monkeypatch.setattr(brave_tools.requests, "get", _get)
    _seed_cache(cache_dir, "FPT earnings")

    md, status = brave_tools.scout_search("FPT earnings", scope="macro")
    assert status["status"] == "ok"
    assert status["used"] == 0
    assert status["cache_hit"] is True
    assert called["n"] == 0


# ---------------------------------------------------------------------------
# 4. Exhaustion on 4th call
# ---------------------------------------------------------------------------


def test_exhaustion_on_fourth_call(cache_dir, fake_brave_json, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))
    for i in range(3):
        md, status = brave_tools.scout_search(f"q{i}", scope="macro")
        assert status["status"] == "ok"
    assert brave_tools.budget_status("macro")["remaining"] == 0

    called = {"n": 0}

    def _get(*a, **k):
        called["n"] += 1
        return _FakeResponse({"web": {"results": []}})

    monkeypatch.setattr(brave_tools.requests, "get", _get)
    md, status = brave_tools.scout_search("q3", scope="macro")
    assert status["status"] == "exhausted"
    assert status["used"] == 3
    assert status["remaining"] == 0
    assert md == ""
    assert "directive" in status
    assert len(status["queries_used"]) == 3
    assert called["n"] == 0


# ---------------------------------------------------------------------------
# 5. reset_budget restores used=0 and appends audit entry
# ---------------------------------------------------------------------------


def test_reset_budget_restores_used_and_appends_audit(
    cache_dir, fake_brave_json, monkeypatch
):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))
    brave_tools.scout_search("q1", scope="macro")
    brave_tools.scout_search("q2", scope="macro")
    assert brave_tools.budget_status("macro")["used"] == 2

    record = brave_tools.reset_budget("macro")
    assert record["used"] == 0
    assert len(record["resets"]) == 1
    assert brave_tools.budget_status("macro")["used"] == 0
    assert brave_tools.budget_status("macro")["remaining"] == 3


# ---------------------------------------------------------------------------
# 6. budget_status fields correct
# ---------------------------------------------------------------------------


def test_budget_status_fields(cache_dir, fake_brave_json, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))
    status = brave_tools.budget_status("fresh")
    assert set(status.keys()) == {"scope", "used", "remaining", "queries_used"}
    assert status["scope"] == "fresh"
    assert status["used"] == 0
    assert status["remaining"] == 3
    assert status["queries_used"] == []

    brave_tools.scout_search("q1", scope="fresh")
    status = brave_tools.budget_status("fresh")
    assert status["used"] == 1
    assert status["remaining"] == 2
    assert len(status["queries_used"]) == 1
    assert status["queries_used"][0]["q"] == "q1"


# ---------------------------------------------------------------------------
# 7. Corrupt budget file tolerated
# ---------------------------------------------------------------------------


def test_corrupt_budget_file_tolerated(cache_dir, monkeypatch):
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "scout_budget.json").write_text("{not valid json", encoding="utf-8")
    status = brave_tools.budget_status("macro")
    assert status["used"] == 0
    assert status["remaining"] == 3


# ---------------------------------------------------------------------------
# 8. requests.get raising -> used increments + error markdown
# ---------------------------------------------------------------------------


def test_requests_get_raising_increments_used(cache_dir, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")

    def _raise(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr(brave_tools.requests, "get", _raise)
    md, status = brave_tools.scout_search("q1", scope="macro")
    assert status["status"] == "ok"
    assert status["used"] == 1
    assert "Error executing Brave Search" in md


# ---------------------------------------------------------------------------
# 9. Missing API key -> used NOT incremented
# ---------------------------------------------------------------------------


def test_missing_api_key_does_not_increment_used(cache_dir, monkeypatch):
    # load_dotenv() at import does NOT override already-set env vars, so an
    # empty string stays falsy and exercises the missing-key path.
    monkeypatch.setenv("BRAVE_API_KEY", "")
    called = {"n": 0}

    def _get(*a, **k):
        called["n"] += 1
        return _FakeResponse({"web": {"results": []}})

    monkeypatch.setattr(brave_tools.requests, "get", _get)
    md, status = brave_tools.scout_search("q1", scope="macro")
    assert status["status"] == "ok"
    assert status["used"] == 0
    assert "BRAVE_API_KEY" in md
    assert called["n"] == 0


# ---------------------------------------------------------------------------
# 10. Budget file is valid JSON after every op
# ---------------------------------------------------------------------------


def test_budget_file_valid_json_after_every_op(cache_dir, fake_brave_json, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))

    def _read_json():
        with open(cache_dir / "scout_budget.json", "r", encoding="utf-8") as f:
            return json.load(f)

    brave_tools.scout_search("q1", scope="macro")
    _read_json()
    brave_tools.budget_status("macro")
    _read_json()
    brave_tools.reset_budget("macro")
    _read_json()
    brave_tools.budget_status("other")
    data = _read_json()
    assert "scopes" in data
    assert "macro" in data["scopes"]
    assert "other" in data["scopes"]


# ---------------------------------------------------------------------------
# 11. Per-scope isolation
# ---------------------------------------------------------------------------


def test_per_scope_isolation(cache_dir, fake_brave_json, monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))
    for i in range(3):
        brave_tools.scout_search(f"a{i}", scope="A")
    assert brave_tools.budget_status("A")["remaining"] == 0

    status_b = brave_tools.budget_status("B")
    assert status_b["remaining"] == 3
    assert status_b["used"] == 0

    md, status = brave_tools.scout_search("b0", scope="B")
    assert status["status"] == "ok"
    assert status["used"] == 1
    assert "### Search Results for:" in md
    assert brave_tools.budget_status("A")["remaining"] == 0


# ---------------------------------------------------------------------------
# 12. CLI exhaustion e2e (mocked, no API burn)
# ---------------------------------------------------------------------------


def test_cli_scout_exhaustion_e2e(cache_dir, fake_brave_json, monkeypatch, capsys):
    """Drive `stockiv.cli.scout` four times; the 4th must report exhausted, exit 0."""
    import stockiv.cli

    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(brave_tools.requests, "get", _mock_get_ok(fake_brave_json))

    for i in range(3):
        stockiv.cli.scout(["--scope", "E2E_MOCK", "--query", f"q{i}"])
        out = capsys.readouterr().out
        assert "BUDGET:" in out

    with pytest.raises(SystemExit) as exc_info:
        stockiv.cli.scout(["--scope", "E2E_MOCK", "--query", "q3"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert '"status": "exhausted"' in out
    assert "directive" in out
