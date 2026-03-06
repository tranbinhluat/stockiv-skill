import sys
import os
from crewai import Crew, Process

# Ensure tools can be imported properly for standalone testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stockiv.crews.collector.collector import CollectorCrew


def test_annual_report_fetching():
    print("Initialize Collector Crew...")
    collector_base = CollectorCrew()

    # We only want to test the annual report task, not the whole thing
    print("\nExtracting market_data_fetcher and fetch_annual_report_task...")
    fetcher_agent = collector_base.market_data_fetcher()
    report_task = collector_base.fetch_annual_report_task()

    # Create a mini-crew just for this test
    mini_crew = Crew(
        agents=[fetcher_agent],
        tasks=[report_task],
        process=Process.sequential,
        verbose=True,
    )

    print("\nKicking off Mini-Crew for stock 'FPT'...")
    inputs = {"stock_symbols": "FPT"}

    result = mini_crew.kickoff(inputs=inputs)

    print("\nFINAL RESULT:")
    print(result.raw)


if __name__ == "__main__":
    test_annual_report_fetching()
