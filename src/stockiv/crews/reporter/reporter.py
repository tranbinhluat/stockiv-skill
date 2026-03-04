"""
Reporter Crew - Generates comprehensive reports.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import primary_llm


@CrewBase
class ReporterCrew:
    """Reporter Crew - Report Generation"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["reporter"],
            llm=primary_llm,
        )

    @task
    def generate_report(self) -> Task:
        return Task(
            config=self.tasks_config["generate_report"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Reporter Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
