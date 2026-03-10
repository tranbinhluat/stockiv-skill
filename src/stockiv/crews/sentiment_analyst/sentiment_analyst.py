"""
Sentiment Analyst Crew - Analyzes market sentiment and news.
"""

import os
from dotenv import load_dotenv

load_dotenv()
from langtrace_python_sdk import langtrace  # noqa: E402

if os.getenv("LANGTRACE_API_KEY"):
    print("Found langtrace api key.")
    langtrace.init(
        api_key=os.getenv("LANGTRACE_API_KEY"),
        disable_instrumentations={"all_except": ["openai"]},
    )

from crewai import Agent, Crew, Process, Task  # noqa: E402
from crewai.project import CrewBase, agent, crew, task  # noqa: E402
from crewai_tools import FileReadTool, DirectoryReadTool  # noqa: E402
from stockiv.agents.base import advanced_llm  # noqa: E402
from tools.sqlite_tools import FetchMarketIndexTool  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from typing import Optional  # noqa: E402


class SentimentAnalystCrewInputs(BaseModel):
    stock_symbols: Optional[str] = Field(
        default=None, description="The stock ticker symbol being analyzed."
    )
    year: Optional[str] = Field(
        default=None, description="The current year (e.g. '2026')."
    )
    week: Optional[str] = Field(
        default=None, description="The current ISO week number (e.g. '10')."
    )
    macro_sentiment_md_path: Optional[str] = Field(
        default=None,
        description="Path to save the generated markdown weekly macro sentiment.",
    )
    overall_macro_sentiment_md_path: Optional[str] = Field(
        default=None,
        description="Path to save or append to the overall yearly sentiment log.",
    )
    market_sentiment_dir: Optional[str] = Field(
        default=None,
        description="Directory path to save general market sentiment outputs.",
    )
    market_context_path: Optional[str] = Field(
        default=None,
        description="Path to the pre-crawled macro-market context document.",
    )
    ticker_context_path: Optional[str] = Field(
        default=None,
        description="Path to the pre-crawled ticker-specific context document.",
    )
    ticker_sentiment_path: Optional[str] = Field(
        default=None,
        description="Path to save the generated ticker-specific sentiment outputs.",
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
            llm=advanced_llm,
            tools=[FileReadTool()],
            reasoning=True,
            max_reasoning_attempts=2,
        )

    @agent
    def trend_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["trend_analyst"],
            llm=advanced_llm,
            # Granting both so it can find historical files and read them
            tools=[DirectoryReadTool(), FileReadTool(), FetchMarketIndexTool()],
            reasoning=True,
            max_reasoning_attempts=2,
        )

    @agent
    def ticker_sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["ticker_sentiment_analyst"],
            llm=advanced_llm,
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

    def run(self, inputs: SentimentAnalystCrewInputs):
        """
        Executes the Sentiment Analyst Crew with strongly typed inputs.
        """
        return self.crew().kickoff(inputs=inputs.model_dump())
