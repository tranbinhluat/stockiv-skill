"""
Orchestrator Crew - Coordinates all crews in the workflow.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import glm_llm


@CrewBase
class OrchestratorCrew:
    """Orchestrator Crew - Workflow Orchestration"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config["orchestrator"],
            llm=glm_llm,
        )

    @task
    def orchestrate_workflow(self) -> Task:
        return Task(
            config=self.tasks_config["orchestrate_workflow"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Orchestrator Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True
        )
