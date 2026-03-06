"""
Synthesizer Crew - Interprets and evaluates data directly against the GCCP framework.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from pydantic import BaseModel, Field

from stockiv.agents.base import get_llm
from stockiv.knowledge.base import kb
from crewai_tools import FileReadTool
import sys
from pathlib import Path

# Add project root to sys.path so we can import from `tools` directory
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.sqlite_tools import QueryStockDatabaseTool  # noqa: E402


class SynthesizerReport(BaseModel):
    """The final structured evaluation report from the Synthesizer crew."""

    stock_symbol: str = Field(..., description="The stock symbol being evaluated.")
    industry_classification: str = Field(
        ...,
        description="Classification of the industry (Slow, Sustainable, Fast, Cyclical).",
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
    relative_valuation_analysis: str = Field(
        ...,
        description="Analysis of P/E, P/B, and EV/EBITDA against sector benchmarks and growth rate.",
    )
    margin_of_safety_analysis: str = Field(
        ..., description="Conclusion on Margin of Safety based on market phase."
    )

    # Summary
    summary_of_findings: str = Field(
        ...,
        description="A final BLUF outlining the overall facts found during synthesis without stating a definitive pass/fail decision.",
    )
    delegated_visuals: str = Field(
        ...,
        description="Links or descriptions of embedded visuals/tables delegated to the Visualization Specialist.",
    )

    def to_markdown(self) -> str:
        """Converts the structured Pydantic model into a beautifully formatted Markdown report."""

        def bool_to_badge(val: bool) -> str:
            return "🟢 **PASS**" if val else "🔴 **FAIL**"

        md = f"# GCCP Synthesis Report: {self.stock_symbol}\n\n"
        md += f"**Industry Classification:** {self.industry_classification}\n\n"

        md += f"## 1. Business Model & Moat | Status: {bool_to_badge(self.business_model_is_good)}\n"
        md += f"- **Input (Raw Materials):** {self.business_model_input_analysis}\n"
        md += (
            f"- **Output (Product/Customers):** {self.business_model_output_analysis}\n"
        )
        md += f"- **Core Engine:** {self.business_model_core_engine_analysis}\n\n"

        md += f"## 2. Management & Governance | Status: {bool_to_badge(self.management_is_good)}\n"
        md += f"- **Analysis:** {self.management_analysis}\n\n"

        md += f"## 3. Financial Health & Forensics | Status: {bool_to_badge(self.is_good)}\n"
        md += f"- **Capital Structure (Debt):** {self.capital_structure}\n"
        md += f"- **Profitability (Margins/ROE):** {self.profitability}\n"
        md += f"- **Cash Generation (OCF/FCF):** {self.cash_generation}\n"
        md += f"- **Accounting Forensics (Anomalies):** {self.forensic_anomalies}\n\n"

        md += f"## 4. Valuation & Margin of Safety | Status: {bool_to_badge(self.valuation_is_cheap)}\n"
        md += f"- **Market Phase:** {self.market_phase_context}\n"
        md += f"- **Relative Valuation:** {self.relative_valuation_analysis}\n"
        md += f"- **Margin of Safety:** {self.margin_of_safety_analysis}\n\n"

        md += "## 5. Final Synthesis Summary\n"
        md += f"{self.summary_of_findings}\n\n"

        md += "## 6. Delegated Visualizations\n"
        md += f"{self.delegated_visuals}\n"

        return md


@CrewBase
class SynthesizerCrew:
    """Synthesizer Crew - Monolithic GCCP Data Interpreter and Evaluator"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def lead_synthesizer(self) -> Agent:
        config = self.agents_config["lead_synthesizer"].copy()

        # Inject the entire GCCP Framework explicit text into the agent's backstory
        kb_text = f"--- FRAMEWORK ---\n{kb.framework}\n\n--- CRITERIA ---\n{kb.criteria}\n\n--- INDUSTRY GUIDES ---\n{kb.industry_guides}\n\n--- EVIDENCE STANDARD ---\n{kb.evidence_standard}\n\n--- FINANCIAL READING GUIDE ---\n{kb.financial_reading_guide}"
        config["backstory"] = config["backstory"].replace("{gccp_knowledge}", kb_text)

        return Agent(
            config=config,
            llm=get_llm("qwen3-max-2026-01-23"),
            tools=[FileReadTool(), QueryStockDatabaseTool()],
        )

    @agent
    def visualization_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["visualization_specialist"],
            llm=get_llm("qwen3-max-2026-01-23"),
        )

    @task
    def compile_evaluation_report(self) -> Task:
        return Task(
            config=self.tasks_config["compile_evaluation_report"],
            output_pydantic=SynthesizerReport,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the monolithic Synthesizer Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
