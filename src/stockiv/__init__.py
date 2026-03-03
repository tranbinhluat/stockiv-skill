"""
CrewAI Project - Main Entry Point

This example demonstrates a basic CrewAI setup with research and writing agents.
Configured to use Gemini 2.5 Pro.
"""

import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from dotenv import load_dotenv

from stockiv.callbacks import LoggingCallback, ConsoleCallback

load_dotenv()

# Configure Gemini
gemini_llm = LLM(
    model="gemini/gemini-3-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
)


def create_researcher() -> Agent:
    """Create a research agent that searches and analyzes information."""
    return Agent(
        role="Senior Research Analyst",
        goal="Discover cutting-edge developments in AI and data science",
        backstory="""You are an experienced research analyst with a keen eye for
        emerging trends in technology. You have a knack for finding relevant
        information and synthesizing complex topics.""",
        tools=[SerperDevTool(), ScrapeWebsiteTool()],
        llm=gemini_llm,
        verbose=True,
    )


def create_writer() -> Agent:
    """Create a writing agent that creates content based on research."""
    return Agent(
        role="Tech Content Writer",
        goal="Craft engaging blog posts about AI developments",
        backstory="""You are a skilled writer who transforms technical concepts
        into accessible, engaging content. Your readers love your clear explanations
        and real-world examples.""",
        llm=gemini_llm,
        verbose=True,
    )


def create_tasks(agents: dict) -> list[Task]:
    """Create research and writing tasks."""
    research_task = Task(
        description="""Research the latest developments in large language models
        and AI agents. Focus on recent breakthroughs from the past month.
        Include specific examples, company names, and technical details.""",
        expected_output="A comprehensive report with 5-7 key developments, "
        "including sources and technical details",
        agent=agents["researcher"],
    )

    writing_task = Task(
        description="""Using the research findings, write an engaging blog post
        about the latest AI developments. The post should be informative yet
        accessible to a general tech audience.""",
        expected_output="A 500-700 word blog post with a catchy title, "
        "clear structure, and actionable insights",
        agent=agents["writer"],
    )

    return [research_task, writing_task]


def main():
    """Run the CrewAI crew."""
    # Check for API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found. Please set it in your .env file.")
        print("Example: GOOGLE_API_KEY=your-key-here")
        return

    if not os.getenv("SERPER_API_KEY"):
        print("Warning: SERPER_API_KEY not found. Web search tools will not work.")
        print("Get one at: https://serper.dev/api-key")

    # Create agents
    agents = {
        "researcher": create_researcher(),
        "writer": create_writer(),
    }

    # Create tasks
    tasks = create_tasks(agents)

    # Initialize event listeners (singleton - registers with event bus)
    LoggingCallback()
    ConsoleCallback()

    # Create and run crew
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        tracing=True,
    )

    print("\n" + "=" * 60)
    print("Starting CrewAI Research & Writing Crew")
    print("=" * 60 + "\n")

    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("Crew execution completed!")
    print("=" * 60 + "\n")

    print("Final Output:")
    print("-" * 60)
    print(result)


if __name__ == "__main__":
    main()
