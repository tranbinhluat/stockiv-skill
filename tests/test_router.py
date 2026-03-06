from stockiv.crews.orchestrator.orchestrator import StockOrchestratorFlow
import os
from stockiv.callbacks import LoggingCallback, ConsoleCallback


def run_test():
    print("[*] Initializing callbacks...")
    LoggingCallback()
    ConsoleCallback()

    # Ensure tracing is globally active for this test
    os.environ["CREWAI_TRACING_ENABLED"] = "true"

    print("Testing valid stock request...")
    flow = StockOrchestratorFlow()
    # Mock kickoff state
    result = flow.kickoff(
        inputs={"request": "Can you please collect all the data for FPT?"}
    )
    print("Flow Result:", result)
    print("Extracted Ticker:", flow.state.target_ticker)


if __name__ == "__main__":
    run_test()
