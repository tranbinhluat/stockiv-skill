"""
Orchestrator Crew - Coordinates all crews in the workflow.
"""

from crewai.flow.flow import Flow, listen, start, router
import re
import sys
import os

# Ensure we can import the CollectorCrew
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from stockiv.crews.collector.collector import CollectorCrew


class StockOrchestratorFlow(Flow):
    """
    Main Orchestrator Flow that coordinates the execution of various Crews
    (Collector, QuantAnalyst, SentimentAnalyst, etc) based on user requests.
    """

    @start()
    def receive_request(self):
        # The user input should be passed into the flow via kickoff(inputs={"request": "..."})
        request = self.state.get("request", "").lower()
        print(f"\n[Orchestrator] Received request: '{request}'")
        return request

    @router(receive_request)
    def route_request(self):
        """
        Dynamically routes the request to the appropriate Crew.
        (This will later be expanded into an LLM router, but for now uses regex)
        """
        request = self.state.get("request", "").lower()

        # Simple regex to check if they want to collect data for a ticker
        if "collect" in request or "gather" in request:
            # Try to extract a 3-letter ticker (e.g. FPT) ignoring common words
            match = re.search(r"\b(?!(?:for|the|and|all|any)\b)([a-z]{3})\b", request)
            if match:
                ticker = match.group(1).upper()
                self.state["target_ticker"] = ticker
                print(f"[Orchestrator] ➡️  Routing to Collector Crew for: {ticker}")
                return "route_to_collector"

        print(
            "[Orchestrator] ⚠️ Could not determine routing or missing ticker. Terminating flow."
        )
        return "unrecognized_route"

    @listen("route_to_collector")
    def execute_collector(self):
        """
        Executes the Collector Crew for the target ticker.
        """
        ticker = self.state.get("target_ticker")
        print(f"\n[Orchestrator] 🚀 Launching Collector Crew for {ticker}...")

        collector = CollectorCrew()
        # Initialize the crew and kickoff with the ticker input
        result = collector.crew().kickoff(inputs={"stock_symbols": ticker})

        print(f"\n[Orchestrator] ✅ Collector Crew completed for {ticker}.")
        self.state["collector_result"] = str(result)
        return result

    @listen("unrecognized_route")
    def handle_error(self):
        print("\n[Orchestrator] ❌ Workflow stopped: Did not understand request.")
        return "Error: Could not route request."
