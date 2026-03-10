"""
Weekly Report Flow - Runs Collector (context tasks only) and Sentiment Analyst.
"""

from crewai.flow.flow import Flow, listen, start
from datetime import datetime

from stockiv.config.paths import (
    MARKET_SENTIMENT_DIR,
    RAW_CONTEXT_DIR,
    REPORT_MARKET_DIR,
)
from stockiv.flows.state import PipelineState
from stockiv.crews.collector.collector import CollectorCrew, CollectorCrewInputs
from stockiv.crews.sentiment_analyst.sentiment_analyst import (
    SentimentAnalystCrew,
    SentimentAnalystCrewInputs,
)


class WeeklyReportFlow(Flow[PipelineState]):
    """
    Weekly Report Flow that coordinates the execution of the Collector Crew
    (restricted to searching macro) and the Sentiment Analyst Crew
    to generate the weekly sentiment summaries.
    """

    @start()
    def setup_flow(self):
        """
        1. GENERATE PIPELINE STATE AND CENTRALIZED PATHS
        """
        print("\n[WeeklyReport Flow] ⚙️ Initializing State and Output Paths...")
        now = datetime.now()
        year = now.strftime("%Y")
        _, week_num, _ = now.isocalendar()

        self.state.shared_data["report_year"] = year
        self.state.shared_data["report_week"] = f"{week_num:02d}"

        # Standard Weekly Report Formatting Example: 2026_W10_market_report
        report_title = f"{year}_W{week_num:02d}_market_report"
        self.state.shared_data["report_title"] = report_title

        self.state.shared_data["market_context_path"] = str(
            RAW_CONTEXT_DIR / "market_context.md"
        )
        self.state.shared_data["market_sentiment_dir"] = str(MARKET_SENTIMENT_DIR)
        self.state.shared_data["report_md_path"] = str(
            REPORT_MARKET_DIR / f"{report_title}.md"
        )
        self.state.shared_data["report_pdf_path"] = str(
            REPORT_MARKET_DIR / f"{report_title}.pdf"
        )
        self.state.shared_data["overall_report_md_path"] = str(
            REPORT_MARKET_DIR / f"{year}_overall_market_sentiment.md"
        )

    @listen(setup_flow)
    def execute_collector_news(self):
        """
        Run Collector Crew, but restrict it to only the macro news context task.
        """
        print("\n[WeeklyReport Flow] 🚀 Launching Collector Crew (Macro News Only)...")

        if "all" in self.state.mock_crews or "collector" in self.state.mock_crews:
            print("[WeeklyReport Flow - MOCK] Bypassing Collector Crew...")
            dummy_path = self.state.shared_data["market_context_path"]
            with open(dummy_path, "w", encoding="utf-8") as f:
                f.write(
                    "# MOCK MACRO CONTEXT\n\nThis is a mocked dataset for the market context to allow downstream crews to test effectively."
                )
            self.state.history += "Collector executed (MOCK). Result: Mocked Dataset\n"
            return

        try:
            collector_inst = CollectorCrew()
            crew_inst = collector_inst.crew()

            # Filter the tasks to ONLY include macro context tool
            target_task_names = ["fetch_macro_context_task"]
            filtered_tasks = [t for t in crew_inst.tasks if t.name in target_task_names]

            if not filtered_tasks:
                raise ValueError(
                    "Could not find context tasks in the CollectorCrew configuration."
                )

            crew_inst.tasks = filtered_tasks

            # We must also ensure any dependencies (context) on removed tasks are cleared
            # Since fetch_macro doesn't depend on financials, and fetch_ticker depends on macro,
            # this subset stands alone properly.

            # market_context_path: output file
            inputs = CollectorCrewInputs(
                market_context_path=self.state.shared_data["market_context_path"]
            )
            # Use explicit kickoff on the mutated crew_inst instead of collector_inst.run()
            result = crew_inst.kickoff(inputs=inputs.model_dump())
            self.state.history += (
                f"Collector (Macro News Only) executed. Result: {str(result)}\n"
            )
        except Exception as e:
            self.state.history += f"Collector (Macro News Only) Failed: {str(e)}\n"

    @listen(execute_collector_news)
    def execute_sentiment(self):
        current_date = datetime.now().strftime("%Y-%m-%d")

        print(
            f"\n[WeeklyReport Flow] 🚀 Launching Sentiment Analyst Crew (Macro Phase)... (Year: {self.state.shared_data.get('report_year')}, Week: {self.state.shared_data.get('report_week')})..."
        )

        if "all" in self.state.mock_crews or "sentiment" in self.state.mock_crews:
            print("[WeeklyReport Flow - MOCK] Bypassing Sentiment Analyst Crew...")
            dummy_path = self.state.shared_data["report_md_path"]
            with open(dummy_path, "w", encoding="utf-8") as f:
                f.write(
                    f"# MOCK WEEKLY REPORT\n\nGenerated for Week {self.state.shared_data.get('report_week', '00')} of {self.state.shared_data.get('report_year', '0000')}."
                )
            self.state.history += "Sentiment Analyst executed (MOCK).\n"
            return

        try:
            sentiment_inst = SentimentAnalystCrew()
            crew_inst = sentiment_inst.crew()

            # Isolate ONLY the macro sentiment tasks
            target_task_names = [
                "summarize_current_week_macro",
                "synthesize_recent_trends",
            ]
            filtered_tasks = [t for t in crew_inst.tasks if t.name in target_task_names]

            if not filtered_tasks:
                raise ValueError(
                    "Could not find macro sentiment tasks in the SentimentAnalystCrew configuration."
                )

            crew_inst.tasks = filtered_tasks

            inputs = SentimentAnalystCrewInputs(
                date=current_date,
                year=self.state.shared_data["report_year"],
                week=self.state.shared_data["report_week"],
                report_title=self.state.shared_data["report_title"],
                report_md_path=self.state.shared_data["report_md_path"],
                overall_report_md_path=self.state.shared_data["overall_report_md_path"],
                market_sentiment_dir=self.state.shared_data["market_sentiment_dir"],
                market_context_path=self.state.shared_data["market_context_path"],
            )
            # Use explicit kickoff on the mutated crew_inst instead of sentiment_inst.run()
            result = crew_inst.kickoff(inputs=inputs.model_dump())
            self.state.shared_data["news_sentiment_analysis"] = str(result)
            self.state.history += (
                "Sentiment Analyst executed. Result recorded in State.\n"
            )
        except Exception as e:
            self.state.history += f"Sentiment Analyst Failed: {str(e)}\n"

    @listen(execute_sentiment)
    def execute_reporter(self):
        print(
            "\n[WeeklyReport Flow] 🚀 Launching Reporter Crew (Translation & Publishing Phase)..."
        )

        if "all" in self.state.mock_crews or "reporter" in self.state.mock_crews:
            print("[WeeklyReport Flow - MOCK] Bypassing Reporter Crew...")
            dummy_pdf = self.state.shared_data["report_pdf_path"]
            with open(dummy_pdf, "w", encoding="utf-8") as f:
                f.write("MOCK PDF BINARY OMITTED")
            self.state.history += "Reporter executed (MOCK). Sent payload to Discord.\n"
            return

        try:
            from stockiv.crews.reporter.reporter import ReporterCrew, ReporterCrewInputs

            reporter_inst = ReporterCrew()

            inputs = ReporterCrewInputs(
                report_file_path=self.state.shared_data["report_md_path"],
                pdf_output_path=self.state.shared_data["report_pdf_path"],
                report_title=self.state.shared_data["report_title"],
            )
            reporter_inst.run(inputs=inputs)
            self.state.history += "Reporter executed. Sent payload to Discord.\n"
        except Exception as e:
            self.state.history += f"Reporter Failed: {str(e)}\n"

    @listen(execute_reporter)
    def finish_flow(self):
        print("\n[WeeklyReport Flow] 🏁 Flow successfully completed.")
        print("Final Execution History Logged. Terminating.")
        return self.state.history


if __name__ == "__main__":
    WeeklyReportFlow().plot(filename="./weekly.html")
