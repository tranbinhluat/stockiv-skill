"""
CrewAI Callbacks for monitoring and logging.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from crewai.callbacks import CrewAICallbacks
from typing import Any, Dict


class LoggingCallback(CrewAICallbacks):
    """Custom callback to log all crew events."""

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = (
            self.log_dir / f"crew_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )
        self.start_time = None

    def on_crew_start(self) -> None:
        """Called when the crew starts execution."""
        self.start_time = time.time()
        self._log(
            {
                "event": "crew_start",
                "timestamp": datetime.now().isoformat(),
            }
        )

    def on_crew_end(self, output: Any) -> None:
        """Called when the crew finishes execution."""
        duration = time.time() - self.start_time if self.start_time else 0
        self._log(
            {
                "event": "crew_end",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "output": str(output)[:500],  # Truncate long outputs
            }
        )

    def on_task_start(self, task: Any) -> None:
        """Called when a task starts."""
        self._log(
            {
                "event": "task_start",
                "timestamp": datetime.now().isoformat(),
                "task": task.description if hasattr(task, "description") else str(task),
            }
        )

    def on_task_end(self, task: Any, output: Any) -> None:
        """Called when a task finishes."""
        self._log(
            {
                "event": "task_end",
                "timestamp": datetime.now().isoformat(),
                "task": task.description if hasattr(task, "description") else str(task),
                "output": str(output)[:500],
            }
        )

    def on_agent_action(self, agent: Any, action: Any) -> None:
        """Called when an agent performs an action."""
        self._log(
            {
                "event": "agent_action",
                "timestamp": datetime.now().isoformat(),
                "agent": agent.role if hasattr(agent, "role") else str(agent),
                "action": str(action)[:300],
            }
        )

    def on_tool_use(self, tool_name: str, input_data: Any, result: Any) -> None:
        """Called when a tool is used."""
        self._log(
            {
                "event": "tool_use",
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "input": str(input_data)[:300],
                "result": str(result)[:300],
            }
        )

    def _log(self, data: Dict[str, Any]) -> None:
        """Write log entry to file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(data) + "\n")


class ConsoleCallback(CrewAICallbacks):
    """Simple console output callback."""

    def on_task_start(self, task: Any) -> None:
        print(f"\n🚀 Task started: {task.description[:80]}...")

    def on_task_end(self, task: Any, output: Any) -> None:
        print(f"\n✅ Task completed: {task.description[:80]}...")

    def on_tool_use(self, tool_name: str, input_data: Any, result: Any) -> None:
        print(f"\n🔧 Tool used: {tool_name}")
