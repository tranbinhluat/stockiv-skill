"""
Collector Crew - Data Gathering Authority

Responsible for calling external APIs (vnstock, Brave Search) to gather
quantitative financial data and qualitative market context. Populates local
storage for downstream crews.
"""

import os
import sys

# Ensure tools can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

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
from stockiv.agents import primary_llm, light_llm  # noqa: E402
from tools.vnstock_tools import (  # noqa: E402
    fetch_historical_prices,
    fetch_financial_statements,
    fetch_financial_ratios,
    fetch_company_overview,
    fetch_ratio_summary,
    fetch_dividend_history,
    crawl_vietstock_ratios,
    crawl_vnindex_ratios,
)
from tools.brave_tools import search_market_context  # noqa: E402
from tools.report_finder_tools import search_annual_report_pdf, download_and_convert_pdf  # noqa: E402
from tools.cache_tools import clean_expired_cache  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from typing import Optional  # noqa: E402


class CollectorCrewInputs(BaseModel):
    stock_symbols: Optional[str] = Field(
        default=None,
        description="The stock ticker symbol to collect data for (e.g. 'FPT').",
    )
    company_name: Optional[str] = Field(
        default=None,
        description="Full company name for the ticker (e.g. 'FPT Corporation'). Used by search agents to avoid ticker ambiguity.",
    )
    market_context_path: Optional[str] = Field(
        default=None,
        description="File path to save the generated macro market context.",
    )
    ticker_context_path: Optional[str] = Field(
        default=None,
        description="File path to save the generated ticker-specific context.",
    )
    annual_report_md_dir: Optional[str] = Field(
        default=None,
        description="Directory path to save the parsed markdown annual reports.",
    )
    annual_report_pdf_dir: Optional[str] = Field(
        default=None,
        description="Directory path containing the raw PDF annual reports.",
    )
    current_year: Optional[str] = Field(
        default=None,
        description="The current year to ensure searched data is fresh.",
    )


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
                crawl_vietstock_ratios,
                crawl_vnindex_ratios,
            ],
        )

    @agent
    def macro_micro_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["macro_micro_scout"],
            llm=primary_llm,
            tools=[search_market_context, clean_expired_cache],
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
    def crawl_live_ratios_task(self) -> Task:
        return Task(
            config=self.tasks_config["crawl_live_ratios_task"],
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

    def run(self, inputs: CollectorCrewInputs):
        """
        Executes the Collector Crew with strongly typed inputs.
        """
        return self.crew().kickoff(inputs=inputs.model_dump())
