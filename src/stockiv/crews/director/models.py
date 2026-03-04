"""
Director Crew Output Models

Structured output models for the Director's validation decisions.
"""

from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class Anomaly(BaseModel):
    """A detected financial or governance anomaly."""

    category: str = Field(
        description="Category: revenue, margins, balance_sheet, cash_flow, equity, related_parties, governance"
    )
    description: str = Field(description="Brief description of the anomaly")
    data: str = Field(description="Specific numbers from statements")
    question: str = Field(description="Probing question for clarification")
    required: str = Field(description="What must be provided to address the anomaly")


class FinancialStatementVerification(BaseModel):
    """Verification status of required financial statements."""

    income_statement: bool = Field(
        description="Income Statement (3-5 years) provided and reviewed"
    )
    balance_sheet: bool = Field(
        description="Balance Sheet (3-5 years) provided and reviewed"
    )
    cash_flow_statement: bool = Field(
        description="Cash Flow Statement (3-5 years) provided and reviewed"
    )
    notes_reviewed: bool = Field(
        description="Notes to Financial Statements reviewed for anomalies"
    )


class MethodologyCheck(BaseModel):
    """Methodology validation results."""

    style_verified: bool = Field(
        description="Correct investment style used (Graham, Greenblatt, Lynch)"
    )
    all_criteria_evaluated: bool = Field(
        description="All criteria evaluated (Graham=9, Greenblatt=5)"
    )
    scoring_correct: bool = Field(description="Scoring calculated correctly")
    tier_comparison_valid: bool = Field(
        description="Tier comparison valid (same tier only)"
    )
    industry_context_applied: bool = Field(
        description="Industry-specific factors considered"
    )


class AccuracyCheck(BaseModel):
    """Accuracy validation results."""

    numbers_sourced: bool = Field(description="All numbers traceable to source")
    data_current: bool = Field(description="Data is current (not stale)")
    calculations_correct: bool = Field(description="Calculations verified accurate")
    peer_comparison_valid: bool = Field(
        description="Peer comparison valid (same tier and industry)"
    )


class CompletenessCheck(BaseModel):
    """Completeness validation results."""

    all_criteria_checked: bool = Field(
        description="All investment style criteria evaluated"
    )
    risks_identified: bool = Field(description="Risk factors identified and analyzed")
    red_flags_reported: bool = Field(description="Red flags reported (if they exist)")
    downside_considered: bool = Field(description="Downside scenarios analyzed")


class EvidenceCheck(BaseModel):
    """Evidence validation results."""

    pdfs_provided: bool = Field(description="PDF documents attached or linked")
    page_references: bool = Field(
        description="Page references provided for all key numbers"
    )
    excel_model: bool = Field(description="Excel model with formulas provided")
    primary_sources: bool = Field(
        description="Primary sources used (annual reports, filings)"
    )


class DirectorDecision(BaseModel):
    """
    Director's validation decision for stock analysis.

    This structured output enables the Orchestrator to parse decisions
    programmatically and route accordingly (APPROVED → Reporter, REJECTED → fix,
    MORE_INFO_NEEDED → clarification).
    """

    decision: Literal["APPROVED", "REJECTED", "MORE_INFO_NEEDED"] = Field(
        description="Final decision: APPROVED (ready for publication), REJECTED (fatal flaws), "
        "MORE_INFO_NEEDED (clarification required)"
    )
    ticker: str = Field(description="Stock ticker symbol analyzed")
    style: str = Field(
        description="Investment style applied: Graham, Greenblatt, or Lynch"
    )

    # Financial Statements (REQUIRED)
    financial_statements: FinancialStatementVerification = Field(
        description="Verification of required financial statements"
    )

    # Anomaly Detection
    anomalies: List[Anomaly] = Field(
        default_factory=list,
        description="List of detected anomalies requiring clarification",
    )

    # Validation Checks
    methodology: MethodologyCheck = Field(description="Methodology validation results")
    accuracy: AccuracyCheck = Field(description="Accuracy validation results")
    completeness: CompletenessCheck = Field(
        description="Completeness validation results"
    )
    evidence: EvidenceCheck = Field(description="Evidence validation results")

    # Detailed Feedback
    methodology_failures: List[str] = Field(
        default_factory=list, description="Specific methodology failures identified"
    )
    accuracy_failures: List[str] = Field(
        default_factory=list, description="Specific accuracy failures identified"
    )
    completeness_failures: List[str] = Field(
        default_factory=list, description="Specific completeness failures identified"
    )
    evidence_failures: List[str] = Field(
        default_factory=list, description="Specific evidence failures identified"
    )

    # Summary
    feedback_summary: str = Field(
        description="Human-readable summary of the decision and key findings"
    )

    # Optional routing guidance
    next_steps: Optional[List[str]] = Field(
        default=None,
        description="Specific next steps for REJECTED or MORE_INFO_NEEDED decisions",
    )

    def to_markdown(self) -> str:
        """Format the decision as a markdown report for human review."""
        lines = [
            f"# [{self.decision}]",
            "",
            f"**Ticker:** {self.ticker}",
            f"**Style:** {self.style}",
            "",
        ]

        # Financial Statements
        lines.append("## ✅ Financial Statements Verified:")
        fs = self.financial_statements
        checks = [
            ("Income Statement", fs.income_statement),
            ("Balance Sheet", fs.balance_sheet),
            ("Cash Flow Statement", fs.cash_flow_statement),
            ("Notes Reviewed", fs.notes_reviewed),
        ]
        for name, verified in checks:
            status = "✅" if verified else "❌"
            lines.append(f"- {status} {name}")
        lines.append("")

        # Anomalies
        if self.anomalies:
            lines.append("## 🔍 Anomalies Detected:")
            for i, anomaly in enumerate(self.anomalies, 1):
                lines.append(f"\n### {i}. {anomaly.category}")
                lines.append(f"📊 **Data:** {anomaly.data}")
                lines.append(f"❓ **Question:** {anomaly.question}")
                lines.append(f"📋 **Required:** {anomaly.required}")
            lines.append("")
        else:
            lines.append("## ✅ Anomaly Scan: No anomalies detected\n")

        # Validation Checks
        lines.append("## ✅ Methodology Verified:")
        meth = self.methodology
        lines.append(f"- Style verified: {'✅' if meth.style_verified else '❌'}")
        lines.append(
            f"- All criteria evaluated: {'✅' if meth.all_criteria_evaluated else '❌'}"
        )
        lines.append(f"- Scoring correct: {'✅' if meth.scoring_correct else '❌'}")
        lines.append(
            f"- Tier comparison valid: {'✅' if meth.tier_comparison_valid else '❌'}"
        )
        lines.append(
            f"- Industry context applied: {'✅' if meth.industry_context_applied else '❌'}"
        )
        lines.append("")

        # Failures by category
        if self.methodology_failures:
            lines.append("### ❌ Methodology Failures:")
            for failure in self.methodology_failures:
                lines.append(f"- {failure}")
            lines.append("")

        if self.accuracy_failures:
            lines.append("### ❌ Accuracy Failures:")
            for failure in self.accuracy_failures:
                lines.append(f"- {failure}")
            lines.append("")

        if self.completeness_failures:
            lines.append("### ❌ Completeness Failures:")
            for failure in self.completeness_failures:
                lines.append(f"- {failure}")
            lines.append("")

        if self.evidence_failures:
            lines.append("### ❌ Evidence Failures:")
            for failure in self.evidence_failures:
                lines.append(f"- {failure}")
            lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append(self.feedback_summary)
        lines.append("")

        # Next steps (if any)
        if self.next_steps:
            lines.append("## Next Steps")
            for step in self.next_steps:
                lines.append(f"- {step}")
            lines.append("")

        # Approval message
        if self.decision == "APPROVED":
            lines.append(
                "\n---\n**Analysis withstands scrutiny. Ready for publication.**"
            )
        elif self.decision == "REJECTED":
            lines.append("\n---\n**Not acceptable. Address failures and resubmit.**")
        else:  # MORE_INFO_NEEDED
            lines.append(
                "\n---\n**Clarification required. Address items and resubmit.**"
            )

        return "\n".join(lines)
