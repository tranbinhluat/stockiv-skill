"""
Test: Run Report Loop Flow with real Synthesizer & Director crews.
Only human-in-the-loop is mocked to prevent CLI hanging.

Usage:
    uv run python tests/test_report_loop.py
    uv run python tests/test_report_loop.py --ticker MWG --max-loops 3
    uv run python tests/test_report_loop.py --mock synthesizer,director,human
"""

import argparse

from stockiv.flows.report_loop import SynthesizerReporterFlow
from stockiv.utils.logger import setup_global_logger


def main():
    parser = argparse.ArgumentParser(description="Test Report Loop Flow")
    parser.add_argument("--ticker", type=str, default="FPT", help="Stock ticker")
    parser.add_argument("--max-loops", type=int, default=5, help="Max feedback loops")
    parser.add_argument(
        "--mock",
        type=str,
        default="human",
        help="Comma-separated crews to mock (e.g., 'human', 'synthesizer,director,human', 'all')",
    )
    args = parser.parse_args()

    # Enable logging (same as main.py)
    setup_global_logger("test_report_loop")

    mock_list = [m.strip().lower() for m in args.mock.split(",") if m.strip()]

    print("=" * 60)
    print("  Report Loop Flow Test")
    print(f"  Ticker:    {args.ticker}")
    print(f"  Max Loops: {args.max_loops}")
    print(f"  Mocking:   {mock_list}")
    print("=" * 60)

    flow = SynthesizerReporterFlow()
    flow.state.target_ticker = args.ticker.upper()
    flow.state.mock = mock_list
    flow.state.max_loops = args.max_loops

    result = flow.kickoff()

    print("\n" + "=" * 60)
    print(f"  Flow Result:        {result}")
    print(f"  Director Approval:  {flow.state.director_approval}")
    print(f"  Report Version:     {flow.state.report_version}")
    print(f"  Loop Count:         {flow.state.loop_count}")
    print("  History:")
    for line in flow.state.history.strip().split("\n"):
        print(f"    {line}")
    print("=" * 60)


if __name__ == "__main__":
    main()
