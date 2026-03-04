"""
Quant Analyst Crew - Performs quantitative analysis on stock data.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import primary_llm


@CrewBase
class QuantAnalystCrew:
    """Quant Analyst Crew - Quantitative Analysis"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def quant_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["quant_analyst"],
            llm=primary_llm,
        )

    @task
    def analyze_metrics(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_metrics"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Quant Analyst Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
