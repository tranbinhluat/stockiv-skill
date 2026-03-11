"""
Synthesizer Crew - Interprets and evaluates data directly against the GCCP framework.

Uses Process.hierarchical with a manager agent that delegates to workers.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool

from pydantic import BaseModel, Field
from typing import Optional

from stockiv.agents.base import light_llm, advanced_llm
from stockiv.config.paths import PROCESSED_DIR, PROCESSED_ANNUAL_REPORTS_DIR
from stockiv.knowledge.base import kb
from crewai_tools import FileReadTool, DirectoryReadTool

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
            return f"Execution successful. Output:\n{result.stdout}"
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

    stock_symbol: str = Field(..., description="The stock symbol being evaluated.")
    current_metrics: str = Field(
        ...,
        description="The current trading price, current date, and active market cap.",
    )
    quantitative_metrics_summary: str = Field(
        ...,
        description="A markdown table citing the exact financial metrics (revenue, profit, debt, margins) you extracted from the database.",
    )
    quantitative_anomaly_flags: str = Field(
        ...,
        description="Explicitly detail any anomalies YOU found in the database metrics (e.g., sudden margin drops, debt spikes, or bizarre ROE). State 'No quantitative anomalies detected' if the numbers are stable.",
    )

    # Business Model
    business_model_is_good: bool = Field(
        ...,
        description="Does the company have a good, simple, and focused business model?",
    )
    business_model_input_analysis: str = Field(
        ..., description="Analysis of raw materials and sourcing."
    )
    business_model_output_analysis: str = Field(
        ..., description="Analysis of product, customers, and revenue streams."
    )
    business_model_core_engine_analysis: str = Field(
        ..., description="Analysis of factories, workforce, and distribution network."
    )

    # Management & Governance
    management_is_good: bool = Field(
        ..., description="Is the management reputed and shareholder-aligned?"
    )
    management_analysis: str = Field(
        ..., description="Analysis of shareholder structure, board, and reputation."
    )

    # Industry Analysis
    industry_classification: str = Field(
        ...,
        description="Classification of the industry (Slow, Sustainable, Fast, Cyclical).",
    )
    industry_dynamics_analysis: str = Field(
        ...,
        description="Deep analysis of the industry risks and tailwinds, explicitly incorporating qualitative data from the sentiment reports.",
    )

    # Financial Health
    is_good: bool = Field(
        ...,
        description="Does the financial health meet the minimum requirements (e.g., ROE > 15%, ROA > 6%, OCF > Net Income)?",
    )
    capital_structure: str = Field(
        ..., description="Analysis of debt vs equity and asset location."
    )
    profitability: str = Field(
        ..., description="Analysis of Gross/Operating/Net Margins, ROE, and ROA."
    )
    cash_generation: str = Field(
        ..., description="Analysis of OCF vs Net Income and FCF Margin."
    )
    forensic_anomalies: str = Field(
        ...,
        description="Analysis of accounting anomalies (e.g., related party transactions, inventory bloat, fake revenue) based on the financial reading guide. Note: Requires Annual Report Notes.",
    )

    # Valuation & Margin of Safety
    valuation_is_cheap: bool = Field(
        ...,
        description="Is the price cheap relative to its growth, assets, and market context?",
    )
    market_phase_context: str = Field(
        ...,
        description="Current market phase (Crisis, Fair, Bubble) and how it affects the valuation.",
    )
    investment_criteria_analysis: str = Field(
        ...,
        description="Explicit computation of specific investment criteria: Benjamin Graham's safe conditions (e.g. P/E * P/B < 22.5) OR Peter Lynch's classifications (e.g. PEG ratio for Fast Growers).",
    )
    competitive_peer_comparison: str = Field(
        ...,
        description="Explicit benchmarking of the company's valuation metrics against its sector peers or an explanation of its monopoly status.",
    )
    relative_valuation_analysis: str = Field(
        ...,
        description="Analysis of P/E, P/B, and EV/EBITDA against sector benchmarks and growth rate.",
    )
    margin_of_safety_analysis: str = Field(
        ..., description="Conclusion on Margin of Safety based on market phase."
    )

    # Summary and Suggestions
    summary_of_findings: str = Field(
        ...,
        description="A final BLUF outlining the overall facts found during synthesis without stating a definitive pass/fail decision.",
    )
    actionable_suggestion: str = Field(
        ...,
        description="A clear, direct action recommendation based on the current Margin of Safety (e.g., 'BUY NOW', 'WAIT FOR P/E TO DROP TO 14x', 'AVOID').",
    )
    calculated_target_price: str = Field(
        ...,
        description="Explicit calculation of the Fair Value and the suggested Buy Price after applying the required Margin of Safety (MoS) discount based on the market context and business risks.",
    )
    critical_warnings: str = Field(
        ...,
        description="Explicitly state 'What to wait for' and 'What to be careful about' regarding this investment.",
    )
    delegated_visuals: str = Field(
        ...,
        description="Links or descriptions of embedded visuals/tables delegated to the Data Specialist.",
    )
    citations_and_footnotes: str = Field(
        ...,
        description="Write the detailed footnote definitions here (e.g., '[^1]: According to... (Source: SQLite DB)'). If no footnotes were used, leave this empty, but you MUST use footnotes for your quantitative claims.",
    )

    def to_markdown(self) -> str:
        """Converts the structured Pydantic model into a beautifully formatted Markdown report."""

        def bool_to_badge(val: bool) -> str:
            return "🟢 **PASS**" if val else "🔴 **FAIL**"

        md = f"# GCCP Synthesis Report: {self.stock_symbol}\n\n"
        md += f"**Current Metrics:** {self.current_metrics}\n"
        md += f"**Industry Classification:** {self.industry_classification}\n\n"

        md += "## Part I: Quantitative Summary & Industry Dynamics\n"
        md += f"{self.quantitative_metrics_summary}\n\n"
        md += f"### Quantitative Anomaly Flags:\n{self.quantitative_anomaly_flags}\n\n"
        md += f"### Industry Context & Sentiment Risk:\n{self.industry_dynamics_analysis}\n\n"

        md += f"## Part II: Good Company (Qualitative) | Overall Status: {bool_to_badge(self.business_model_is_good and self.management_is_good)}\n"
        md += f"### 1. Business Model & Moat | Status: {bool_to_badge(self.business_model_is_good)}\n"
        md += f"- **Input (Raw Materials):** {self.business_model_input_analysis}\n"
        md += (
            f"- **Output (Product/Customers):** {self.business_model_output_analysis}\n"
        )
        md += f"- **Core Engine:** {self.business_model_core_engine_analysis}\n\n"

        md += f"### 2. Management & Governance | Status: {bool_to_badge(self.management_is_good)}\n"
        md += f"- **Analysis:** {self.management_analysis}\n\n"

        md += f"## Part III: Good Company (Quantitative) | Financial Health Status: {bool_to_badge(self.is_good)}\n"
        md += f"- **Capital Structure (Debt):** {self.capital_structure}\n"
        md += f"- **Profitability (Margins/ROE):** {self.profitability}\n"
        md += f"- **Cash Generation (OCF/FCF):** {self.cash_generation}\n"
        md += f"- **Accounting Forensics (Anomalies):** {self.forensic_anomalies}\n\n"

        md += f"## Part IV: Cheap Price | Overall Status: {bool_to_badge(self.valuation_is_cheap)}\n"
        md += "### Market Phase & Criteria Validation\n"
        md += f"- **Market Context:** {self.market_phase_context}\n"
        md += f"- **Strategy Criteria (Graham/Lynch):** {self.investment_criteria_analysis}\n"
        md += f"- **Peer Comparison:** {self.competitive_peer_comparison}\n"
        md += f"- **Relative Valuation:** {self.relative_valuation_analysis}\n"
        md += f"- **Margin of Safety:** {self.margin_of_safety_analysis}\n\n"

        md += "## Part V: Final Synthesis Summary & Actionable Advice\n"
        md += f"**Overall BLUF:** {self.summary_of_findings}\n\n"

        md += "### Valuation Target & Margin of Safety\n"
        md += f"- **Target/Suggested Entry Price:** {self.calculated_target_price}\n\n"

        md += "### Actionable Suggestion\n"
        md += f"> **{self.actionable_suggestion}**\n\n"

        md += "### Critical Warnings & Observations\n"
        md += f"{self.critical_warnings}\n\n"

        md += "## Part VI: Visuals, Footnotes and Citation Sources\n"
        md += f"{self.delegated_visuals}\n\n"
        md += f"{self.citations_and_footnotes}\n"

        return md


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
# Crew Definition (Hierarchical Manager Pattern)
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
                FetchPeerComparisonsTool(),
                FileReadTool(),
                sentiment_dir_tool,
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
            tools=[annual_report_dir_tool, read_file],
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

    @crew
    def crew(self) -> Crew:
        """Creates the Synthesizer crew with hierarchical manager delegation."""
        # Filter out the manager from the worker list (same pattern as CollectorCrew)
        worker_agents = [
            a
            for a in self.agents
            if a.role != self.agents_config["synthesizer_manager"]["role"]
        ]

        return Crew(
            agents=worker_agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.synthesizer_manager(),
            verbose=True,
            tracing=True,
        )

    def run(self, inputs: SynthesizerCrewInputs):
        """
        Executes the Synthesizer Crew with strongly typed inputs.
        """
        return self.crew().kickoff(inputs=inputs.model_dump())
