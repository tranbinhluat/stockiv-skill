"""
Synthesizer Crew - Interprets and evaluates data directly against the GCCP framework.

Uses Process.sequential where agents execute specific tasks, but retain delegation rights.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool

from pydantic import BaseModel, Field
from typing import Optional

from stockiv.agents.base import light_llm, advanced_llm
from stockiv.config.paths import PROCESSED_DIR, PROCESSED_ANNUAL_REPORTS_DIR
from stockiv.knowledge.base import kb
from crewai_tools import FileReadTool, DirectoryReadTool, MDXSearchTool

import os
import subprocess
import tempfile


@tool("execute_python_code")
def execute_python_code(code: str) -> str:
    """Execute pandas/matplotlib python code. It runs in a temporary file and returns stdout/stderr. Do NOT use plt.show(), save to a .png file instead."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["uv", "run", "python", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        os.remove(temp_path)

        if result.returncode == 0:
            out = result.stdout
            if len(out) > 6000:
                out = (
                    out[:6000]
                    + "\n\n...[TRUNCATED: Output is too long! Do NOT print entire dataframes with pd.set_option('display.max_rows', None). Use .head(), .tail(), or strictly filter your queries instead.]..."
                )
            return f"Execution successful. Output:\n{out}"
        else:
            return f"Execution failed. Error:\n{result.stderr}"
    except Exception as e:
        return f"Execution error: {str(e)}"


@tool("read_file")
def read_file(file_path: str) -> str:
    """Read the content of a file given its absolute or relative path."""
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


@tool("append_to_file")
def append_to_file(file_path: str, content: str) -> str:
    """Append text or markdown content to an existing file."""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n{content}\n")
        return f"Successfully appended content to {file_path}"
    except Exception as e:
        return f"Failed to append to {file_path}: {str(e)}"


# Import SQLite and search tools
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.sqlite_tools import (  # noqa: E402
    QueryStockDatabaseTool,
    FetchRecentFinancialsTool,
    FetchPeerComparisonsTool,
    FetchCurrentMarketSnapshotTool,
    CalculateFrameworkMetricsTool,
)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class BaselineMetrics(BaseModel):
    """Raw, comprehensive data extraction from the Data Specialist."""

    current_price_data: str = Field(
        ...,
        description="Current trading price of the stock, exact date, and 1-year momentum.",
    )
    current_vnindex: str = Field(
        ..., description="Current VNINDEX value and recent momentum."
    )
    fundamental_ratios: str = Field(
        ...,
        description="Table or list of all recent fundamental ratios (P/E, P/B, ROE, etc).",
    )
    multi_year_comparisons: str = Field(
        ...,
        description="Table or list of financials across the last 4 quarters and max years (if enough data), including YoY growth percentages.",
    )
    peer_competitors: str = Field(
        ...,
        description="Table or list comparing target ratios to top domestic competitors.",
    )

    def to_markdown(self) -> str:
        md = "## Data Specialist Baseline Metrics\n\n"
        md += f"### Current Market Metrics\n{self.current_price_data}\n\n"
        md += f"### VNINDEX Baseline\n{self.current_vnindex}\n\n"
        md += f"### Fundamental Ratios\n{self.fundamental_ratios}\n\n"
        md += f"### Multi-Year Comparisons & YoY\n{self.multi_year_comparisons}\n\n"
        md += f"### Peer Competitors\n{self.peer_competitors}\n"
        return md


class SynthesizerReport(BaseModel):
    """The final structured evaluation report from the Synthesizer crew."""

    is_good: bool = Field(..., description="Overall good company?")
    valuation_is_cheap: bool = Field(..., description="Overall cheap price?")
    actionable_suggestion: str = Field(
        ..., description="Actionable suggestion (BUY, WAIT, AVOID)"
    )
    calculated_target_price: str = Field(
        ..., description="Target price with Margin of Safety"
    )
    report_markdown: str = Field(
        ...,
        description="The FULL detailed markdown report containing all analysis, citations, guidelines, and visuals, formatted comprehensively following the GCCP framework structure.",
    )

    def to_markdown(self) -> str:
        """Converts the structured Pydantic model into a beautifully formatted Markdown report."""
        return self.report_markdown


# ---------------------------------------------------------------------------
# Crew Inputs
# ---------------------------------------------------------------------------


class SynthesizerCrewInputs(BaseModel):
    stock_symbols: Optional[str] = Field(
        default=None, description="The stock ticker symbol being evaluated."
    )
    date: Optional[str] = Field(
        default=None, description="The date of analysis (YYYY-MM-DD)."
    )
    financial_summary_path: Optional[str] = Field(
        default=None, description="File path to load or save the financial summary."
    )
    annual_reports_dir: Optional[str] = Field(
        default=None, description="Directory path to load annual reports from."
    )
    synthesizer_output_dir: Optional[str] = Field(
        default=None, description="Directory path to save the final synthesized report."
    )
    sentiment_dir: Optional[str] = Field(
        default=None,
        description="Directory path to load generated sentiment reports from.",
    )
    ticker_sentiment_path: Optional[str] = Field(
        default=None, description="File path to the ticker-specific sentiment report."
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Path to Director's review file from previous loop. Manager reads this with FileReadTool to address weaknesses.",
    )
    report_version: int = Field(
        default=1,
        description="Version number for the report (incremented on each feedback loop).",
    )


# ---------------------------------------------------------------------------
# Crew Definition (Sequential Pattern)
# ---------------------------------------------------------------------------


@CrewBase
class SynthesizerCrew:
    """Synthesizer Crew - Hierarchical GCCP Data Interpreter and Evaluator"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def synthesizer_manager(self) -> Agent:
        config = self.agents_config["synthesizer_manager"].copy()

        # Inject the entire GCCP Framework text into the agent's backstory
        kb_text = (
            f"--- FRAMEWORK ---\n{kb.framework}\n\n"
            f"--- CRITERIA ---\n{kb.criteria}\n\n"
            f"--- INDUSTRY GUIDES ---\n{kb.industry_guides}\n\n"
            f"--- EVIDENCE STANDARD ---\n{kb.evidence_standard}\n\n"
            f"--- FINANCIAL READING GUIDE ---\n{kb.financial_reading_guide}"
        )
        config["backstory"] = config["backstory"].replace("{gccp_knowledge}", kb_text)

        return Agent(
            config=config,
            llm=advanced_llm,
            tools=[FileReadTool()],
            allow_delegation=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def data_specialist(self) -> Agent:
        sentiment_dir_tool = DirectoryReadTool(
            directory=str(PROCESSED_DIR / "sentiment")
        )
        return Agent(
            config=self.agents_config["data_specialist"],
            llm=light_llm,
            tools=[
                execute_python_code,
                QueryStockDatabaseTool(),
                FetchRecentFinancialsTool(),
                FetchCurrentMarketSnapshotTool(),
                FetchPeerComparisonsTool(),
                CalculateFrameworkMetricsTool(),
                FileReadTool(),
                sentiment_dir_tool,
                append_to_file,
            ],
        )

    @agent
    def forensic_accountant(self) -> Agent:
        annual_report_dir_tool = DirectoryReadTool(
            directory=str(PROCESSED_ANNUAL_REPORTS_DIR)
        )
        return Agent(
            config=self.agents_config["forensic_accountant"],
            llm=light_llm,
            tools=[
                annual_report_dir_tool,
                MDXSearchTool(
                    collection_name="forensic_mdx_collection_v2",
                    config={
                        "embedding_model": {
                            "provider": "sentence-transformer",
                            "config": {"model": "all-MiniLM-L6-v2"},
                        },
                    },
                ),
            ],
            verbose=False,
        )

    @task
    def collect_baseline_metrics(self) -> Task:
        return Task(
            config=self.tasks_config["collect_baseline_metrics"],
        )

    @task
    def forensic_annual_report_review(self) -> Task:
        return Task(
            config=self.tasks_config["forensic_annual_report_review"],
        )

    @task
    def compile_evaluation_report(self) -> Task:
        task_config = self.tasks_config["compile_evaluation_report"].copy()
        schema_str = SynthesizerReport.model_json_schema()
        task_config["description"] += (
            f"\n\nCRITICAL: Your JSON output MUST explicitly follow this flat schema:\n{schema_str}"
        )
        return Task(
            config=task_config,
        )

    def _build_evaluate_feedback_task(self) -> Task:
        """Build the evaluate_feedback task (not decorated — used only in revision_crew)."""
        task_config = self.tasks_config["evaluate_feedback"].copy()
        schema_str = SynthesizerReport.model_json_schema()
        task_config["description"] += (
            f"\n\nCRITICAL: Your JSON output MUST explicitly follow this flat schema:\n{schema_str}"
        )
        return Task(
            config=task_config,
            agent=self.synthesizer_manager(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Synthesizer crew for FIRST PASS (full pipeline).

        Tasks: collect_baseline_metrics → forensic_annual_report_review → compile_evaluation_report
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def revision_crew(self) -> Crew:
        """Creates a lean Synthesizer crew for REVISION (feedback loop).

        Tasks: evaluate_feedback ONLY — manager reads feedback + previous report himself.
        Agents: all three are included so the manager can delegate data/forensic queries.
        """
        return Crew(
            agents=[
                self.synthesizer_manager(),
                self.data_specialist(),
                self.forensic_accountant(),
            ],
            tasks=[self._build_evaluate_feedback_task()],
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def run(self, inputs: SynthesizerCrewInputs, revision: bool = False):
        """
        Executes the Synthesizer Crew with strongly typed inputs.

        Args:
            inputs: Crew inputs (paths, ticker, etc.)
            revision: If True, uses revision_crew (evaluate_feedback only).
                      If False, uses crew (full first-pass pipeline).
        """
        if revision:
            return self.revision_crew().kickoff(inputs=inputs.model_dump())
        return self.crew().kickoff(inputs=inputs.model_dump())
