"""
Sentiment Analyst Crew - Analyzes market sentiment and news.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import FileReadTool

from stockiv.agents import primary_llm


@CrewBase
class SentimentAnalystCrew:
    """Sentiment Analyst Crew - Market Sentiment Analysis"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["sentiment_analyst"],
            llm=primary_llm,
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
            memory=True,
            embedder={
                "provider": "huggingface",
                "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
            },
        )
