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


from stockiv.agents.base import primary_llm
import json


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
        Dynamically routes the request to the appropriate Crew using an LLM.
        Falls back to regex if the LLM fails.
        """
        request = self.state.get("request", "").lower()

        print("[Orchestrator] 🤔 Asking LLM to route the request...")
        prompt = f"""
        Analyze the following user request and determine the best route and the target stock ticker (if any).
        Request: "{request}"

        If the user is asking to collect or gather data for a stock, set 'route' to "route_to_collector" and extract the uppercase stock ticker (e.g. "FPT").
        If the request is unclear or not related to collecting stock data, set 'route' to "unrecognized_route" and 'target_ticker' to "".

        Output EXACTLY one valid JSON object with keys 'route' and 'target_ticker', nothing else. Do not wrap in markdown tags.
        """

        try:
            response = primary_llm.call(messages=[{"role": "user", "content": prompt}])

            # Clean up response to find JSON if markdown used
            json_str = response
            matches = re.findall(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL)
            if matches:
                json_str = matches[0]

            data = json.loads(json_str.strip())
            route = data.get("route", "unrecognized_route")
            ticker = data.get("target_ticker", "")

            if route == "route_to_collector" and ticker:
                self.state["target_ticker"] = ticker.upper()
                print(
                    f"[Orchestrator] ➡️  LLM routed to Collector Crew for: {ticker.upper()}"
                )
                return "route_to_collector"

            print(f"[Orchestrator] ➡️  LLM routed to: {route}")
            return route

        except Exception as e:
            print(f"[Orchestrator] ⚠️ LLM routing failed ({e}). Falling back to regex.")

        # Fallback regex to check if they want to collect data for a ticker
        if "collect" in request or "gather" in request:
            # Try to extract a 3-letter ticker (e.g. FPT) ignoring common words
            match = re.search(r"\b(?!(?:for|the|and|all|any)\b)([a-z]{3})\b", request)
            if match:
                ticker = match.group(1).upper()
                self.state["target_ticker"] = ticker
                print(
                    f"[Orchestrator] ➡️  Regex Fallback Routing to Collector Crew for: {ticker}"
                )
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
