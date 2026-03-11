"""
Director Crew - Quality Control & Fraud Detection Authority

The Director challenges every analysis with forensic precision, verifying
methodology, detecting anomalies, validating evidence, and ensuring only
accurate, complete, and well-supported analysis reaches publication.

Decision authority: [APPROVED], [REJECTED], [MORE_INFO_NEEDED]
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
import os


class DirectorCrewInputs(BaseModel):
    stock_symbols: Optional[str] = Field(
        default=None, description="The stock ticker symbol being analyzed."
    )
    analysis: Optional[str] = Field(
        default=None,
        description="The raw synthesized analysis text (legacy, for non-file mode).",
    )
    synthesis_report_path: Optional[str] = Field(
        default=None,
        description="Path to the Synthesizer's versioned GCCP report file.",
    )
    review_output_path: Optional[str] = Field(
        default=None, description="Path where Director writes their review markdown."
    )
    evidence_rules: Optional[str] = Field(
        default=None, description="Custom evidence extraction or verification rules."
    )
    financial_rules: Optional[str] = Field(
        default=None, description="Custom financial logic rules for validation."
    )


from stockiv.agents import advanced_llm  # noqa: E402


class ValidationDecision(BaseModel):
    decision: Literal["APPROVED", "REJECTED", "MORE_INFO_NEEDED"] = Field(
        description="The final decision on the analysis quality."
    )
    reasoning: str = Field(
        description="Detailed explanation of why the analysis was approved, rejected, or needs more info."
    )


@CrewBase
class DirectorCrew:
    """Director Crew - Quality Control & Fraud Detection"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def director(self) -> Agent:
        return Agent(
            config=self.agents_config["director"],
            llm=advanced_llm,
            tools=[FileReadTool()],
        )

    @task
    def validate_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["validate_analysis"],
            output_pydantic=ValidationDecision,
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

    def run(self, inputs: DirectorCrewInputs):
        """
        Executes the Director Crew with strongly typed inputs.
        Writes the Director's review to a markdown file if review_output_path is provided.
        """
        result = self.crew().kickoff(inputs=inputs.model_dump())

        # Write Director's full review to markdown if output path is specified
        if inputs.review_output_path:
            try:
                os.makedirs(os.path.dirname(inputs.review_output_path), exist_ok=True)
                decision_obj = result.pydantic
                review_md = "# Director Review\n\n"
                if decision_obj:
                    review_md += f"**Decision:** {decision_obj.decision}\n\n"
                    review_md += f"## Reasoning\n\n{decision_obj.reasoning}\n"
                else:
                    review_md += f"## Raw Output\n\n{result.raw}\n"

                with open(inputs.review_output_path, "w", encoding="utf-8") as f:
                    f.write(review_md)
                print(f"✅ Director review saved to: {inputs.review_output_path}")
            except Exception as e:
                print(f"⚠️ Failed to save Director review: {e}")

        return result
