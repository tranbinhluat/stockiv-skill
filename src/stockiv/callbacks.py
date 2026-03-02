"""
CrewAI Callbacks for monitoring and logging.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from crewai.events import crewai_event_bus
from crewai.events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
)


class LoggingCallback:
    """Custom callback to log all crew events."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to avoid duplicate handlers."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir: str = "./logs"):
        if self._initialized:
            return

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = (
            self.log_dir / f"crew_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )
        self.start_time = None
        self._register_handlers()
        LoggingCallback._initialized = True

    def _register_handlers(self):
        """Register event handlers on the event bus."""
        crewai_event_bus.on(CrewKickoffStartedEvent)(self.on_crew_start)
        crewai_event_bus.on(CrewKickoffCompletedEvent)(self.on_crew_end)
        crewai_event_bus.on(TaskStartedEvent)(self.on_task_start)
        crewai_event_bus.on(TaskCompletedEvent)(self.on_task_end)
        crewai_event_bus.on(ToolUsageStartedEvent)(self.on_tool_start)
        crewai_event_bus.on(ToolUsageFinishedEvent)(self.on_tool_end)

    def on_crew_start(self, source, event: CrewKickoffStartedEvent) -> None:
        """Called when the crew starts execution."""
        self.start_time = time.time()
        self._log(
            {
                "event": "crew_start",
                "timestamp": datetime.now().isoformat(),
            }
        )

    def on_crew_end(self, source, event: CrewKickoffCompletedEvent) -> None:
        """Called when the crew finishes execution."""
        duration = time.time() - self.start_time if self.start_time else 0
        self._log(
            {
                "event": "crew_end",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "output": str(event.result)[:500] if hasattr(event, "result") else "",
            }
        )

    def on_task_start(self, source, event: TaskStartedEvent) -> None:
        """Called when a task starts."""
        self._log(
            {
                "event": "task_start",
                "timestamp": datetime.now().isoformat(),
                "task": str(event.task),
            }
        )

    def on_task_end(self, source, event: TaskCompletedEvent) -> None:
        """Called when a task finishes."""
        self._log(
            {
                "event": "task_end",
                "timestamp": datetime.now().isoformat(),
                "task": str(event.task),
                "output": str(event.output)[:500] if hasattr(event, "output") else "",
            }
        )

    def on_tool_start(self, source, event: ToolUsageStartedEvent) -> None:
        """Called when a tool starts execution."""
        self._log(
            {
                "event": "tool_start",
                "timestamp": datetime.now().isoformat(),
                "tool": str(event.tool_name)
                if hasattr(event, "tool_name")
                else str(event.tool),
                "input": str(event.tool_input)[:300]
                if hasattr(event, "tool_input")
                else "",
            }
        )

    def on_tool_end(self, source, event: ToolUsageFinishedEvent) -> None:
        """Called when a tool finishes execution."""
        self._log(
            {
                "event": "tool_end",
                "timestamp": datetime.now().isoformat(),
                "tool": str(event.tool_name)
                if hasattr(event, "tool_name")
                else str(event.tool),
                "result": str(event.result)[:300] if hasattr(event, "result") else "",
            }
        )

    def _log(self, data: dict) -> None:
        """Write log entry to file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(data) + "\n")


class ConsoleCallback:
    """Simple console output callback."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to avoid duplicate handlers."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._register_handlers()
        ConsoleCallback._initialized = True

    def _register_handlers(self):
        """Register event handlers on the event bus."""
        crewai_event_bus.on(TaskStartedEvent)(self.on_task_start)
        crewai_event_bus.on(TaskCompletedEvent)(self.on_task_end)
        crewai_event_bus.on(ToolUsageStartedEvent)(self.on_tool_start)
        crewai_event_bus.on(ToolUsageFinishedEvent)(self.on_tool_end)

    def on_task_start(self, source, event: TaskStartedEvent) -> None:
        task_desc = str(event.task)[:80]
        print(f"\n🚀 Task started: {task_desc}...")

    def on_task_end(self, source, event: TaskCompletedEvent) -> None:
        task_desc = str(event.task)[:80]
        print(f"\n✅ Task completed: {task_desc}...")

    def on_tool_start(self, source, event: ToolUsageStartedEvent) -> None:
        tool_name = (
            str(event.tool_name) if hasattr(event, "tool_name") else str(event.tool)
        )
        print(f"\n🔧 Tool using: {tool_name}...")

    def on_tool_end(self, source, event: ToolUsageFinishedEvent) -> None:
        tool_name = (
            str(event.tool_name) if hasattr(event, "tool_name") else str(event.tool)
        )
        print(f"\n✅ Tool finished: {tool_name}")
