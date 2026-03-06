"""
Collector Crew - Data Gathering Authority

Responsible for calling external APIs (vnstock, Brave Search) to gather
quantitative financial data and qualitative market context. Populates local
storage for downstream crews.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import primary_llm
import sys
import os

# Ensure tools can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from tools.vnstock_tools import (
    fetch_historical_prices,
    fetch_financial_statements,
    fetch_financial_ratios,
    fetch_company_overview,
    fetch_ratio_summary,
    fetch_dividend_history,
)
from tools.brave_tools import search_market_context


@CrewBase
class CollectorCrew:
    """Collector Crew - Data Gathering Authority"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def market_data_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_data_fetcher"],
            llm=primary_llm,
            tools=[
                fetch_historical_prices,
                fetch_financial_statements,
                fetch_financial_ratios,
                fetch_company_overview,
                fetch_ratio_summary,
                fetch_dividend_history,
            ],
        )

    @agent
    def macro_micro_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["macro_micro_scout"],
            llm=primary_llm,
            tools=[search_market_context],
        )

    @task
    def fetch_financials_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_financials_task"],
        )

    @task
    def fetch_daily_market_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_daily_market_data_task"],
        )

    @task
    def fetch_macro_context_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_macro_context_task"],
        )

    @task
    def fetch_ticker_context_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_ticker_context_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Collector Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
