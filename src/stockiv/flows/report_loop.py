"""
Report Loop Flow - Versioned file-based feedback loop between Synthesizer and Director.

Each loop iteration produces versioned files on disk:
  - {ticker}_GCCP_report_v{N}.md   (Synthesizer output)
  - {ticker}_director_review_v{N}.md (Director review)

Loop Architecture (single-path, no duplicates):
  CrewAI's @listen(or_()) fires only ONCE for non-routers (tracked in
  _fired_or_listeners). Routers are EXEMPT from this guard.

  So the flow uses TWO branches that each run Synthesizer+Director:
    execute_first_pass  → (synth full kickoff + director review)
    handle_revision     → (synth replay + director review)

  The router @router(or_(execute_first_pass, handle_revision)) is the
  only step using or_(), and it loops by returning "loop_back".

Retry Strategy:
  On Director rejection, uses CrewAI's crew.replay() to re-run ONLY the
  compile_evaluation_report task (preserving data extraction context from
  tasks [0] and [1]).
"""

from crewai.flow.flow import Flow, listen, start, router, or_
import os
from pathlib import Path

from stockiv.config.paths import (
    PROCESSED_ANNUAL_REPORTS_DIR,
    PROCESSED_SENTIMENT_MARKET_DIR,
    PROCESSED_SENTIMENT_TICKER_DIR,
    PROCESSED_SYNTHESIZER_DIR,
)
from stockiv.flows.state import PipelineState
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew, SynthesizerCrewInputs
from stockiv.crews.director.director import DirectorCrew, DirectorCrewInputs
from stockiv.crews.director.models import DirectorDecision


class ReportLoopState(PipelineState):
    """State for the Report Loop — extends PipelineState.

    Loop mechanism fields live here as direct attributes.
    Data paths are stored in shared_data (populated by parent flow or initialize_setup).
    """

    # Loop mechanism
    director_feedback_path: str = ""  # Path to Director's    review file
    director_approval: str = "REJECTED"
    loop_count: int = 0
    max_loops: int = 5
    report_version: int = 1

    # Legacy
    synthesized_insights: str = ""


class SynthesizerReporterFlow(Flow[ReportLoopState]):
    """
    Mini flow that orchestrates the Synthesizer Crew and Director Crew in a
    versioned file-based feedback loop.

    First pass:  Full pipeline (baseline_metrics → forensic_review → compile_report)
    Revisions:   Lean pipeline (evaluate_feedback only) — manager reads
                 Director feedback + previous report, fixes weak sections.
    """

    def _is_mocking(self, step_name: str) -> bool:
        """Check if a specific crew/step should be mocked based on state.mock."""
        mock_val = getattr(self.state, "mock", [])
        if isinstance(mock_val, bool):
            return mock_val
        if isinstance(mock_val, str):
            mocks = [m.strip().lower() for m in mock_val.split(",")]
            return "all" in mocks or step_name.lower() in mocks
        if isinstance(mock_val, list):
            mocks = [m.lower() for m in mock_val]
            return "all" in mocks or step_name.lower() in mocks
        return False

    def _build_synthesizer_inputs(self) -> dict:
        """Build the inputs dict for the Synthesizer crew."""
        ticker = self.state.target_ticker
        version = self.state.report_version
        inputs_obj = SynthesizerCrewInputs(
            stock_symbols=ticker,
            date=self.state.shared_data.get("current_date", "2026-03-11"),
            financial_summary_path=self.state.shared_data.get("financial_summary_path")
            or None,
            annual_reports_dir=self.state.shared_data.get("annual_reports_dir") or None,
            synthesizer_output_dir=self.state.shared_data.get("synthesizer_output_dir")
            or None,
            sentiment_dir=self.state.shared_data.get("sentiment_dir") or None,
            ticker_sentiment_path=self.state.shared_data.get("ticker_sentiment_path")
            or None,
            report_version=version,
        )

        # Inject Director's review file path as feedback on retries
        if self.state.director_feedback_path:
            print(
                f"[ReportLoop Flow] 📝 Injecting Director feedback: {self.state.director_feedback_path}"
            )
            inputs_obj.feedback = self.state.director_feedback_path

        return inputs_obj.model_dump()

    @start()
    def initialize_setup(self):
        """Setup loop state and populate centralized paths from stockiv.config.paths.

        Uses setdefault so a parent flow (e.g. DeepDiveFlow) can pre-populate
        shared_data paths before kickoff without being overwritten.
        """
        ticker = self.state.target_ticker.upper()
        if not ticker:
            raise ValueError(
                "target_ticker must be set on state before kicking off SynthesizerReporterFlow."
            )
        self.state.target_ticker = ticker

        print(
            f"\n[ReportLoop Flow] Initializing for {ticker}. "
            f"Max Loops allowed: {self.state.max_loops}"
        )

        # Reset loop counters
        self.state.loop_count = 0
        self.state.report_version = 1

        # No crew state to reset — each kickoff creates a fresh instance

        # --- Populate shared_data paths (centralized defaults) ---
        synthesizer_ticker_dir = PROCESSED_SYNTHESIZER_DIR / ticker
        synthesizer_ticker_dir.mkdir(parents=True, exist_ok=True)
        self.state.shared_data.setdefault(
            "synthesizer_output_dir", str(synthesizer_ticker_dir)
        )
        self.state.shared_data.setdefault(
            "financial_summary_path",
            str(synthesizer_ticker_dir / f"{ticker}_financial_summary.md"),
        )

        # Annual reports
        self.state.shared_data.setdefault(
            "annual_reports_dir", str(PROCESSED_ANNUAL_REPORTS_DIR)
        )

        # Sentiment
        self.state.shared_data.setdefault(
            "sentiment_dir", str(PROCESSED_SENTIMENT_MARKET_DIR)
        )
        ticker_sentiment_dir = PROCESSED_SENTIMENT_TICKER_DIR / ticker
        ticker_sentiment_dir.mkdir(parents=True, exist_ok=True)

        # Find latest weekly sentiment file, fallback to hardcoded name
        sentiment_files = list(ticker_sentiment_dir.glob("*.md"))
        if sentiment_files:
            sentiment_files.sort(reverse=True)
            chosen_sentiment = sentiment_files[0]
        else:
            chosen_sentiment = ticker_sentiment_dir / f"{ticker}_sentiment.md"

        self.state.shared_data.setdefault(
            "ticker_sentiment_path",
            str(chosen_sentiment),
        )

        self.state.history += f"ReportLoop setup complete for {ticker}.\n"
        return self.state.target_ticker

    def _run_synthesizer_mock(self):
        """Mock Synthesizer for testing the loop flow."""
        ticker = self.state.target_ticker
        version = self.state.report_version
        output_dir = self.state.shared_data.get(
            "synthesizer_output_dir", str(PROCESSED_SYNTHESIZER_DIR / ticker)
        )
        os.makedirs(output_dir, exist_ok=True)
        report_path = str(Path(output_dir) / f"{ticker}_GCCP_report_v{version}.md")

        mock_content = f"# MOCK GCCP Synthesis Report: {ticker} (v{version})\n\n"
        mock_content += (
            "This is a simulated report to test the Director feedback loop. "
            "It applies the **All** investment style criteria.\n\n"
        )
        mock_content += "## 1. Business Model & Moat | Status: 🟢 **PASS**\n"
        mock_content += (
            "- **Analysis:** The company shows strong recurring revenue.\n\n"
        )
        mock_content += "## 2. Financial Statements Review\n"
        mock_content += (
            "- **Income Statement:** Reviewed (3-5 years) [Source: SQLite Database]\n"
            "- **Balance Sheet:** Reviewed (3-5 years) [Source: SQLite Database]\n"
            "- **Cash Flow Statement:** Reviewed (3-5 years) [Source: SQLite Database]\n"
            "- **Notes to Financial Statements:** Reviewed [Source: Annual Reports]\n\n"
        )
        mock_content += "## 3. Management & Governance | Status: 🟢 **PASS**\n"
        mock_content += "- **Analysis:** Management is transparent and has good capital allocation.\n\n"
        mock_content += "## Part III: Good Company (Quantitative) | Financial Health Status: 🟢 **PASS**\n"
        mock_content += (
            "- **Profitability (Margins/ROE):** ROE is >15%, which is excellent.\n\n"
        )

        if self.state.director_feedback_path:
            mock_content += "## Part IV: Addressed Feedback\n"
            mock_content += f"> **Notice:** I have explicitly reviewed the previous Director feedback located at `{self.state.director_feedback_path}` and adjusted my analysis accordingly.\n\n"

        mock_content += "## Part V: Final Synthesis Summary & Actionable Advice\n"
        mock_content += "**Overall BLUF:** Company meets GCCP criteria.\n"
        mock_content += "- **Target/Suggested Entry Price:** 100,000 VND\n"
        mock_content += "> **BUY NOW**\n"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(mock_content)

        self.state.synthesized_insights = mock_content
        self.state.history += (
            f"Synthesizer v{version} executed (MOCK) and wrote to {report_path}.\n"
        )
        print(
            f"[ReportLoop Flow - MOCK] 📝 Wrote mock synthesis report to {report_path}"
        )

        financial_summary_path = self.state.shared_data.get(
            "financial_summary_path",
            str(Path(output_dir) / f"{ticker}_financial_summary.md"),
        )
        if not os.path.exists(financial_summary_path):
            mock_fs = f"# MOCK Financial Summary for {ticker}\n\n"
            mock_fs += "This file serves as the ground truth for financial data.\n"
            mock_fs += "- Revenue: 1000\n"
            mock_fs += "- Net Income: 200\n"
            mock_fs += "- Total Equity: 500\n"
            with open(financial_summary_path, "w", encoding="utf-8") as f:
                f.write(mock_fs)
            print(
                f"[ReportLoop Flow - MOCK] 📝 Wrote mock financial summary to {financial_summary_path}"
            )

    def _run_synthesizer_full_kickoff(self):
        """Run full Synthesizer crew kickoff (first pass — 3-task pipeline)."""
        ticker = self.state.target_ticker
        version = self.state.report_version
        print(
            f"\n[ReportLoop Flow] 🚀 Launching Synthesizer Crew (FIRST PASS) for {ticker} "
            f"(Version: v{version}, Loop: {self.state.loop_count + 1}/{self.state.max_loops})..."
        )

        try:
            os.environ["CREWAI_STORAGE_DIR"] = f"stock-agent-synthesizer-{ticker}"

            synthesizer_crew = SynthesizerCrew()
            inputs = self._build_synthesizer_inputs()
            result = synthesizer_crew.run(
                inputs=SynthesizerCrewInputs(**inputs), revision=False
            )

            if hasattr(result, "pydantic") and result.pydantic:
                md_content = result.pydantic.to_markdown()
                output_dir = self.state.shared_data.get(
                    "synthesizer_output_dir", str(PROCESSED_SYNTHESIZER_DIR / ticker)
                )
                report_path = str(
                    Path(output_dir) / f"{ticker}_GCCP_report_v{version}.md"
                )
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                self.state.synthesized_insights = md_content
            else:
                self.state.synthesized_insights = str(result)

            self.state.history += f"Synthesizer v{version} full kickoff executed.\n"

        except Exception as e:
            self.state.history += f"Synthesizer v{version} Failed: {str(e)}\n"
            raise

    def _run_synthesizer_revision(self):
        """Run Synthesizer revision crew — evaluate_feedback task only.

        Manager reads Director feedback + previous report himself, then
        delegates data/forensic queries as needed.
        """
        ticker = self.state.target_ticker
        version = self.state.report_version
        print(
            f"\n[ReportLoop Flow] 🔄 Launching Synthesizer Crew (REVISION) for {ticker} "
            f"(Version: v{version}, Loop: {self.state.loop_count + 1}/{self.state.max_loops})..."
        )

        try:
            os.environ["CREWAI_STORAGE_DIR"] = f"stock-agent-synthesizer-{ticker}"

            synthesizer_crew = SynthesizerCrew()
            inputs = self._build_synthesizer_inputs()
            result = synthesizer_crew.run(
                inputs=SynthesizerCrewInputs(**inputs), revision=True
            )

            if hasattr(result, "pydantic") and result.pydantic:
                md_content = result.pydantic.to_markdown()
                output_dir = self.state.shared_data.get(
                    "synthesizer_output_dir", str(PROCESSED_SYNTHESIZER_DIR / ticker)
                )
                report_path = str(
                    Path(output_dir) / f"{ticker}_GCCP_report_v{version}.md"
                )
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                self.state.synthesized_insights = md_content
            else:
                self.state.synthesized_insights = str(result)

            self.state.history += (
                f"Synthesizer v{version} revision executed (evaluate_feedback only).\n"
            )

        except Exception as e:
            self.state.history += f"Synthesizer v{version} revision failed: {str(e)}\n"
            raise

    # ────────────────────────────────────────────────────────────
    # Director helper (called from both first_pass and revision)
    # ────────────────────────────────────────────────────────────

    def _run_director(self):
        """Run Director Crew to validate the current Synthesizer output.

        Reads the synthesis report from disk, runs Director review, and
        writes structured review via DirectorDecision.to_markdown().
        Updates state: director_approval, director_feedback_path, loop_count.
        """
        ticker = self.state.target_ticker
        version = self.state.report_version
        output_dir = self.state.shared_data.get(
            "synthesizer_output_dir", str(PROCESSED_SYNTHESIZER_DIR / ticker)
        )

        synthesis_report_path = str(
            Path(output_dir) / f"{ticker}_GCCP_report_v{version}.md"
        )
        review_output_path = str(
            Path(output_dir) / f"{ticker}_director_review_v{version}.md"
        )

        print(
            f"\n[ReportLoop Flow] 🕵️‍♂️ Launching Director Crew for v{version} review..."
        )
        print(f"  Reading: {synthesis_report_path}")
        print(f"  Writing: {review_output_path}")

        if self._is_mocking("director"):
            # Alternate mock logic to test loops
            if self.state.loop_count < 2:
                self.state.director_approval = "REJECTED"
                self.state.director_feedback_path = review_output_path
                os.makedirs(output_dir, exist_ok=True)
                mock_review = (
                    f"# [REJECTED]\n\n"
                    f"**Ticker:** {ticker}\n"
                    f"**Style:** Graham\n\n"
                    f"## ❌ Methodology Failures:\n"
                    f"- Missing margin of safety calculation\n"
                    f"- Debt-to-equity ratio not verified against balance sheet\n\n"
                    f"## Summary\n"
                    f"MOCK REJECTION v{version} — Needs more quantitative detail on margins.\n\n"
                    f"## Next Steps\n"
                    f"- Recalculate margin of safety with current market price\n"
                    f"- Verify debt ratios against latest balance sheet\n"
                )
                with open(review_output_path, "w", encoding="utf-8") as f:
                    f.write(mock_review)
            else:
                self.state.director_approval = "APPROVED"
                self.state.director_feedback_path = ""
                os.makedirs(output_dir, exist_ok=True)
                mock_review = (
                    f"# [APPROVED]\n\n"
                    f"**Ticker:** {ticker}\n"
                    f"**Style:** Graham\n\n"
                    f"## Summary\n"
                    f"MOCK APPROVAL v{version} — All criteria met.\n\n"
                    "---\n**Analysis withstands scrutiny. Ready for publication.**\n"
                )
                with open(review_output_path, "w", encoding="utf-8") as f:
                    f.write(mock_review)
            self.state.loop_count += 1
            print(
                f"[ReportLoop Flow - MOCK] Director returned: {self.state.director_approval}"
            )
            return

        try:
            # Pre-read the synthesis report so it's injected into the task prompt
            # (Qwen models skip tool calls with output_pydantic, so we provide content directly)
            report_content = ""
            if os.path.exists(synthesis_report_path):
                with open(synthesis_report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                print(f"  ✅ Pre-read report: {len(report_content)} chars")
            else:
                report_content = f"ERROR: File not found at {synthesis_report_path}"
                print(f"  ❌ Report file not found: {synthesis_report_path}")

            director_crew = DirectorCrew()

            # Pre-read financial summary as ground truth for Director
            financial_summary_content = ""
            financial_summary_path = self.state.shared_data.get(
                "financial_summary_path", ""
            )
            if financial_summary_path and os.path.exists(financial_summary_path):
                with open(financial_summary_path, "r", encoding="utf-8") as f:
                    financial_summary_content = f.read()
                print(
                    f"  ✅ Pre-read financial summary: {len(financial_summary_content)} chars"
                )
            else:
                financial_summary_content = "No financial summary available."
                print(f"  ⚠️ Financial summary not found at: {financial_summary_path}")

            inputs_obj = DirectorCrewInputs(
                stock_symbols=ticker,
                synthesis_report_path=synthesis_report_path,
                review_output_path=review_output_path,
                report_content=report_content,
                financial_summary_content=financial_summary_content,
            )
            result = director_crew.run(inputs=inputs_obj)

            # Extract DirectorDecision from result
            decision_obj = result.pydantic
            if not decision_obj:
                print(
                    "[ReportLoop Flow] ⚠️ Director returned non-Pydantic result. Treating as REJECTED."
                )
                self.state.director_feedback_path = review_output_path
                self.state.loop_count += 1
                self.state.director_approval = "REJECTED"
                return

            # Log structured decision info
            if isinstance(decision_obj, DirectorDecision):
                print(
                    f"[ReportLoop Flow] Director Decision: {decision_obj.decision}\n"
                    f"  Summary: {decision_obj.feedback_summary}"
                )
                if decision_obj.next_steps:
                    print(f"  Next Steps: {', '.join(decision_obj.next_steps)}")
            else:
                print(
                    f"[ReportLoop Flow] Director Decision: {decision_obj.decision}\n"
                    f"  (Unexpected pydantic type: {type(decision_obj).__name__})"
                )

            self.state.director_feedback_path = review_output_path
            self.state.loop_count += 1
            self.state.director_approval = decision_obj.decision

        except Exception as e:
            self.state.history += f"Director v{version} Failed: {str(e)}\n"
            self.state.loop_count += 1
            self.state.director_approval = "ERROR"
            raise

    # ────────────────────────────────────────────────────────────
    # Flow steps
    #
    # CrewAI insight: @listen(or_()) fires only ONCE for non-routers.
    # Routers are exempt. So the director can't be a separate or_() listener.
    # Instead, each branch runs synthesizer + director in one step.
    # ────────────────────────────────────────────────────────────

    @listen(initialize_setup)
    def execute_first_pass(self):
        """First pass: run Synthesizer (full kickoff) + Director review."""
        if self._is_mocking("synthesizer"):
            self._run_synthesizer_mock()
        else:
            self._run_synthesizer_full_kickoff()
        self._run_director()

    @listen("loop_back")
    def handle_revision(self):
        """Loop-back: re-run Synthesizer (revision crew) + Director review."""
        self.state.report_version += 1
        print(
            f"\n[ReportLoop Flow] 🔄 Director rejected v{self.state.report_version - 1}. "
            f"Re-running Synthesizer (revision) for v{self.state.report_version}..."
        )
        if self._is_mocking("synthesizer"):
            self._run_synthesizer_mock()
        else:
            self._run_synthesizer_revision()
        self._run_director()

    @router(or_(execute_first_pass, handle_revision))
    def evaluate_director_decision(self):
        """Route based on Director's decision and loop limit.

        Uses @router(or_()) because routers are exempt from CrewAI's
        or_() deduplication guard — this is the only way to re-trigger
        on each loop iteration.
        """
        if self.state.director_approval == "APPROVED":
            return "route_to_reporter"

        if self.state.director_approval == "ERROR":
            return "route_to_failure"

        if self.state.loop_count >= self.state.max_loops:
            print(
                f"\n[ReportLoop Flow] 🛑 Reached Max Loop Limit ({self.state.max_loops}). Failing out."
            )
            return "route_to_human_in_loop"

        return "loop_back"

    @listen("route_to_human_in_loop")
    def await_human_decision(self):
        """
        Pause logic simulating Human In the Loop over N8N or CLI.
        Since CrewAI 'Flows' don't natively PAUSE execution visually on CLI well,
        we ask via python built-in input() as a stop-gap.
        """
        print("\n\n" + "=" * 50)
        print("🚨 HUMAN IN THE LOOP REQUIRED 🚨")
        print("=" * 50)
        print(
            f"Director Crew has failed to approve the report after {self.state.max_loops} versions."
        )
        print(f"Latest review file: {self.state.director_feedback_path}")
        print("\nWhat would you like to do?")
        print("[1] Override and Approve (Proceed to Reporter)")
        print("[2] Abort Workflow")

        if self._is_mocking("human"):
            print("[MOCK MODE] Automatically choosing [2] Abort to prevent hanging.")
            return "route_to_failure"

        try:
            choice = input("Enter choice (1/2): ")
            if choice.strip() == "1":
                print("Human overriding Director. Proceeding...")
                return "route_to_reporter"
            else:
                return "route_to_failure"
        except EOFError:
            # Handle non-interactive terminal (like CI/tests)
            print("No interactive terminal available. Defaulting to ABORT.")
            return "route_to_failure"

    @listen("route_to_reporter")
    def execute_reporter(self):
        """
        Mock Reporter step handling approval.
        """
        print("\n[ReportLoop Flow] ✨ Analysis APPROVED! Generating final report...")

        # We simulate the reporter actually writing it since Reporter Crew lacks full task setup.
        symbol = self.state.target_ticker or "TICKER"
        output_dir = f"data/processed/reports/{symbol}"
        os.makedirs(output_dir, exist_ok=True)

        file_path = f"{output_dir}/Final_{symbol}_Report.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Final Synthesized Report for {symbol}\n\n")
            f.write("## Status: APPROVED BY DIRECTOR\n\n")
            f.write(self.state.synthesized_insights)

        print(f"✅ Success! Report saved to {file_path}")
        return "SUCCESS"

    @listen("route_to_failure")
    def handle_failure(self):
        print("\n[ReportLoop Flow] ❌ Flow completely failed/aborted.")
        return "FAILURE"


if __name__ == "__main__":
    flow = SynthesizerReporterFlow()
    # path = flow.plot("report_loop_flow.html")
    # print(f"✅ Plot saved to absolute path: {path}")
