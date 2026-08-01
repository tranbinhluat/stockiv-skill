import os
import time


def clean_expired_cache(days: int = 14) -> str:
    """
    Scans the local JSON cache directory and deletes files older than the specified number of days.
    Use this tool before running market queries to ensure stale cache data does not improperly feed the context.

    Args:
        days: The threshold in days (default: 14). Files older than this will be deleted.

    Returns:
        A string summarizing how many files were deleted and their paths.
    """
    # Imported inside the function so tests can monkeypatch stockiv.config.paths.RAW_CACHE_DIR
    # (a module-level binding would cache the old path and ignore the patch).
    from stockiv.config.paths import RAW_CACHE_DIR

    deleted_files = []

    if not RAW_CACHE_DIR.exists():
        return deleted_files

    current_time = time.time()
    threshold_seconds = days * 86400  # 24 * 60 * 60

    for file_path in RAW_CACHE_DIR.glob("*.json"):
        # Never delete the session budget file regardless of age — it owns state that
        # must survive cache cleanup. See tools/brave_tools.py:scout_search.
        if file_path.name == "scout_budget.json":
            continue
        if file_path.is_file():
            file_mtime = os.path.getmtime(file_path)
            age_seconds = current_time - file_mtime

            if age_seconds > threshold_seconds:
                try:
                    os.remove(file_path)
                    deleted_files.append(str(file_path))
                    print(
                        f"[CacheCleaner] Deleted expired cache file: {file_path.name}"
                    )
                except Exception as e:
                    print(f"[CacheCleaner] Failed to delete file {file_path}: {e}")

    return f"Successfully deleted {len(deleted_files)} expired cache files: {deleted_files}"
