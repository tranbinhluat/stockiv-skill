"""
Main Entry Point & Master Flow Orchestrator for StockIV.
"""

from stockiv.flows.deepdive import DeepDiveFlow
from stockiv.flows.weekly import WeeklyReportFlow
from stockiv.flows.report_loop import SynthesizerReporterFlow
from stockiv.utils.logger import setup_global_logger


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
        print("[System] Initializing DeepDive Flow...")
        flow = DeepDiveFlow()
    elif args.flow == "weekly":
        print("[System] Initializing Weekly Report Flow...")
        flow = WeeklyReportFlow()
    elif args.flow == "reportloop":
        print("[System] Initializing Synthesizer->Director Loop Flow...")
        flow = SynthesizerReporterFlow()
        flow.state.max_loops = args.max_loops
        flow.state.target_ticker = "FPT"  # Test default
    else:
        print("[System] Unknown flow requested.")
        return

    flow.state.request = args.request

    mock_crews_list = [c.strip().lower() for c in args.mock.split(",") if c.strip()]
    flow.state.mock_crews = mock_crews_list

    result = flow.kickoff()
    print(f"\n[{args.flow.capitalize()} Flow Result]:\n{result}")


if __name__ == "__main__":
    kickoff()
