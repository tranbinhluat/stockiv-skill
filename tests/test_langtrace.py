import os
from dotenv import load_dotenv

# MUST BE IMPORTED BEFORE CREWAI
from langtrace_python_sdk import langtrace
from crewai import Agent, Crew, Process, Task
from stockiv.agents.base import primary_llm

load_dotenv()

if os.getenv("LANGTRACE_API_KEY"):
    print("Initializing Langtrace...")
    langtrace.init(
        api_key=os.getenv("LANGTRACE_API_KEY"),
        disable_instrumentations={"all_except": ["openai"]},
    )
else:
    print("No LANGTRACE_API_KEY found.")


def run_test():
    print("Creating Agent...")
    test_agent = Agent(
        role="Test Agent",
        goal="Say hello",
        backstory="You are a simple test agent.",
        verbose=True,
        llm=primary_llm,
    )

    print("Creating Task...")
    test_task = Task(
        description="Write a 1 sentence greeting.",
        expected_output="A single greeting sentence.",
        agent=test_agent,
    )

    print("Creating Crew...")
    test_crew = Crew(
        agents=[test_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True,
    )

    print("Kicking off...")
    result = test_crew.kickoff()
    print("Result:", result)


if __name__ == "__main__":
    run_test()
