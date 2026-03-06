import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crewai import Crew
from stockiv.crews.collector.collector import CollectorCrew
from stockiv.callbacks import LoggingCallback, ConsoleCallback

print("[*] Initializing callbacks...")
LoggingCallback()
ConsoleCallback()

print("[*] Instantiating CollectorCrew...")
collector = CollectorCrew().crew()

# Find the fetch_market_context_task
scout_task = next(
    task for task in collector.tasks if task.name == "fetch_market_context_task"
)

print(f"[*] Found Task: {scout_task.name}")
print("[*] Executing target: FPT")

test_crew = Crew(
    agents=[scout_task.agent], tasks=[scout_task], verbose=True, tracing=True
)

result = test_crew.kickoff(inputs={"stock_symbols": "FPT"})

print("\n\n" + "=" * 50)
print("FINAL SCOUT OUTPUT")
print("=" * 50)
print(result.raw)
