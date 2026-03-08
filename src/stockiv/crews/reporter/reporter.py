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

from stockiv.agents import primary_llm
from tools.discord_publisher_tool import send_discord_message

load_dotenv()


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
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def discord_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["discord_publisher"],
            llm=primary_llm,
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
    def publish_to_discord(self) -> Task:
        return Task(
            config=self.tasks_config["publish_to_discord"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Reporter Crew pipeline. Note: Generate Report task is omitted here as it's assumed to run in another place or replaced by the incoming context."""
        return Crew(
            agents=[self.translator(), self.discord_publisher()],
            tasks=[self.translate_report(), self.publish_to_discord()],
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
