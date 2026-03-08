"""
DeepDiveFlow - Main Entry Flow for full comprehensive stock analysis.
"""

from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router
import sys
import os

# Ensure the root package is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from stockiv.flows.state import PipelineState
from stockiv.crews.orchestrator.orchestrator import OrchestratorCrew
from stockiv.crews.collector.collector import CollectorCrew
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew
from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew


class TickerExtraction(BaseModel):
    """LLM decision output dictating if a ticker was found."""

    is_valid: bool = Field(
        description="True if the request is asking to analyze a specific stock/company, False otherwise."
    )
    target_ticker: str = Field(
        description="The target stock ticker (e.g. 'FPT', 'AAPL'). Empty if not found."
    )


class DeepDiveFlow(Flow[PipelineState]):
    """
    Main Entry Flow that coordinates the execution of various Crews
    (Collector, QuantAnalyst, SentimentAnalyst, etc) based on user requests.
    Uses an explicit Master Router Loop with fallback guarantees.
    """

    @start()
    def analyze_request(self):
        """
        Use Orchestrator LLM call to extract the ticker and validate the request.
        """
        self.state.request = self.state.request.lower()
        print(f"\n[DeepDive Flow] Received request: '{self.state.request}'")
        self.state.history += f"Initial Request: {self.state.request}\n"

        if self.state.is_mock:
            print("[DeepDive Flow - MOCK] Bypassing Orchestrator LLM...")
            self.state.target_ticker = "FPT"
            return "FPT"

        # Use OrchestratorCrew with qwen2.5-vl-72b-instruct for ticker extraction
        try:
            orchestrator = OrchestratorCrew()
            result = orchestrator.crew().kickoff(inputs={"request": self.state.request})

            # The result is automatically parsed into TickerExtraction thanks to output_pydantic
            extraction = result.pydantic

            if (
                not extraction
                or not extraction.is_valid
                or not extraction.target_ticker
            ):
                print("[DeepDive Flow] ❌ Invalid request or no ticker found.")
                return None

            self.state.target_ticker = extraction.target_ticker.upper()
            print(f"[DeepDive Flow] ✅ Valid Ticker Found: {self.state.target_ticker}")
            return self.state.target_ticker

        except Exception as e:
            print(
                f"[DeepDive Flow] ⚠️ Orchestrator execution failed ({e}). Forcing error route."
            )
            return None

    @router(analyze_request)
    def handle_routing(self, ticker):
        """Routes execution after `analyze_request` based on state."""
        print(f"[DeepDive Flow] Debug: Ticker is '{ticker}'")
        if ticker:
            return "route_to_collector"
        return "unrecognized_route"

    @listen("route_to_collector")
    def execute_collector(self):
        ticker = self.state.target_ticker
        print(f"\n[DeepDive Flow] 🚀 Launching Collector Crew for {ticker}...")

        context_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../data/raw/context",
            )
        )
        os.makedirs(context_dir, exist_ok=True)
        self.state.market_context_path = os.path.join(context_dir, "market_context.md")
        self.state.ticker_context_path = os.path.join(
            context_dir, f"{ticker}_ticker_context.md"
        )

        if self.state.is_mock:
            print("[DeepDive Flow - MOCK] Bypassing Collector Crew...")
            self.state.history += "Collector executed (MOCK). Result: Mocked Dataset\n"
            return "route_to_sentiment"

        try:
            collector = CollectorCrew()
            result = collector.crew().kickoff(
                inputs={
                    "stock_symbols": ticker,
                    "market_context_path": self.state.market_context_path,
                    "ticker_context_path": self.state.ticker_context_path,
                }
            )
            self.state.history += f"Collector executed. Result: {str(result)}\n"
        except Exception as e:
            self.state.history += f"Collector Failed: {str(e)}\n"

    @listen(execute_collector)
    def execute_sentiment(self):
        ticker = self.state.target_ticker
        from datetime import datetime

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        year, week, _ = now.isocalendar()

        print(
            f"\n[DeepDive Flow] 🚀 Launching Sentiment Analyst Crew for {ticker} (Year: {year}, Week: {week})..."
        )

        # if self.state.is_mock:
        #     print(f"[DeepDive Flow - MOCK] Bypassing Sentiment Analyst Crew...")
        #     self.state.news_sentiment_analysis = "MOCK Sentiment Data"
        #     self.state.history += f"Sentiment Analyst executed (MOCK). Result recorded in State.\n"
        #     self.state.sentiment_finished = True
        #     return

        # Provide requisite paths for sentiment analyst
        output_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../data/processed/sentiment/market",
            )
        )
        os.makedirs(output_dir, exist_ok=True)
        report_title = f"{year}_W{week:02d}_market_report"
        report_md_path = os.path.join(output_dir, f"{report_title}.md")
        overall_report_md_path = os.path.join(
            output_dir, f"{year}_overall_market_sentiment.md"
        )

        try:
            sentiment_crew = SentimentAnalystCrew()
            result = sentiment_crew.crew().kickoff(
                inputs={
                    "stock_symbols": ticker,
                    "date": current_date,
                    "year": str(year),
                    "week": str(week),
                    "report_title": report_title,
                    "report_md_path": report_md_path,
                    "overall_report_md_path": overall_report_md_path,
                    "market_context_path": self.state.market_context_path,
                    "ticker_context_path": self.state.ticker_context_path,
                }
            )
            self.state.shared_data["news_sentiment_analysis"] = str(result)
            self.state.history += (
                "Sentiment Analyst executed. Result recorded in State.\n"
            )
        except Exception as e:
            self.state.history += f"Sentiment Analyst Failed: {str(e)}\n"

    @listen(execute_sentiment)
    def execute_synthesizer(self):
        ticker = self.state.target_ticker
        from datetime import datetime

        current_date = datetime.now().strftime("%Y-%m-%d")

        print(f"\n[DeepDive Flow] 🚀 Launching Synthesizer Crew for {ticker}...")

        if self.state.is_mock:
            print("[DeepDive Flow - MOCK] Bypassing Synthesizer Crew...")
            self.state.history += "Synthesizer executed (MOCK). Result: Mocked Report\n"
            return

        try:
            synthesizer = SynthesizerCrew()
            result = synthesizer.crew().kickoff(
                inputs={
                    "stock_symbols": ticker,
                    "date": current_date,
                    "financial_summary_path": f"data/processed/synthesizer/{ticker}/{ticker}_financial_summary.md",
                    "annual_reports_dir": "data/processed/annual_reports/",
                    "synthesizer_output_dir": f"data/processed/synthesizer/{ticker}/",
                    "sentiment_dir": "data/processed/sentiment",
                }
            )
            self.state.history += f"Synthesizer executed. Result: {str(result)}\n"
        except Exception as e:
            self.state.history += f"Synthesizer Failed/Complained: {str(e)}\n"

    @listen("unrecognized_route")
    def handle_error(self):
        print(
            "\n[DeepDive Flow] ❌ Workflow stopped: Did not understand request or hit a routing error."
        )
        return "Error: Could not route request."

    @listen(execute_synthesizer)
    def finish_flow(self):
        print(
            f"\n[DeepDive Flow] 🏁 Flow successfully completed for target: {self.state.target_ticker}."
        )
        print("Final Execution History Logged. Terminating.")
        return self.state.history
