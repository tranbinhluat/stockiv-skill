"""
Report Loop Flow - Evaluates synthesis, loops with Director, and outputs.
"""

from crewai.flow.flow import Flow, listen, start, router, or_
from pydantic import BaseModel
import sys
import os

# Ensure the root package is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew, SynthesizerCrewInputs
from stockiv.crews.director.director import DirectorCrew, DirectorCrewInputs


class ReportLoopState(BaseModel):
    """Specific state for the Report Loop."""

    request: str = ""
    target_ticker: str = ""
    history: str = ""
    is_mock: bool = False

    # Loop specific mechanism
    director_feedback: str = ""
    director_approval: str = "REJECTED"
    loop_count: int = 0
    max_loops: int = 5

    # Data pass-through
    financial_summary: str = ""
    synthesized_insights: str = ""


class SynthesizerReporterFlow(Flow[ReportLoopState]):
    """
    Mini flow that orchestrates the Synthesizer Crew and Director Crew in a
    feedback loop. Upon Director rejection, it feeds back the response.
    If loop limit is hit, requires human-in-the-loop validation.
    """

    @start()
    def initialize_setup(self):
        """Setup initial limits based on input."""
        # Typically set from CLI overriding the state defaults
        print(
            f"\n[ReportLoop Flow] Initializing. Max Loops allowed: {self.state.max_loops}"
        )
        self.state.loop_count = 0
        return self.state.target_ticker

    @listen(or_(initialize_setup, "route_to_synthesizer"))
    def execute_synthesizer(self):
        """
        Run the Synthesizer Crew. If there is director_feedback, inject it.
        """
        ticker = self.state.target_ticker
        print(
            f"\n[ReportLoop Flow] 🚀 Launching Synthesizer Crew for {ticker} (Loop: {self.state.loop_count + 1}/{self.state.max_loops})..."
        )

        if self.state.is_mock:
            self.state.synthesized_insights = (
                f"MOCK Synthesized Insights (Loop {self.state.loop_count})"
            )
            self.state.history += "Synthesizer executed (MOCK).\n"
            return
        try:
            synthesizer_crew = SynthesizerCrew()

            # Combine inputs, injecting feedback if present
            inputs_obj = SynthesizerCrewInputs(
                stock_symbols=ticker,
                # Assume standard deepdive flow already got this, but simulate if not
                date="2026-03-07",
                financial_summary="Simulated raw DB dump for " + ticker,
            )

            if self.state.director_feedback:
                print(
                    "[ReportLoop Flow] 📝 Injecting previous Director Feedback into Synthesizer context."
                )
                inputs_obj.manager_directives = self.state.director_feedback

            result = synthesizer_crew.run(inputs=inputs_obj)
            self.state.synthesized_insights = str(result)
            self.state.history += (
                f"Synthesizer executed (Loop {self.state.loop_count}).\n"
            )

        except Exception as e:
            self.state.history += f"Synthesizer Failed: {str(e)}\n"

        return

    @listen(execute_synthesizer)
    def execute_director(self):
        """
        Run the Director Crew to validate the Synthesizer output.
        """
        print("\n[ReportLoop Flow] 🕵️‍♂️ Launching Director Crew for Validation...")

        if self.state.is_mock:
            # Alternate mock logic to test loops
            if self.state.loop_count < 2:
                self.state.director_approval = "REJECTED"
                self.state.director_feedback = (
                    "MOCK REJECTION - Needs more detail on Margins"
                )
            else:
                self.state.director_approval = "APPROVED"
                self.state.director_feedback = "MOCK APPROVAL - All looks good."
            self.state.loop_count += 1
            print(
                f"[ReportLoop Flow - MOCK] Director returned: {self.state.director_approval} - {self.state.director_feedback}"
            )
            return
        try:
            director_crew = DirectorCrew()
            inputs_obj = DirectorCrewInputs(analysis=self.state.synthesized_insights)
            result = director_crew.run(inputs=inputs_obj)

            # Extract Pydantic ValidationDecision
            decision_obj = result.pydantic
            if not decision_obj:
                print(
                    "[ReportLoop Flow] ⚠️ Director returned non-Pydantic result. Treating as REJECTED."
                )
                self.state.director_feedback = "Failed to parse structured output."
                self.state.loop_count += 1

            print(
                f"[ReportLoop Flow] Director Decision: {decision_obj.decision}\nReasoning: {decision_obj.reasoning}"
            )

            self.state.director_feedback = decision_obj.reasoning
            self.state.loop_count += 1
            self.state.director_approval = decision_obj.decision

        except Exception as e:
            self.state.history += f"Director Failed: {str(e)}\n"
            self.state.loop_count += 1
            self.state.director_approval = "ERROR"
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

        print(
            "\n[ReportLoop Flow] 🔄 Director rejected analysis. Routing back to Synthesizer..."
        )
        return "route_to_synthesizer"

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
        print("Director Crew has failed to approve the report 5 times.")
        print("Latest Feedback:")
        print(self.state.director_feedback)
        print("\nWhat would you like to do?")
        print("[1] Override and Approve (Proceed to Reporter)")
        print("[2] Abort Workflow")

        if self.state.is_mock:
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
