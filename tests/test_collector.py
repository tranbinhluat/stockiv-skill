import sys
import os

# Ensure tools can be imported properly for standalone testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from stockiv.crews.collector.collector import CollectorCrew


def test_collector():
    print("Initializing Collector Crew...")
    collector_base = CollectorCrew()
    crew = collector_base.crew()

    print("\n[TEST] Initiating MOCK execution of Collector Crew for stock 'FPT'...")

    # We inject a blatant dry-run instruction to force the LLMs to skip actual tool usage
    mock_instruction = "Help me collect data for MWG stock"

    try:
        # Kickoff the crew with the injected mock instructions
        result = crew.kickoff(inputs={"stock_symbols": mock_instruction})

        print("\n\n=========================================")
        print("MOCK EXECUTION COMPLETED SUCCESSFULLY!")
        print("=========================================")
        print("FINAL CREW OUTPUT:")
        print(result)

    except Exception as e:
        print(f"\n[ERROR] Mock Execution failed: {str(e)}")


if __name__ == "__main__":
    test_collector()
