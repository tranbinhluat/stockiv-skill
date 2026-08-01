import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from stockiv.config import paths  # noqa: E402
from tools.cache_tools import clean_expired_cache  # noqa: E402


def _age_file(path: Path, days: int) -> None:
    """Set both atime and mtime of `path` to `days` ago, so cache cleanup sees it as expired."""
    old_time = time.time() - (days * 86400)
    os.utime(path, (old_time, old_time))


def test_clean_expired_cache_preserves_scout_budget(monkeypatch, tmp_path):
    """
    scout_budget.json must survive cache cleanup even when its mtime makes it
    look expired. A regular aged .json file in the same dir MUST still be
    deleted — this proves the guard excludes only the budget file (no
    over-exclusion).
    """
    # Redirect RAW_CACHE_DIR to an isolated temp dir for the duration of the test.
    monkeypatch.setattr(paths, "RAW_CACHE_DIR", tmp_path)

    # 1. Budget file — aged beyond the threshold, must survive.
    budget_file = tmp_path / "scout_budget.json"
    budget_file.write_text('{"scopes": {}}', encoding="utf-8")
    _age_file(budget_file, days=30)

    # 2. Regular aged cache file — must be deleted.
    aged_cache = tmp_path / "old_query_2024-01-01.json"
    aged_cache.write_text('{"results": []}', encoding="utf-8")
    _age_file(aged_cache, days=30)

    # Run with a 14-day threshold — both seeded files are 30 days old.
    result = clean_expired_cache(days=14)

    # Budget survives.
    assert budget_file.exists(), (
        f"scout_budget.json was deleted by cache cleanup — guard failed.\n"
        f"clean_expired_cache returned: {result}"
    )
    # Budget content untouched.
    assert budget_file.read_text(encoding="utf-8") == '{"scopes": {}}'

    # Regular aged cache was deleted — no over-exclusion.
    assert not aged_cache.exists(), (
        f"Aged non-budget cache file was NOT deleted — guard may be over-excluding.\n"
        f"clean_expired_cache returned: {result}"
    )

    # Sanity: the function reported exactly 1 deletion.
    assert "Successfully deleted 1 expired cache files" in result
