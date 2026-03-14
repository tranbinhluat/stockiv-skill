"""
Director Crew - Quality Control & Fraud Detection Authority

The Director challenges every analysis with forensic precision, verifying
methodology, detecting anomalies, validating evidence, and ensuring only
accurate, complete, and well-supported analysis reaches publication.

Decision authority: [APPROVED], [REJECTED], [MORE_INFO_NEEDED]
"""

from pydantic import BaseModel, Field
from typing import Optional
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
import os

from stockiv.crews.director.models import DirectorDecision


# Wrapper around FileReadTool to avoid Qwen string-serialization bug
# (Qwen passes 'None' string instead of null for optional int params,
#  causing Pydantic validation failure in FileReadToolSchema)
@tool("read_file")
def read_file(file_path: str) -> str:
    """Read the full content of a file given its absolute path."""
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


class DirectorCrewInputs(BaseModel):
    stock_symbols: Optional[str] = Field(
        default=None, description="The stock ticker symbol being analyzed."
    )
    synthesis_report_path: Optional[str] = Field(
        default=None,
        description="Path to the Synthesizer's versioned GCCP report file.",
    )
    review_output_path: Optional[str] = Field(
        default=None, description="Path where Director writes their review markdown."
    )
    financial_summary_path: Optional[str] = Field(
        default=None,
        description="Path to the financial summary data (source of truth from database). "
        "Director uses this to cross-check Synthesizer's numbers.",
    )


from stockiv.agents import advanced_llm  # noqa: E402


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
            tools=[read_file],
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

    def run(self, inputs: DirectorCrewInputs):
        """
        Executes the Director Crew with strongly typed inputs.
        Writes the Director's review as rich markdown via DirectorDecision.to_markdown().
        """
        result = self.crew().kickoff(inputs=inputs.model_dump())

        # Write Director's structured review to markdown
        if inputs.review_output_path:
            try:
                os.makedirs(os.path.dirname(inputs.review_output_path), exist_ok=True)
                decision_obj = result.pydantic
                if decision_obj and isinstance(decision_obj, DirectorDecision):
                    review_md = decision_obj.to_markdown()
                else:
                    # Fallback if pydantic parsing failed
                    review_md = (
                        "# Director Review\n\n"
                        "## ⚠️ Pydantic Parsing Failed\n\n"
                        f"## Raw Output\n\n{result.raw}\n"
                    )

                with open(inputs.review_output_path, "w", encoding="utf-8") as f:
                    f.write(review_md)
                print(f"✅ Director review saved to: {inputs.review_output_path}")
            except Exception as e:
                print(f"⚠️ Failed to save Director review: {e}")

        return result
