import os

os.environ["CHROMA_HUGGINGFACE_API_KEY"] = "dummy_key"  # pragma: allowlist secret

from crewai import Crew, Agent, Task
from stockiv.agents.base import primary_llm

agent = Agent(role="Test", goal="Test", backstory="Test", llm=primary_llm)

print("Agent initialized with memory. Type 'exit' to quit.")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        break

    task = Task(
        description=user_input, expected_output="A helpful response.", agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        # memory=,
        # embedder={
        #     "provider": "huggingface",
        #     "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
        # }
    )
    result = crew.kickoff()
    print(f"\nAgent: {result.raw}")
