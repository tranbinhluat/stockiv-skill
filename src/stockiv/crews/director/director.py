"""
Director Crew - Quality Control & Fraud Detection Authority

The Director challenges every analysis with forensic precision, verifying
methodology, detecting anomalies, validating evidence, and ensuring only
accurate, complete, and well-supported analysis reaches publication.

Decision authority: [APPROVED], [REJECTED], [MORE_INFO_NEEDED]
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import primary_llm
from stockiv.crews.director.models import DirectorDecision


@CrewBase
class DirectorCrew:
    """Director Crew - Quality Control & Fraud Detection"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def director(self) -> Agent:
        return Agent(
            config=self.agents_config["director"],
            llm=primary_llm,
        )

    @task
    def validate_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["validate_analysis"],
            output_pydantic=DirectorDecision,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Director Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
