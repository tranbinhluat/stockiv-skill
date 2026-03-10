"""
Reporter Crew - Generates comprehensive reports and publishes to Discord.
"""

import os
import sys

# Ensure tools can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from dotenv import load_dotenv

from stockiv.agents import primary_llm, light_llm
from tools.discord_publisher_tool import send_discord_message
from tools.pdf_exporter_tool import markdown_to_pdf
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()


class ReporterCrewInputs(BaseModel):
    stock_symbols: Optional[str] = Field(
        default=None,
        description="Comma-separated stock symbols for which the report is generated.",
    )
    report_file_path: Optional[str] = Field(
        default=None,
        description="Path to the source markdown report file to be translated/formatted.",
    )
    report_title: Optional[str] = Field(
        default=None, description="The title to use for the final report document."
    )
    pdf_output_path: Optional[str] = Field(
        default=None, description="Destination path for the generated PDF report."
    )


@CrewBase
class ReporterCrew:
    """Reporter Crew - Report Generation & Publishing"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ------------------
    # AGENTS
    # ------------------

    @agent
    def reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["reporter"],
            llm=primary_llm,
        )

    @agent
    def translator(self) -> Agent:
        return Agent(
            config=self.agents_config["translator"],
            llm=primary_llm,
            tools=[FileReadTool()],
        )

    @agent
    def pdf_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["pdf_generator"],
            llm=light_llm,
            tools=[markdown_to_pdf],
        )

    @agent
    def formatter(self) -> Agent:
        return Agent(
            config=self.agents_config["formatter"],
            llm=light_llm,
        )

    @agent
    def discord_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["discord_publisher"],
            llm=light_llm,
            tools=[send_discord_message],
        )

    # ------------------
    # TASKS
    # ------------------

    @task
    def translate_report(self) -> Task:
        return Task(
            config=self.tasks_config["translate_report"],
        )

    @task
    def export_to_pdf(self) -> Task:
        return Task(
            config=self.tasks_config["export_to_pdf"],
        )

    @task
    def format_report(self) -> Task:
        return Task(
            config=self.tasks_config["format_report"],
        )

    @task
    def publish_to_discord(self) -> Task:
        return Task(
            config=self.tasks_config["publish_to_discord"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Reporter Crew pipeline. Note: Generate Report task is omitted here as it's assumed to run in another place or replaced by the incoming context."""
        return Crew(
            agents=[
                self.translator(),
                self.pdf_generator(),
                self.formatter(),
                self.discord_publisher(),
            ],
            tasks=[
                self.translate_report(),
                self.export_to_pdf(),
                self.format_report(),
                self.publish_to_discord(),
            ],
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def run(self, inputs: ReporterCrewInputs):
        """
        Executes the Reporter Crew with strongly typed inputs.
        """
        return self.crew().kickoff(inputs=inputs.model_dump())
