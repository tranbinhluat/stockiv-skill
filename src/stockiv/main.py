"""
Main Entry Point & Master Flow Orchestrator for StockIV.
"""

from stockiv.flows.deepdive import DeepDiveFlow
from stockiv.flows.weekly import WeeklyReportFlow


def kickoff():
    """CLI Entry Point."""
    import argparse

    parser = argparse.ArgumentParser(description="StockIV AI Agent Orchestrator")
    parser.add_argument(
        "--request",
        type=str,
        help="The natural language request (e.g., 'Gather data for FPT')",
        default="Deep dive analyze MWG",
    )
    parser.add_argument(
        "--flow",
        type=str,
        choices=["deepdive", "weekly"],
        default="deepdive",
        help="Which orchestration flow to run.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run the pipeline in Mock Mode to bypass expensive LLM executions.",
    )
    args = parser.parse_args()

    if args.flow == "deepdive":
        print("[System] Initializing DeepDive Flow...")
        flow = DeepDiveFlow()
    elif args.flow == "weekly":
        print("[System] Initializing Weekly Report Flow...")
        flow = WeeklyReportFlow()
    else:
        print("[System] Unknown flow requested.")
        return

    flow.state.request = args.request
    flow.state.is_mock = args.mock
    
    result = flow.kickoff()
    print(f"\n[{args.flow.capitalize()} Flow Result]:\n{result}")


if __name__ == "__main__":
    kickoff()
