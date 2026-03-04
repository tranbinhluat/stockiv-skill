"""
Sentiment Analyst Crew - Analyzes market sentiment and news.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

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
        )

    @task
    def analyze_sentiment(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_sentiment"],
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
        )
