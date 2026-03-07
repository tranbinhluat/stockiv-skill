"""
Collector Crew - Data Gathering Authority

Responsible for calling external APIs (vnstock, Brave Search) to gather
quantitative financial data and qualitative market context. Populates local
storage for downstream crews.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import primary_llm, light_llm
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
    fetch_market_index,
)
from tools.brave_tools import search_market_context
from tools.report_finder_tools import search_annual_report_pdf, download_and_convert_pdf


@CrewBase
class CollectorCrew:
    """Collector Crew - Data Gathering Authority"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def collector_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["collector_manager"],
            llm=light_llm,
            allow_delegation=True,
        )

    @agent
    def market_data_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_data_fetcher"],
            llm=light_llm,
            tools=[
                fetch_historical_prices,
                fetch_financial_statements,
                fetch_financial_ratios,
                fetch_company_overview,
                fetch_ratio_summary,
                fetch_dividend_history,
                fetch_market_index,
            ],
        )

    @agent
    def macro_micro_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["macro_micro_scout"],
            llm=primary_llm,
            tools=[search_market_context],
        )

    @agent
    def annual_report_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["annual_report_analyst"],
            llm=light_llm,
            tools=[search_annual_report_pdf, download_and_convert_pdf],
        )

    @task
    def fetch_financials_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_financials_task"],
        )

    @task
    def fetch_annual_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_annual_report_task"],
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
        # When using @CrewBase, self.agents becomes a list of the *instantiated* agents automatically.
        # We need to explicitly filter out the manager agent from the worker list.
        worker_agents = [
            agent
            for agent in self.agents
            if agent.role != self.agents_config["collector_manager"]["role"]
        ]

        return Crew(
            agents=worker_agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.collector_manager(),
            verbose=True,
            tracing=True,
        )
