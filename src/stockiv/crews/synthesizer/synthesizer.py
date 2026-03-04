"""
Synthesizer Crew - Combines analysis from multiple sources.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stockiv.agents import primary_llm


@CrewBase
class SynthesizerCrew:
    """Synthesizer Crew - Data Synthesis"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config["synthesizer"],
            llm=primary_llm,
        )

    @task
    def synthesize_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["synthesize_analysis"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Synthesizer Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
