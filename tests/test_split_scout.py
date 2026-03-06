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

# Find the two new context tasks
macro_task = next(
    task for task in collector.tasks if task.name == "fetch_macro_context_task"
)
ticker_task = next(
    task for task in collector.tasks if task.name == "fetch_ticker_context_task"
)

print(f"[*] Found Task: {macro_task.name}")
print(f"[*] Found Task: {ticker_task.name}")
print("[*] Executing target: FPT")

test_crew = Crew(
    agents=[macro_task.agent, ticker_task.agent],  # Technically the same agent
    tasks=[macro_task, ticker_task],
    verbose=True,
    tracing=True,
)

result = test_crew.kickoff(inputs={"stock_symbols": "FPT"})

print("\n\n" + "=" * 50)
print("FINAL SCOUT OUTPUT")
print("=" * 50)
print(result.raw)
