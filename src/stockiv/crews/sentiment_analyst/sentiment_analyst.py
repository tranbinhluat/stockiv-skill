"""
Sentiment Analyst Crew - Analyzes market sentiment and news.
"""

import os
from dotenv import load_dotenv
from langtrace_python_sdk import langtrace
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool
from stockiv.agents.base import get_llm

load_dotenv()

if os.getenv("LANGTRACE_API_KEY"):
    print("Found langtrace api key.")
    langtrace.init(
        api_key=os.getenv("LANGTRACE_API_KEY"),
        disable_instrumentations={"all_except": ["openai"]},
    )


@CrewBase
class SentimentAnalystCrew:
    """Sentiment Analyst Crew - Market Sentiment Analysis"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def macro_sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["macro_sentiment_analyst"],
            llm=get_llm("qwen3-max-2026-01-23"),
            tools=[FileReadTool()],
            reasoning=True,
            max_reasoning_attempts=2,
        )

    @agent
    def trend_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["trend_analyst"],
            llm=get_llm("qwen3-max-2026-01-23"),
            # Granting both so it can find historical files and read them
            tools=[DirectoryReadTool(), FileReadTool()],
            reasoning=True,
            max_reasoning_attempts=2,
        )

    @agent
    def ticker_sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["ticker_sentiment_analyst"],
            llm=get_llm("qwen3-max-2026-01-23"),
            tools=[FileReadTool()],
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @task
    def summarize_current_week_macro(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_current_week_macro"],
        )

    @task
    def synthesize_recent_trends(self) -> Task:
        return Task(
            config=self.tasks_config["synthesize_recent_trends"],
        )

    @task
    def summarize_symbol_sentiment(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_symbol_sentiment"],
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
            # Memory removed to prevent Qwen JSON parsing crashes
        )
