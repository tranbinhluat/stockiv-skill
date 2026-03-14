import os
from pydantic import BaseModel

# Required for local huggingface embedding
os.environ["CHROMA_HUGGINGFACE_API_KEY"] = "dummy_key"  # pragma: allowlist secret

from crewai import Crew, Agent, Task
from crewai.flow.flow import Flow, listen, start
from stockiv.agents.base import primary_llm


class ChatState(BaseModel):
    user_name: str = ""
    user_dog_name: str = ""
    conversation_history: str = ""


class MemoryTestFlow(Flow[ChatState]):
    """
    Test flow to verify if memory persists across completely separate crew runs
    within the same flow lifetime.
    """

    @start()
    def crew_one_introduction(self):
        print("\n--- STEP 1: INITIAL CHAT ---")
        user_input = input("You: ")

        agent1 = Agent(
            role="Friendly Greeter",
            goal="Have a pleasant chat with the user and learn about them.",
            backstory="You are a friendly agent who loves learning about people and their pets. You don't know anything until they tell you.",
            llm=primary_llm,
        )

        task1 = Task(
            description=f"Respond to the user naturally. User message: '{user_input}'",
            expected_output="A friendly response acknowledging what they said.",
            agent=agent1,
        )

        crew1 = Crew(
            agents=[agent1],
            tasks=[task1],
            # memory=True, # Enable memory sharing
            # embedder={
            #     "provider": "huggingface",
            #     "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
            # }
        )

        result = crew1.kickoff()
        print(f"\nAgent 1: {result.raw}")
        return

    @listen(crew_one_introduction)
    def crew_two_recall(self):
        print("\n\n--- STEP 2: RECALL TEST ---")
        print(
            "Now, a COMPLETELY DIFFERENT agent will try to answer based on the previous agent's memory."
        )
        user_input2 = input("You: ")

        agent2 = Agent(
            role="Memory Tester",
            goal="Answer the user's question accurately using your shared memory.",
            backstory="You are a different agent. You rely entirely on the shared CrewAI memory database to remember what the user said previously.",
            llm=primary_llm,
        )

        task2 = Task(
            description=f"Answer the user's question. Use your memory to recall details from previous conversations if necessary. User message: '{user_input2}'",
            expected_output="An answer that proves you remember the context.",
            agent=agent2,
        )

        crew2 = Crew(
            agents=[agent2],
            tasks=[task2],
            # memory=True, # Enable memory sharing
            # embedder={
            #     "provider": "huggingface",
            #     "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
            # }
        )

        result = crew2.kickoff()
        print(f"\nAgent 2: {result.raw}")
        return


if __name__ == "__main__":
    print("Initializing Memory Test Flow...")
    print("In Step 1, tell the agent your name or your dog's name.")
    print("In Step 2, ask the second agent what your name or dog's name is.")
    flow = MemoryTestFlow()
    flow.kickoff()
