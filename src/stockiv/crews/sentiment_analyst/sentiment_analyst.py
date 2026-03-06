"""
Sentiment Analyst Crew - Analyzes market sentiment and news.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import Memory

from crewai_tools import FileReadTool

from stockiv.agents.base import get_llm


@CrewBase
class SentimentAnalystCrew:
    """Sentiment Analyst Crew - Market Sentiment Analysis"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["sentiment_analyst"],
            llm=get_llm("qwen3-max-2026-01-23"),
            tools=[FileReadTool()],
        )

    @task
    def summarize_market(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_market"],
        )

    @task
    def summarize_symbol(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_symbol"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Sentiment Analyst Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
            memory=Memory(
                llm=get_llm("qwen3-max-2026-01-23"),
                embedder={
                    "provider": "huggingface",
                    "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
                },
            ),
        )
