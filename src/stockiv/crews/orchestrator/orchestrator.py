"""
Orchestrator Crew - Routing logic classification agent.
"""

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from stockiv.agents.base import orchestrator_llm

# We define the output schema for the routing task here
from pydantic import BaseModel, Field
from typing import Optional


class OrchestratorCrewInputs(BaseModel):
    request: Optional[str] = Field(
        default=None,
        description="The raw natural language user request to orchestrate.",
    )


class TickerExtraction(BaseModel):
    """LLM decision output dictating if a ticker was found."""

    is_valid: bool = Field(
        description="True if the request is asking to analyze a specific stock/company, False otherwise."
    )
    target_ticker: str = Field(
        description="The target stock ticker (e.g. 'FPT', 'AAPL'). Empty if not found."
    )


@CrewBase
class OrchestratorCrew:
    """Orchestrator Crew - Classifies user requests to route to downstream Flow paths"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def router(self) -> Agent:
        return Agent(
            config=self.agents_config["router"],
            llm=orchestrator_llm,
        )

    @task
    def routing_task(self) -> Task:
        return Task(
            config=self.tasks_config["routing_task"],
            output_pydantic=TickerExtraction,
            agent=self.router(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def run(self, inputs: OrchestratorCrewInputs):
        """
        Executes the Orchestrator Crew with strongly typed inputs.
        """
        return self.crew().kickoff(inputs=inputs.model_dump())
