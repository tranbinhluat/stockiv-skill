"""
Weekly Report Flow - Runs Collector (context tasks only) and Sentiment Analyst.
"""

from crewai.flow.flow import Flow, listen, start
import sys
import os
from datetime import datetime

# Ensure the root package is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from stockiv.flows.state import PipelineState
from stockiv.crews.collector.collector import CollectorCrew
from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew


class WeeklyReportFlow(Flow[PipelineState]):
    """
    Weekly Report Flow that coordinates the execution of the Collector Crew
    (restricted to searching macro) and the Sentiment Analyst Crew
    to generate the weekly sentiment summaries.
    """

    @start()
    def execute_collector_news(self):
        """
        Run Collector Crew, but restrict it to only the macro news context task.
        """
        print("\n[WeeklyReport Flow] 🚀 Launching Collector Crew (Macro News Only)...")

        # 1. GENERATE PIPELINE STATE AND CENTRALIZED PATHS
        now = datetime.now()
        year = now.strftime("%Y")
        _, week_num, _ = now.isocalendar()

        self.state.report_year = year
        self.state.report_week = f"{week_num:02d}"

        # Standard Weekly Report Formatting Example: 2026_W10_market_report
        if self.state.is_mock:
            self.state.report_title = "2026_W10_market_report"
        else:
            self.state.report_title = f"{year}_W{week_num:02d}_market_report"

        output_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../data/processed/sentiment/market",
            )
        )
        os.makedirs(output_dir, exist_ok=True)

        self.state.report_md_path = os.path.join(
            output_dir, f"{self.state.report_title}.md"
        )
        self.state.report_pdf_path = os.path.join(
            output_dir, f"{self.state.report_title}.pdf"
        )

        # Define overall report path for the synthesize_recent_trends task
        self.state.shared_data["overall_report_md_path"] = os.path.join(
            output_dir, f"{year}_overall_market_sentiment.md"
        )

        context_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../data/raw/context",
            )
        )
        os.makedirs(context_dir, exist_ok=True)
        self.state.market_context_path = os.path.join(context_dir, "market_context.md")

        if self.state.is_mock:
            print("[WeeklyReport Flow - MOCK] Bypassing Collector Crew...")
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

            result = crew_inst.kickoff(
                inputs={
                    "market_context_path": self.state.market_context_path,
                }
            )
            self.state.history += (
                f"Collector (Macro News Only) executed. Result: {str(result)}\n"
            )
        except Exception as e:
            self.state.history += f"Collector (Macro News Only) Failed: {str(e)}\n"

    @listen(execute_collector_news)
    def execute_sentiment(self):
        current_date = datetime.now().strftime("%Y-%m-%d")

        print(
            f"\n[WeeklyReport Flow] 🚀 Launching Sentiment Analyst Crew (Macro Phase)... (Year: {self.state.report_year}, Week: {self.state.report_week})..."
        )

        if self.state.is_mock:
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

            result = crew_inst.kickoff(
                inputs={
                    "date": current_date,
                    "year": self.state.report_year,
                    "week": self.state.report_week,
                    "report_title": self.state.report_title,
                    "report_md_path": self.state.report_md_path,
                    "overall_report_md_path": self.state.shared_data[
                        "overall_report_md_path"
                    ],
                    "market_context_path": self.state.market_context_path,
                }
            )
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

        try:
            from stockiv.crews.reporter.reporter import ReporterCrew

            reporter_inst = ReporterCrew()
            crew_inst = reporter_inst.crew()

            if self.state.is_mock:
                print(
                    "[WeeklyReport Flow - MOCK] Passing mock sentiment file path to Reporter..."
                )

            crew_inst.kickoff(
                inputs={
                    "report_file_path": self.state.report_md_path,
                    "pdf_output_path": self.state.report_pdf_path,
                    "report_title": self.state.report_title,
                }
            )
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
