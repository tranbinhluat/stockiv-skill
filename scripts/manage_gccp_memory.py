import os
from pathlib import Path
from crewai.memory.storage.unified_memory import UnifiedMemory

def get_gccp_memory():
    db_path = str(Path.home() / ".local" / "share" / "stockew" / "memory")
    return UnifiedMemory(
        storage_type="chromadoc",
        scope="/gccp",
        db_path=db_path,
        recency_weight=0.0,
        semantic_weight=1.0,
        importance_weight=0.0
    )
