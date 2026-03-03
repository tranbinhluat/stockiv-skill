"""
Collector Crew - Gathers stock data from various sources.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class CollectorCrew:
    """Collector Crew - Data Collection"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def data_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["data_collector"],
        )

    @task
    def collect_stock_data(self) -> Task:
        return Task(
            config=self.tasks_config["collect_stock_data"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Collector Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
