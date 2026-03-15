"""
DeepDiveFlow - Full comprehensive stock analysis for a specific ticker.

Expects `target_ticker` to be set on state before kickoff.
Chain: setup_flow → collector → sentiment → synthesizer_loop (TODO) → reporter → finish
"""

from datetime import datetime

from crewai.flow.flow import Flow, listen, start

from stockiv.config.paths import (
    PROCESSED_ANNUAL_REPORTS_DIR,
    PROCESSED_SENTIMENT_MARKET_DIR,
    PROCESSED_SENTIMENT_TICKER_DIR,
    PROCESSED_SYNTHESIZER_DIR,
    RAW_ANNUAL_REPORT_DIR,
    RAW_CONTEXT_DIR,
    REPORT_TICKER_DIR,
)
from stockiv.flows.state import PipelineState
from stockiv.crews.collector.collector import CollectorCrew, CollectorCrewInputs
from stockiv.crews.sentiment_analyst.sentiment_analyst import (
    SentimentAnalystCrew,
    SentimentAnalystCrewInputs,
)
from stockiv.utils.freshness import is_file_fresh, get_file_age_days


class DeepDiveFlow(Flow[PipelineState]):
    """
    Full GCCP deep-dive flow for a single ticker.
    Caller must set `flow.state.target_ticker` before kickoff.
    """

    @start()
    def setup_flow(self):
        """
        1. GENERATE PIPELINE STATE AND CENTRALIZED PATHS
        """
        ticker = self.state.target_ticker.upper()
        if not ticker:
            raise ValueError(
                "target_ticker must be set on state before kicking off DeepDiveFlow."
            )
        self.state.target_ticker = ticker

        print(f"\n[DeepDive Flow] ⚙️ Initializing State for {ticker}...")

        now = datetime.now()
        year = now.strftime("%Y")
        _, week_num, _ = now.isocalendar()
        current_date = now.strftime("%Y-%m-%d")

        self.state.shared_data["report_year"] = year
        self.state.shared_data["report_week"] = f"{week_num:02d}"
        self.state.shared_data["current_date"] = current_date

        # --- Report naming ---
        report_title = f"{ticker}_GCCP_report"
        macro_sentiment_title = f"{year}_W{week_num:02d}_macro_sentiment"
        self.state.shared_data["report_title"] = report_title

        # --- Collector paths ---
        self.state.shared_data["market_context_path"] = str(
            RAW_CONTEXT_DIR / "market_context.md"
        )
        self.state.shared_data["ticker_context_path"] = str(
            RAW_CONTEXT_DIR / f"{ticker}_ticker_context.md"
        )

        # --- Sentiment paths ---
        self.state.shared_data["market_sentiment_dir"] = str(
            PROCESSED_SENTIMENT_MARKET_DIR
        )
        self.state.shared_data["macro_sentiment_md_path"] = str(
            PROCESSED_SENTIMENT_MARKET_DIR / f"{macro_sentiment_title}.md"
        )
        self.state.shared_data["overall_macro_sentiment_md_path"] = str(
            PROCESSED_SENTIMENT_MARKET_DIR / f"{year}_overall_macro_sentiment.md"
        )

        ticker_sentiment_dir = PROCESSED_SENTIMENT_TICKER_DIR / ticker
        ticker_sentiment_dir.mkdir(parents=True, exist_ok=True)
        self.state.shared_data["ticker_sentiment_path"] = str(
            ticker_sentiment_dir / f"{year}_W{week_num:02d}_sentiment.md"
        )

        # --- Synthesizer paths ---
        synthesizer_ticker_dir = PROCESSED_SYNTHESIZER_DIR / ticker
        synthesizer_ticker_dir.mkdir(parents=True, exist_ok=True)
        self.state.shared_data["synthesizer_output_dir"] = str(synthesizer_ticker_dir)
        self.state.shared_data["synthesizer_md_path"] = str(
            synthesizer_ticker_dir / f"{ticker}_GCCP_synthesis.md"
        )
        self.state.shared_data["financial_summary_path"] = str(
            synthesizer_ticker_dir / f"{ticker}_financial_summary.md"
        )

        # --- Reporter paths ---
        self.state.shared_data["report_pdf_path"] = str(
            REPORT_TICKER_DIR / f"{report_title}.pdf"
        )

        self.state.history += f"Setup complete for {ticker}.\n"

    @listen(setup_flow)
    def execute_collector(self):
        """
        2. RUN COLLECTOR CREW (full: macro + ticker + annual reports)
           Skips web-search tasks whose output files are still fresh (<7 days).
        """
        ticker = self.state.target_ticker
        print(f"\n[DeepDive Flow] 🚀 Launching Collector Crew for {ticker}...")

        # --- Freshness check: determine which tasks to skip ---
        skip_tasks: list[str] = []
        freshness_checks = {
            "fetch_macro_context_task": self.state.shared_data["market_context_path"],
            "fetch_ticker_context_task": self.state.shared_data["ticker_context_path"],
        }
        for task_name, file_path in freshness_checks.items():
            if is_file_fresh(file_path, max_age_days=7):
                age = get_file_age_days(file_path)
                print(f"  ⏭️  Skipping {task_name} (fresh: {age:.1f} days old)")
                skip_tasks.append(task_name)
            else:
                print(f"  ✅ Will run {task_name} (file missing or stale)")

        try:
            collector = CollectorCrew()
            crew_inst = collector.crew()

            # Filter out fresh tasks
            if skip_tasks:
                crew_inst.tasks = [
                    t for t in crew_inst.tasks if t.name not in skip_tasks
                ]
                self.state.history += f"Collector: skipped fresh tasks {skip_tasks}.\n"

            # --- Auto-resolve company name from vnstock ---
            company_name = ticker  # fallback
            try:
                from vnstock import Vnstock

                listing = (
                    Vnstock().stock(symbol=ticker, source="VCI").listing.all_symbols()
                )
                match = listing[listing["symbol"] == ticker]
                if not match.empty and "organ_name" in match.columns:
                    company_name = str(match.iloc[0]["organ_name"])
                print(f"  📛 Resolved company name: {ticker} → {company_name}")
            except Exception as e:
                print(f"  ⚠️  Could not resolve company name for {ticker}: {e}")

            inputs = CollectorCrewInputs(
                stock_symbols=ticker,
                company_name=company_name,
                market_context_path=self.state.shared_data["market_context_path"],
                ticker_context_path=self.state.shared_data["ticker_context_path"],
                annual_report_md_dir=str(PROCESSED_ANNUAL_REPORTS_DIR / ticker),
                annual_report_pdf_dir=str(RAW_ANNUAL_REPORT_DIR / ticker),
                current_year=self.state.shared_data["report_year"],
            )
            result = crew_inst.kickoff(inputs=inputs.model_dump())
            self.state.history += f"Collector executed. Result: {str(result)}\n"
        except Exception as e:
            self.state.history += f"Collector Failed: {str(e)}\n"
            raise

    @listen(execute_collector)
    def execute_sentiment(self):
        """
        3. RUN SENTIMENT ANALYST CREW (full: macro + ticker)
           Skips macro sentiment tasks whose output files are still fresh (<7 days).
        """
        ticker = self.state.target_ticker
        print(f"\n[DeepDive Flow] 🚀 Launching Sentiment Analyst Crew for {ticker}...")

        # --- Freshness check: determine which tasks to skip ---
        skip_tasks: list[str] = []
        freshness_checks = {
            "summarize_current_week_macro": self.state.shared_data[
                "macro_sentiment_md_path"
            ],
            "synthesize_recent_trends": self.state.shared_data[
                "overall_macro_sentiment_md_path"
            ],
        }
        for task_name, file_path in freshness_checks.items():
            if is_file_fresh(file_path, max_age_days=7):
                age = get_file_age_days(file_path)
                print(f"  ⏭️  Skipping {task_name} (fresh: {age:.1f} days old)")
                skip_tasks.append(task_name)
            else:
                print(f"  ✅ Will run {task_name} (file missing or stale)")

        try:
            sentiment_inst = SentimentAnalystCrew()
            crew_inst = sentiment_inst.crew()

            # Filter out fresh tasks
            if skip_tasks:
                crew_inst.tasks = [
                    t for t in crew_inst.tasks if t.name not in skip_tasks
                ]
                self.state.history += f"Sentiment: skipped fresh tasks {skip_tasks}.\n"

            inputs = SentimentAnalystCrewInputs(
                stock_symbols=ticker,
                year=self.state.shared_data["report_year"],
                week=self.state.shared_data["report_week"],
                macro_sentiment_md_path=self.state.shared_data[
                    "macro_sentiment_md_path"
                ],
                overall_macro_sentiment_md_path=self.state.shared_data[
                    "overall_macro_sentiment_md_path"
                ],
                market_sentiment_dir=self.state.shared_data["market_sentiment_dir"],
                market_context_path=self.state.shared_data["market_context_path"],
                ticker_context_path=self.state.shared_data["ticker_context_path"],
                ticker_sentiment_path=self.state.shared_data["ticker_sentiment_path"],
            )
            result = crew_inst.kickoff(inputs=inputs.model_dump())
            self.state.shared_data["news_sentiment_analysis"] = str(result)
            self.state.history += (
                "Sentiment Analyst executed. Result recorded in State.\n"
            )
        except Exception as e:
            self.state.history += f"Sentiment Analyst Failed: {str(e)}\n"
            raise

    # @listen(execute_sentiment)
    # def execute_synthesizer_loop(self):
    #     """
    #     4. TODO: Integrate report_loop sub-flow here.
    #     Synthesizer → Director feedback loop → approved synthesis output.
    #     For now this is a placeholder that passes through to Reporter.
    #     """
    #     ticker = self.state.target_ticker
    #     print(
    #         f"\n[DeepDive Flow] ⏳ Synthesizer Loop placeholder for {ticker} "
    #         f"(report_loop integration pending)..."
    #     )
    #     self.state.history += "Synthesizer Loop: placeholder (not yet implemented).\n"

    # @listen(execute_synthesizer_loop)
    # def execute_reporter(self):
    #     """
    #     5. RUN REPORTER CREW (Translation & Publishing)
    #     """
    #     print(
    #         "\n[DeepDive Flow] 🚀 Launching Reporter Crew (Translation & Publishing Phase)..."
    #     )

    #     try:
    #         reporter_inst = ReporterCrew()
    #         inputs = ReporterCrewInputs(
    #             stock_symbols=self.state.target_ticker,
    #             source_md_path=self.state.shared_data["synthesizer_md_path"],
    #             pdf_output_path=self.state.shared_data["report_pdf_path"],
    #             report_title=self.state.shared_data["report_title"],
    #         )
    #         reporter_inst.run(inputs=inputs)
    #         self.state.history += "Reporter executed. Sent payload to Discord.\n"
    #     except Exception as e:
    #         self.state.history += f"Reporter Failed: {str(e)}\n"
    #         raise

    @listen(execute_sentiment)
    def finish_flow(self):
        print(
            f"\n[DeepDive Flow] 🏁 Flow successfully completed for {self.state.target_ticker}."
        )
        print("Final Execution History Logged. Terminating.")
        return self.state.history


if __name__ == "__main__":
    flow = DeepDiveFlow()
    flow.state.target_ticker = "FPT"
    print("Kicking off DeepDive Flow for testing...")
    result = flow.kickoff()
    print("Finished.")
