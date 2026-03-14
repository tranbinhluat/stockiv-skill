"""
Utility for checking file freshness to skip redundant data collection tasks.
"""

import time
from pathlib import Path


def is_file_fresh(path: str | Path, max_age_days: int = 7) -> bool:
    """
    Returns True if file exists, is non-empty, and was modified within max_age_days.
    """
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return False
    age_seconds = time.time() - p.stat().st_mtime
    age_days = age_seconds / 86400
    return age_days < max_age_days


def get_file_age_days(path: str | Path) -> float | None:
    """
    Returns the age of the file in days, or None if the file doesn't exist.
    """
    p = Path(path)
    if not p.exists():
        return None
    return (time.time() - p.stat().st_mtime) / 86400
