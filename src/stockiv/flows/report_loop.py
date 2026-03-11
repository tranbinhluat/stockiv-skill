"""
Report Loop Flow - Versioned file-based feedback loop between Synthesizer and Director.

Each loop iteration produces versioned files on disk:
  - {ticker}_GCCP_report_v{N}.md   (Synthesizer output)
  - {ticker}_director_review_v{N}.md (Director review)
"""

from crewai.flow.flow import Flow, listen, start, router, or_
import os

from stockiv.config.paths import (
    PROCESSED_ANNUAL_REPORTS_DIR,
    PROCESSED_SENTIMENT_MARKET_DIR,
    PROCESSED_SENTIMENT_TICKER_DIR,
    PROCESSED_SYNTHESIZER_DIR,
)
from stockiv.flows.state import PipelineState
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew, SynthesizerCrewInputs
from stockiv.crews.director.director import DirectorCrew, DirectorCrewInputs


class ReportLoopState(PipelineState):
    """State for the Report Loop — extends PipelineState.

    Loop mechanism fields live here as direct attributes.
    Data paths are stored in shared_data (populated by parent flow or initialize_setup).
    """

    # Loop mechanism
    director_feedback_path: str = ""  # Path to Director's review file
    director_approval: str = "REJECTED"
    loop_count: int = 0
    max_loops: int = 5
    report_version: int = 1

    # Legacy
    synthesized_insights: str = ""


class SynthesizerReporterFlow(Flow[ReportLoopState]):
    """
    Mini flow that orchestrates the Synthesizer Crew and Director Crew in a
    versioned file-based feedback loop. Every iteration writes to disk for
    human review. Upon Director rejection, it feeds back the review file path.
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
        self.state.shared_data.setdefault(
            "ticker_sentiment_path",
            str(ticker_sentiment_dir / f"{ticker}_sentiment.md"),
        )

        self.state.history += f"ReportLoop setup complete for {ticker}.\n"
        return self.state.target_ticker

    @listen(initialize_setup)
    def execute_synthesizer(self):
        """
        Run the Synthesizer Crew. Pass file paths from shared_data,
        and the Director's review file path as feedback on re-runs.
        """
        ticker = self.state.target_ticker
        version = self.state.report_version
        print(
            f"\n[ReportLoop Flow] 🚀 Launching Synthesizer Crew for {ticker} "
            f"(Version: v{version}, Loop: {self.state.loop_count + 1}/{self.state.max_loops})..."
        )

        if self._is_mocking("synthesizer"):
            output_dir = self.state.shared_data.get(
                "synthesizer_output_dir", f"data/processed/synthesizer/{ticker}"
            )
            os.makedirs(output_dir, exist_ok=True)
            report_path = f"{output_dir}/{ticker}_GCCP_report_v{version}.md"
            
            mock_content = f"# MOCK GCCP Synthesis Report: {ticker} (v{version})\n\n"
            mock_content += "This is a simulated report to test the Director feedback loop.\n\n"
            mock_content += "## 1. Business Model & Moat | Status: 🟢 **PASS**\n"
            mock_content += "- **Analysis:** The company shows strong recurring revenue.\n\n"
            mock_content += "## 2. Management & Governance | Status: 🟢 **PASS**\n"
            mock_content += "- **Analysis:** Management is transparent and has good capital allocation.\n\n"
            mock_content += "## Part III: Good Company (Quantitative) | Financial Health Status: 🟢 **PASS**\n"
            mock_content += "- **Profitability (Margins/ROE):** ROE is >15%, which is excellent.\n\n"
            
            if self.state.director_feedback_path:
                mock_content += f"## Part IV: Addressed Feedback\n"
                mock_content += f"> **Notice:** I have explicitly reviewed the previous Director feedback located at `{self.state.director_feedback_path}` and adjusted my analysis accordingly.\n\n"
                
            mock_content += "## Part V: Final Synthesis Summary & Actionable Advice\n"
            mock_content += "**Overall BLUF:** Company meets GCCP criteria.\n"
            mock_content += "- **Target/Suggested Entry Price:** 100,000 VND\n"
            mock_content += "> **BUY NOW**\n"
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(mock_content)

            self.state.synthesized_insights = mock_content
            self.state.history += f"Synthesizer v{version} executed (MOCK) and wrote to {report_path}.\n"
            print(f"[ReportLoop Flow - MOCK] 📝 Wrote mock synthesis report to {report_path}")
            return
        try:
            synthesizer_crew = SynthesizerCrew()

            inputs_obj = SynthesizerCrewInputs(
                stock_symbols=ticker,
                date=self.state.shared_data.get("current_date", "2026-03-11"),
                financial_summary_path=self.state.shared_data.get(
                    "financial_summary_path"
                )
                or None,
                annual_reports_dir=self.state.shared_data.get("annual_reports_dir")
                or None,
                synthesizer_output_dir=self.state.shared_data.get(
                    "synthesizer_output_dir"
                )
                or None,
                sentiment_dir=self.state.shared_data.get("sentiment_dir") or None,
                ticker_sentiment_path=self.state.shared_data.get(
                    "ticker_sentiment_path"
                )
                or None,
                report_version=version,
            )

            # Inject Director's review file path as feedback on re-runs
            if self.state.director_feedback_path:
                print(
                    f"[ReportLoop Flow] 📝 Injecting Director review path: {self.state.director_feedback_path}"
                )
                inputs_obj.feedback = self.state.director_feedback_path

            result = synthesizer_crew.run(inputs=inputs_obj)
            self.state.synthesized_insights = str(result)
            self.state.history += f"Synthesizer v{version} executed.\n"

        except Exception as e:
            self.state.history += f"Synthesizer v{version} Failed: {str(e)}\n"
            raise

        return
    

    @listen(execute_synthesizer)
    def execute_director(self):
        """
        Run the Director Crew to validate the Synthesizer output.
        Director reads report from disk and writes review to disk.
        """
        ticker = self.state.target_ticker
        version = self.state.report_version
        output_dir = self.state.shared_data.get(
            "synthesizer_output_dir", f"data/processed/synthesizer/{ticker}"
        )

        synthesis_report_path = f"{output_dir}/{ticker}_GCCP_report_v{version}.md"
        review_output_path = f"{output_dir}/{ticker}_director_review_v{version}.md"

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
                # Write mock review file
                os.makedirs(output_dir, exist_ok=True)
                with open(review_output_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"# Director Review v{version}\n\n**Decision:** REJECTED\n\n## Reasoning\nMOCK REJECTION - Needs more detail on Margins\n"
                    )
            else:
                self.state.director_approval = "APPROVED"
                self.state.director_feedback_path = ""
                os.makedirs(output_dir, exist_ok=True)
                with open(review_output_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"# Director Review v{version}\n\n**Decision:** APPROVED\n\n## Reasoning\nMOCK APPROVAL - All looks good.\n"
                    )
            self.state.loop_count += 1
            print(
                f"[ReportLoop Flow - MOCK] Director returned: {self.state.director_approval}"
            )
            return
        try:
            director_crew = DirectorCrew()
            inputs_obj = DirectorCrewInputs(
                stock_symbols=ticker,
                synthesis_report_path=synthesis_report_path,
                review_output_path=review_output_path,
            )
            result = director_crew.run(inputs=inputs_obj)

            # Extract Pydantic ValidationDecision
            decision_obj = result.pydantic
            if not decision_obj:
                print(
                    "[ReportLoop Flow] ⚠️ Director returned non-Pydantic result. Treating as REJECTED."
                )
                self.state.director_feedback_path = review_output_path
                self.state.loop_count += 1
                self.direct_approval = "REJECTED"
                return

            print(
                f"[ReportLoop Flow] Director Decision: {decision_obj.decision}\nReasoning: {decision_obj.reasoning}"
            )

            self.state.director_feedback_path = review_output_path
            self.state.loop_count += 1
            self.state.director_approval = decision_obj.decision


        except Exception as e:
            self.state.history += f"Director v{version} Failed: {str(e)}\n"
            self.state.loop_count += 1
            self.state.director_approval = "ERROR"
            raise
        return


    @router(execute_director)
    def evaluate_director_decision(self, decision):
        """Route based on Director's decision and loop limit."""
        if self.state.director_approval == "APPROVED":
            return "route_to_reporter"

        if self.state.director_approval == "ERROR":
            return "route_to_failure"

        if self.state.loop_count >= self.state.max_loops:
            print(
                f"\n[ReportLoop Flow] 🛑 Reached Max Loop Limit ({self.state.max_loops}). Failing out."
            )
            return "route_to_human_in_loop"

        # Increment version for next iteration
        self.state.report_version += 1
        print(
            f"\n[ReportLoop Flow] 🔄 Director rejected v{self.state.report_version - 1}. "
            f"Routing back to Synthesizer for v{self.state.report_version}..."
        )
        return "evaluate_director_feedback"

    

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
            return "ABORT"

        try:
            choice = input("Enter choice (1/2): ")
            if choice.strip() == "1":
                print("Human overriding Director. Proceeding...")
                return "route_to_reporter"
            else:
                return "ABORT"
        except EOFError:
            # Handle non-interactive terminal (like CI/tests)
            print("No interactive terminal available. Defaulting to ABORT.")
            return "ABORT"

    @router(await_human_decision)
    def evaluate_human_decision(self, decision):
        if decision == "route_to_reporter":
            return "route_to_reporter"
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
