"""
Director Crew - Guides and validates the analysis workflow.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class DirectorCrew:
    """Director Crew - Workflow Direction"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def director(self) -> Agent:
        return Agent(
            config=self.agents_config["director"],
        )

    @task
    def validate_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["validate_analysis"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Director Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
