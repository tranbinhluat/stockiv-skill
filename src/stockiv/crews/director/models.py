"""
Director Crew Output Models

Simplified, flat output model for the Director's validation decisions.
Replaces the previous 7-nested-sub-model structure with 5 flat booleans
and 1 consolidated failures list.
"""

import json

from pydantic import BaseModel, Field, field_validator
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


class DirectorDecision(BaseModel):
    """
    Director's validation decision for stock analysis.

    Flat structure with 5 boolean checks. The flow (report_loop.py) reads
    decision, feedback_summary, and next_steps for routing. The rest is
    for the to_markdown() review file consumed by the Synthesizer on revision.
    """

    decision: Literal["APPROVED", "REJECTED", "MORE_INFO_NEEDED"] = Field(
        description="Final decision: APPROVED (ready for publication), REJECTED (fatal flaws), "
        "MORE_INFO_NEEDED (clarification required)"
    )
    ticker: str = Field(description="Stock ticker symbol analyzed")
    style: str = Field(
        description="Investment style applied: Graham, Greenblatt, Lynch, or All"
    )

    # --- Flat validation checks (replaces 5 nested sub-models) ---
    financial_data_verified: bool = Field(
        description="Were 3-5 years of Income Statement, Balance Sheet, and Cash Flow reviewed?"
    )
    methodology_sound: bool = Field(
        description="Correct investment style applied? Criteria evaluated? Peer tier matching correct?"
    )
    numbers_accurate: bool = Field(
        description="Calculations correct and verified against the Financial Ground Truth data?"
    )
    analysis_complete: bool = Field(
        description="All relevant criteria checked? Risks identified? Red flags reported? Downside considered?"
    )
    logic_and_reasoning_sound: bool = Field(
        description="Are the conclusions logically consistent with the data? (e.g., Target rating matches valuation/MoS, negative sentiment isn't ignored)."
    )
    evidence_traceable: bool = Field(
        description="Claims traceable to SQLite DB, financial summary file, or annual reports? "
        "Inline citations like [Source: SQLite Database] or [Financial Summary] count as valid evidence."
    )

    # Anomaly Detection (kept — core value-add of the Director)
    anomalies: List[Anomaly] = Field(
        default_factory=list,
        description="List of detected anomalies requiring clarification",
    )

    # Consolidated failures list (replaces 4 separate *_failures lists)
    failures: List[str] = Field(
        default_factory=list,
        description="Specific failures identified across methodology, accuracy, completeness, or evidence",
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

    # --- Validators to handle LLM returning stringified JSON ---
    @field_validator("next_steps", "failures", mode="before")
    @classmethod
    def _parse_stringified_list(cls, v):
        """LLMs sometimes return list fields as stringified JSON strings."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            return [v]  # Wrap single string as 1-item list
        return v

    @field_validator("anomalies", mode="before")
    @classmethod
    def _parse_stringified_anomalies(cls, v):
        """LLMs sometimes return anomalies as a stringified JSON string."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
        return v

    def to_markdown(self) -> str:
        """Format the decision as a markdown report for human review."""
        lines = [
            f"# [{self.decision}]",
            "",
            f"**Ticker:** {self.ticker}",
            f"**Style:** {self.style}",
            "",
        ]

        # Validation Checks
        lines.append("## Validation Checks")
        checks = [
            ("Financial Data Verified", self.financial_data_verified),
            ("Methodology Sound", self.methodology_sound),
            ("Numbers Accurate", self.numbers_accurate),
            ("Analysis Complete", self.analysis_complete),
            ("Logic & Reasoning Sound", self.logic_and_reasoning_sound),
            ("Evidence Traceable", self.evidence_traceable),
        ]
        for name, passed in checks:
            status = "✅" if passed else "❌"
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

        # Failures
        if self.failures:
            lines.append("## ❌ Failures:")
            for failure in self.failures:
                lines.append(f"- {failure}")
            lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append(self.feedback_summary)
        lines.append("")

        # Next steps (if any)
        if self.next_steps:
            lines.append("## Next Steps")
            for step in self.next_steps or []:
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
