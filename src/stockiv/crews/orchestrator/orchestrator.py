"""
Orchestrator Crew - Coordinates all crews in the workflow.
"""

from crewai.flow.flow import Flow, listen, start, router
import sys
import os

# Ensure we can import the CollectorCrew
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from stockiv.crews.collector.collector import CollectorCrew
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from stockiv.agents.base import primary_llm


class OrchestratorState(BaseModel):
    request: str = ""
    target_ticker: str = ""
    collector_result: str = ""


class RouteDecision(BaseModel):
    route: str = Field(
        description="The route to take. 'route_to_collector' if data gathering is requested."
    )
    target_ticker: str = Field(
        description="The target stock ticker (e.g. 'FPT'). Empty if unrecognized."
    )


@CrewBase
class RouterCrew:
    """Router Crew - Orchestrates the routing of user requests"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def router(self) -> Agent:
        return Agent(
            config=self.agents_config["router"],
            llm=primary_llm,
        )

    @task
    def routing_task(self) -> Task:
        return Task(
            config=self.tasks_config["routing_task"],
            output_pydantic=RouteDecision,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )


class StockOrchestratorFlow(Flow[OrchestratorState]):
    """
    Main Orchestrator Flow that coordinates the execution of various Crews
    (Collector, QuantAnalyst, SentimentAnalyst, etc) based on user requests.
    """

    @start()
    def receive_request(self):
        # The user input should be passed into the flow via kickoff(inputs={"request": "..."})
        request = self.state.request.lower()
        print(f"\n[Orchestrator] Received request: '{request}'")
        return request

    @router(receive_request)
    def route_request(self):
        """
        Dynamically routes the request to the appropriate Crew using an LLM.
        """
        request = self.state.request.lower()

        print("[Orchestrator] 🤔 Asking RouterCrew to route the request...")

        try:
            router = RouterCrew()
            result = router.crew().kickoff(inputs={"request": request})

            # The result output is a Pydantic object
            decision = result.pydantic

            if decision.route == "route_to_collector" and decision.target_ticker:
                self.state.target_ticker = decision.target_ticker.upper()
                print(
                    f"[Orchestrator] ➡️  LLM routed to Collector Crew for: {decision.target_ticker.upper()}"
                )
                return "route_to_collector"

            print(f"[Orchestrator] ➡️  LLM routed to: {decision.route}")
            return decision.route

        except Exception as e:
            print(f"[Orchestrator] ⚠️ LLM routing failed ({e}).")
            return "unrecognized_route"

        print(
            "[Orchestrator] ⚠️ Could not determine routing or missing ticker. Terminating flow."
        )
        return "unrecognized_route"

    @listen("route_to_collector")
    def execute_collector(self):
        """
        Executes the Collector Crew for the target ticker.
        """
        ticker = self.state.target_ticker
        print(f"\n[Orchestrator] 🚀 Launching Collector Crew for {ticker}...")

        collector = CollectorCrew()
        # Initialize the crew and kickoff with the ticker input
        result = collector.crew().kickoff(inputs={"stock_symbols": ticker})

        print(f"\n[Orchestrator] ✅ Collector Crew completed for {ticker}.")
        self.state.collector_result = str(result)
        return result

    @listen("unrecognized_route")
    def handle_error(self):
        print("\n[Orchestrator] ❌ Workflow stopped: Did not understand request.")
        return "Error: Could not route request."
