"""
CrewAI Project - Test Orchestrator Crew

Simple test to spin up the Orchestrator crew and confirm its responsibility,
scope of work, and workflow.
"""

import os
from crewai import Crew, Process, Task

from stockiv.callbacks import LoggingCallback, ConsoleCallback
from stockiv.crews.orchestrator.orchestrator import OrchestratorCrew


def main():
    """Run the Orchestrator crew test."""
    # Check for API keys
    key = os.getenv("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_AUTH_TOKEN"))
    if not key:
        print(
            "Error: ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not found. Please set it in your .env file."
        )
        return

    # Create the orchestrator crew
    orchestrator_crew = OrchestratorCrew()

    # Initialize event listeners (singleton - registers with event bus)
    LoggingCallback()
    ConsoleCallback()

    # Create a simple test task to confirm the orchestrator's role
    test_task = Task(
        description="Please confirm your responsibility, scope of work, and workflow. Explain how you coordinate the stock analysis process from data collection through final reporting.",
        expected_output="A clear explanation of your role as Workflow Orchestrator, including the crews you coordinate, the sequential workflow you manage, and how you handle Director feedback.",
        agent=orchestrator_crew.orchestrator(),
    )

    # Create and run crew
    crew = Crew(
        agents=[orchestrator_crew.orchestrator()],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True,
        tracing=True,
    )

    print("\n" + "=" * 60)
    print("Starting Orchestrator Crew Test")
    print("=" * 60 + "\n")

    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")

    print("Orchestrator Response:")
    print("-" * 60)
    print(result)


if __name__ == "__main__":
    main()
