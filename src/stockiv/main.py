"""
Main Entry Point & Master Flow Orchestrator for StockIV.
"""

from stockiv.flows.deepdive import DeepDiveFlow
from stockiv.flows.weekly import WeeklyReportFlow
from stockiv.flows.report_loop import ReportLoopFlow
from stockiv.utils.logger import setup_global_logger


def kickoff():
    import argparse
    import os

    # Bypass crewai_tools pydantic validation bug for local LLMs
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = (
            "dummy-key-for-local-llms"  # pragma: allowlist secret
        )

    parser = argparse.ArgumentParser(description="StockIV AI Agent Orchestrator")
    parser.add_argument(
        "--request",
        type=str,
        help="The natural language request (e.g., 'Gather data for FPT')",
        default="Deep dive analyze MWG",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        help="Target ticker symbol for DeepDive flow (e.g., 'FPT', 'MWG').",
        default="MWG",
    )
    parser.add_argument(
        "--flow",
        type=str,
        choices=["deepdive", "weekly", "reportloop"],
        default="deepdive",
        help="Which orchestration flow to run.",
    )
    parser.add_argument(
        "--mock",
        type=str,
        default="",
        help="Comma-separated list of crews to mock (e.g., 'all', 'collector', 'sentiment', 'reporter', 'synthesizer').",
    )
    parser.add_argument(
        "--max_loops",
        type=int,
        default=5,
        help="Max retries if Director rejects analysis (ReportLoop flow only).",
    )
    args = parser.parse_args()

    setup_global_logger(f"cli_{args.flow}")

    if args.flow == "deepdive":
        print(f"[System] Initializing DeepDive Flow for {args.ticker}...")
        flow = DeepDiveFlow()
        flow.state.target_ticker = args.ticker.upper()
    elif args.flow == "weekly":
        print("[System] Initializing Weekly Report Flow...")
        flow = WeeklyReportFlow()
    elif args.flow == "reportloop":
        print("[System] Initializing Synthesizer->Director Loop Flow...")
        flow = ReportLoopFlow()
        flow.state.max_loops = args.max_loops
        flow.state.target_ticker = args.ticker.upper()
    else:
        print("[System] Unknown flow requested.")
        return

    flow.state.request = args.request

    mock_crews_list = [c.strip().lower() for c in args.mock.split(",") if c.strip()]
    flow.state.mock = mock_crews_list

    result = flow.kickoff()
    print(f"\n[{args.flow.capitalize()} Flow Result]:\n{result}")


if __name__ == "__main__":
    kickoff()
