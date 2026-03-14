import os
from crewai import Task, Crew, Agent
from stockiv.agents import advanced_llm
from crewai_tools import FileReadTool


def test_native_read_file():
    # Create a dummy file
    test_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "dummy_evidence_native.txt")
    )
    with open(test_file_path, "w") as f:
        f.write(
            "SECRET_PASSCODE: 99_ALPHA\nThis is evidence that there are no anomalies."
        )

    print(f"Created test file at: {test_file_path}")

    # Create an agent using native FileReadTool
    director_agent = Agent(
        role="Analysis Director",
        goal="Read files exactly as instructed.",
        backstory="You are a strict director who only uses tools exactly when told to.",
        llm=advanced_llm,
        tools=[FileReadTool()],
        verbose=True,
    )

    # Create a simple task to test tool usage with STRICT instructions
    test_task = Task(
        description=f"Read the file located EXACTLY at '{test_file_path}' using your Read a file's content tool and return the SECRET_PASSCODE found inside it as your final answer. DO NOT PASS ANY OPTIONAL ARGUMENTS LIKE start_line OR end_line.",
        expected_output="The exact secret passcode found in the file.",
        agent=director_agent,
    )

    # Run a mini crew
    crew = Crew(agents=[director_agent], tasks=[test_task], verbose=True)

    print("Starting Crew...")
    try:
        result = crew.kickoff()
        print("\n--- RESULT ---")
        print(result.raw)
    except Exception as e:
        print("\n--- CRASH ---")
        print(f"Agent crashed with error: {e}")

    # Clean up
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"Cleaned up {test_file_path}")


if __name__ == "__main__":
    test_native_read_file()
