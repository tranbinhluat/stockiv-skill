"""
Synthesizer Crew - Interprets and evaluates data directly against the GCCP framework.

Uses Process.sequential where agents execute specific tasks, but retain delegation rights.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.tools import tool

from pydantic import BaseModel, Field
from typing import Optional

from stockiv.agents.base import light_llm, advanced_llm
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
    FetchRecentFinancialsTool,
    FetchPeerComparisonsTool,
    FetchCurrentMarketSnapshotTool,
    CalculateFrameworkMetricsTool,
)
from tools.brave_tools import search_market_context  # noqa: E402


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


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
    revision_notes: Optional[str] = Field(
        default=None,
        description="Detailed notes on what was revised based on Director's feedback. Do not include this text inside report_markdown.",
    )

    def to_markdown(self, ticker: str = "") -> str:
        """Converts the structured Pydantic model into a beautifully formatted Markdown report."""
        if ticker:
            title = f"# Phân tích Cổ phiếu {ticker} theo Khung GCCP"
        else:
            title = "# Phân tích Cổ phiếu (GCCP)"

        lines = [
            title,
            "",
            "## Key Conclusions",
            f"- **Good Company?** {'🟢 Yes' if self.is_good else '🔴 No'}",
            f"- **Cheap Price?** {'🟢 Yes' if self.valuation_is_cheap else '🔴 No'}",
            f"- **Actionable Suggestion:** **{self.actionable_suggestion}**",
            f"- **Target Price:** {self.calculated_target_price}",
            "",
            "---",
            "",
            self.report_markdown,
        ]

        # revision_notes kept in Pydantic model for internal tracking
        # but NOT included in the user-facing report

        return "\n".join(lines)


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
    """Synthesizer Crew - Sequential GCCP Data Interpreter and Evaluator"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @before_kickoff
    def pre_compile_baseline_metrics(self, inputs: dict) -> dict:
        """
        Deterministically pre-compiles the baseline financial summary before the crew starts.
        Skips this step if we are in a feedback revision loop (report_version > 1).
        """
        report_version = inputs.get("report_version", 1)
        if report_version > 1:
            print(
                f"[SynthesizerCrew] Revision loop active (v{report_version}). Skipping baseline data pre-compilation."
            )
            return inputs

        ticker = str(inputs.get("stock_symbols", ""))
        financial_summary_path = str(inputs.get("financial_summary_path", ""))

        if not ticker or not financial_summary_path:
            print(
                "[SynthesizerCrew] Missing ticker or financial_summary_path. Cannot pre-compile baseline data."
            )
            return inputs

        print(f"[SynthesizerCrew] Pre-compiling baseline metrics for {ticker}...")

        # Manually invoke the tools
        market_snapshot = FetchCurrentMarketSnapshotTool()._run(ticker=ticker)
        recent_financials = FetchRecentFinancialsTool()._run(ticker=ticker)
        peer_comparisons = FetchPeerComparisonsTool()._run(target_ticker=ticker)
        framework_metrics = CalculateFrameworkMetricsTool()._run(ticker=ticker)

        # Assemble the markdown content deterministically
        content = (
            f"{market_snapshot}\n\n"
            f"{recent_financials}\n\n"
            f"{peer_comparisons}\n\n"
            f"{framework_metrics}\n\n"
        )

        # Write to file directly
        try:
            with open(financial_summary_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(
                f"[SynthesizerCrew] Successfully pre-compiled baseline metrics to {financial_summary_path}"
            )
        except Exception as e:
            print(f"[SynthesizerCrew] Error writing pre-compiled data: {e}")

        return inputs

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
    def quantitative_risk_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["quantitative_risk_analyst"],  # type: ignore
            llm=advanced_llm,
            tools=[FileReadTool()],
            reasoning=True,
        )

    @agent
    def data_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["data_specialist"],
            llm=light_llm,
            tools=[
                execute_python_code,
                FileReadTool(),
                append_to_file,
            ],
        )

    @agent
    def forensic_accountant(self) -> Agent:
        annual_report_dir_tool = DirectoryReadTool()
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

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_researcher"],
            llm=light_llm,
            tools=[search_market_context],
        )

    @task
    def detect_quantitative_anomalies(self) -> Task:
        return Task(
            config=self.tasks_config["detect_quantitative_anomalies"],  # type: ignore
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

        Tasks: detect_quantitative_anomalies → forensic_annual_report_review → compile_evaluation_report
        (Baseline metrics are pre-compiled via @before_kickoff hook)
        """
        return Crew(
            agents=self.agents,
            tasks=[
                self.detect_quantitative_anomalies(),
                self.forensic_annual_report_review(),
                self.compile_evaluation_report(),
            ],
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def revision_crew(self) -> Crew:
        """Creates a lean Synthesizer crew for REVISION (feedback loop).

        Tasks: evaluate_feedback ONLY — manager reads feedback + previous report himself.
        Agents: all delegates are included so the manager can delegate data/forensic/search queries.
        """
        return Crew(
            agents=[
                self.synthesizer_manager(),
                self.quantitative_risk_analyst(),
                self.data_specialist(),
                self.forensic_accountant(),
                self.market_researcher(),
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
