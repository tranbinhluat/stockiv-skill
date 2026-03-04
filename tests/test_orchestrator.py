"""
CrewAI Project - Test Orchestrator Crew

Simple test to spin up the Orchestrator crew and confirm its responsibility,
scope of work, and workflow.
"""

import os
from stockiv.callbacks import LoggingCallback, ConsoleCallback
from stockiv.crews.orchestrator.orchestrator import StockOrchestratorFlow


def main():
    """Run the Orchestrator Flow test."""
    # Check for API keys
    key = os.getenv("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_AUTH_TOKEN"))
    if not key:
        print(
            "Error: ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not found. Please set it in your .env file."
        )
        return

    # Initialize event listeners (singleton - registers with event bus)
    LoggingCallback()
    ConsoleCallback()

    print("\n" + "=" * 60)
    print("Starting Orchestrator Flow Test")
    print("=" * 60 + "\n")

    # Initialize the new Flow
    orchestrator_flow = StockOrchestratorFlow()

    # We want to test routing to the Collector Crew for the ticker 'FPT'
    # We pass this into the flow's state via kickoff() inputs
    print("User Action: Requesting to collect data for FPT...")
    result = orchestrator_flow.kickoff(
        inputs={"request": "Please collect data for FPT."}
    )

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")

    print("Orchestrator Flow Final State:")
    print("-" * 60)
    import pprint

    pprint.pprint(orchestrator_flow.state)
    print("\nFlow Result:")
    print(result)


if __name__ == "__main__":
    main()
