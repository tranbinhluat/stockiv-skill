#!/usr/bin/env python3
"""View CrewAI execution logs."""

import json
import argparse
from pathlib import Path


def view_logs(log_file: str, tail: int = None, filter_event: str = None):
    """Display logs in a readable format."""
    log_path = Path(log_file)

    if not log_path.exists():
        print(f"Log file not found: {log_file}")
        return

    events = []
    with open(log_path) as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    if filter_event:
        events = [e for e in events if e.get("event") == filter_event]

    if tail:
        events = events[-tail:]

    for event in events:
        event_type = event.get("event", "unknown")
        timestamp = event.get("timestamp", "")
        print(f"\n[{timestamp}] {event_type.upper()}")

        for key, value in event.items():
            if key not in ("event", "timestamp"):
                print(f"  {key}: {value}")


def list_logs(log_dir: str = "./logs"):
    """List all available log files."""
    log_path = Path(log_dir)
    if not log_path.exists():
        print(f"No logs directory found: {log_dir}")
        return

    logs = sorted(log_path.glob("crew_*.jsonl"))
    if not logs:
        print(f"No log files found in {log_dir}")
        return

    print(f"Found {len(logs)} log file(s):")
    for log in logs:
        # Count lines
        with open(log) as f:
            lines = sum(1 for _ in f)
        print(f"  - {log.name} ({lines} events)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View CrewAI logs")
    parser.add_argument("--list", action="store_true", help="List all log files")
    parser.add_argument(
        "--file", default="./logs/crew_latest.jsonl", help="Log file to view"
    )
    parser.add_argument("--tail", type=int, help="Show last N events")
    parser.add_argument("--filter", help="Filter by event type")

    args = parser.parse_args()

    if args.list:
        list_logs()
    else:
        view_logs(args.file, args.tail, args.filter)
