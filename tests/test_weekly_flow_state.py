import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from stockiv.flows.weekly import WeeklyReportFlow


def test_weekly_flow():
    print("Testing Weekly Flow Initialization and Kickoff in Mock Mode...")

    flow = WeeklyReportFlow()
    flow.state.is_mock = True

    try:
        # We only want to test flow generation and path passing.
        # Flow.kickoff() will run the full flow. Since mock is true, it shouldn't hit real APIs much.
        _ = flow.kickoff()
        print("Flow state variables:")
        print(f"- report_md_path: {flow.state.report_md_path}")
        print(f"- report_pdf_path: {flow.state.report_pdf_path}")
        print(
            f"- overall_report_md_path: {flow.state.shared_data.get('overall_report_md_path')}"
        )
        print("\nFlow executed successfully in mock mode.")
    except Exception as e:
        print(f"Flow execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_weekly_flow()
