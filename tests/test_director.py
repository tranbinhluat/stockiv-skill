"""
Test Director Crew with Dummy Analysis

Validates the Director's decision-making with different analysis scenarios.
"""

from stockiv.crews import DirectorCrew


# Test scenarios are now files in /tmp/


def test_director(name: str, file_path: str, ticker: str = "VCB"):
    """Run a test case through the Director."""
    print(f"\n{'=' * 80}")
    print(f"TEST: {name}")
    print(f"FILE: {file_path}")
    print(f"{'=' * 80}\n")

    crew = DirectorCrew()
    result = crew.crew().kickoff(
        inputs={
            "stock_symbols": ticker,
            "synthesis_report_path": file_path,
            "financial_summary_path": "/tmp/dummy_financial_summary.md",
        }
    )

    # Get the Pydantic output
    decision = result.pydantic

    # Display the markdown report
    print(decision.to_markdown())
    print(f"\n{'=' * 80}\n")

    return decision


if __name__ == "__main__":
    import sys

    # Run test cases

    # Save test strings to temp files to test the read_file flow
    GOOD_PATH = "/tmp/dummy_synthesis_report.md"
    BAD_PATH = "/tmp/dummy_synthesis_report_bad.md"
    ANOMALY_PATH = "/tmp/dummy_synthesis_report_anomaly.md"
    FINANCIAL_PATH = "/tmp/dummy_financial_summary.md"

    # Create the financial baseline file
    with open(FINANCIAL_PATH, "w") as f:
        f.write(
            "Financial Database Summary\nRevenue: 1000B VND\nNet Income: 150B VND\n"
        )

    test_cases = [
        ("Good Analysis (should APPROVE)", GOOD_PATH, "VCB"),
        ("Incomplete Analysis (should REJECT)", BAD_PATH, "XYZ"),
        ("Anomalies Present (should detect)", ANOMALY_PATH, "ABC"),
    ]

    # Run specific test or all
    if len(sys.argv) > 1:
        idx = int(sys.argv[1]) - 1
        test_cases = [test_cases[idx]]

    for name, path, ticker in test_cases:
        try:
            decision = test_director(name, path, ticker)
            print(f"✅ Test completed. Decision: {decision.decision}")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
