"""
Weekly Report Flow - Runs Collector (context tasks only) and Sentiment Analyst.
"""

from crewai.flow.flow import Flow, listen, start
import sys
import os

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

            result = crew_inst.kickoff()
            self.state.history += (
                f"Collector (Macro News Only) executed. Result: {str(result)}\n"
            )
        except Exception as e:
            self.state.history += f"Collector (Macro News Only) Failed: {str(e)}\n"

    @listen(execute_collector_news)
    def execute_sentiment(self):
        from datetime import datetime

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        year, week_num, _ = now.isocalendar()

        print(
            f"\n[WeeklyReport Flow] 🚀 Launching Sentiment Analyst Crew (Macro Phase)... (Year: {year}, Week: {week_num})..."
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
                inputs={"date": current_date, "year": str(year), "week": str(week_num)}
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

            # Use the output from the sentiment analyst step as input
            # If in mock mode, use a hardcoded path to the existing report
            if self.state.is_mock:
                print(
                    "[WeeklyReport Flow - MOCK] Passing mock sentiment file path to Reporter..."
                )
                # Note: The file path must be absolute to avoid path resolution issues with FileReadTool
                report_file_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../../data/processed/sentiment/market/2026_overall_market_sentiment.md",
                    )
                )
            else:
                from datetime import datetime

                now = datetime.now()
                year = now.strftime("%Y")
                report_file_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        f"../../../data/processed/sentiment/market/{year}_overall_market_sentiment.md",
                    )
                )

            crew_inst.kickoff(inputs={"report_file_path": report_file_path})
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
