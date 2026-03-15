"""
Test: Run Reporter Crew standalone with a synthesis report file.

Exercises the full pipeline: translate → PDF → format → Discord publish.
Uses _ensure_clean_markdown() to handle JSON→Markdown extraction if needed.

Usage:
    uv run python tests/test_reporter_standalone.py
    uv run python tests/test_reporter_standalone.py --source /path/to/report.md --channel 1476822786575171604
"""

import argparse

from stockiv.flows.report_loop import SynthesizerReporterFlow
from stockiv.crews.reporter.reporter import ReporterCrew, ReporterCrewInputs
from stockiv.utils.logger import setup_global_logger


def main():
    parser = argparse.ArgumentParser(description="Test Reporter Crew standalone")
    parser.add_argument(
        "--source",
        type=str,
        default="data/processed/synthesizer/FPT/FPT_GCCP_report_v2.md",
        help="Path to the synthesis report markdown file",
    )
    parser.add_argument(
        "--channel",
        type=str,
        default="1476822786575171604",
        help="Discord channel ID to publish to",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default="FPT",
        help="Stock ticker symbol",
    )
    args = parser.parse_args()

    setup_global_logger("test_reporter_standalone")

    # Step 1: Ensure clean markdown (handles JSON → MD extraction)
    clean_path = SynthesizerReporterFlow._ensure_clean_markdown(args.source)
    print(f"Clean markdown path: {clean_path}")

    # Step 2: Build inputs — pdf_output_path and report_title auto-generated
    inputs = ReporterCrewInputs(
        stock_symbols=args.ticker,
        source_md_path=clean_path,
        discord_channel_id=args.channel,
    )

    print("=" * 60)
    print("  Reporter Crew Standalone Test")
    print(f"  Source:    {clean_path}")
    print(f"  Ticker:    {args.ticker}")
    print(f"  Channel:   {args.channel}")
    print("  PDF Path:  (auto-generated)")
    print("=" * 60)

    # Step 3: Run Reporter
    reporter = ReporterCrew()
    result = reporter.run(inputs=inputs)

    print("\n" + "=" * 60)
    print(f"  Result: {result}")
    print("=" * 60)


if __name__ == "__main__":
    main()
