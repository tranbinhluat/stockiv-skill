"""
Weekly Report Flow - Runs Collector (context tasks only) and Sentiment Analyst.
"""

from crewai.flow.flow import Flow, listen, start
from datetime import datetime

from stockiv.config.paths import (
    PROCESSED_SENTIMENT_MARKET_DIR,
    RAW_CONTEXT_DIR,
    REPORT_MARKET_DIR,
)
from stockiv.flows.state import PipelineState
from stockiv.crews.collector.collector import CollectorCrew, CollectorCrewInputs
from stockiv.crews.sentiment_analyst.sentiment_analyst import (
    SentimentAnalystCrew,
    SentimentAnalystCrewInputs,
)
from stockiv.utils.freshness import is_file_fresh, get_file_age_days


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
        macro_sentiment_title = f"{year}_W{week_num:02d}_macro_sentiment"
        self.state.shared_data["report_title"] = report_title

        self.state.shared_data["market_context_path"] = str(
            RAW_CONTEXT_DIR / "market_context.md"
        )
        self.state.shared_data["market_sentiment_dir"] = str(
            PROCESSED_SENTIMENT_MARKET_DIR
        )

        # Intermediate markdowns stay in processed dir and explicitly declare intent (no "report" in name)
        self.state.shared_data["macro_sentiment_md_path"] = str(
            PROCESSED_SENTIMENT_MARKET_DIR / f"{macro_sentiment_title}.md"
        )
        self.state.shared_data["overall_macro_sentiment_md_path"] = str(
            PROCESSED_SENTIMENT_MARKET_DIR / f"{year}_overall_macro_sentiment.md"
        )

        # Only the finalized output goes to reports directory
        self.state.shared_data["report_pdf_path"] = str(
            REPORT_MARKET_DIR / f"{report_title}.pdf"
        )

    @listen(setup_flow)
    def execute_collector_news(self):
        """
        Run Collector Crew, but restrict it to only the macro news context task.
        Skips if the output file is still fresh (<7 days old).
        """
        market_context_path = self.state.shared_data["market_context_path"]

        if is_file_fresh(market_context_path, max_age_days=7):
            age = get_file_age_days(market_context_path)
            print(
                f"\n[WeeklyReport Flow] ⏭️  Skipping Collector (macro context fresh: {age:.1f} days old)"
            )
            self.state.history += (
                f"Collector skipped: market_context.md is fresh ({age:.1f} days old).\n"
            )
            return

        print("\n[WeeklyReport Flow] 🚀 Launching Collector Crew (Macro News Only)...")

        try:
            collector_inst = CollectorCrew()
            crew_inst = collector_inst.crew()

            # Filter the tasks to ONLY include macro context task
            target_task_names = ["fetch_macro_context_task"]
            filtered_tasks = [t for t in crew_inst.tasks if t.name in target_task_names]

            if not filtered_tasks:
                raise ValueError(
                    "Could not find context tasks in the CollectorCrew configuration."
                )

            crew_inst.tasks = filtered_tasks

            inputs = CollectorCrewInputs(
                market_context_path=market_context_path,
                current_year=self.state.shared_data["report_year"],
            )
            result = crew_inst.kickoff(inputs=inputs.model_dump())
            self.state.history += (
                f"Collector (Macro News Only) executed. Result: {str(result)}\n"
            )
        except Exception as e:
            self.state.history += f"Collector (Macro News Only) Failed: {str(e)}\n"
            raise

    @listen(execute_collector_news)
    def execute_sentiment(self):
        print(
            f"\n[WeeklyReport Flow] 🚀 Launching Sentiment Analyst Crew (Macro Phase)... (Year: {self.state.shared_data.get('report_year')}, Week: {self.state.shared_data.get('report_week')})..."
        )

        # --- Freshness check: skip tasks whose output is fresh ---
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

            # Isolate ONLY the macro sentiment tasks, then remove fresh ones
            target_task_names = [
                "summarize_current_week_macro",
                "synthesize_recent_trends",
            ]
            filtered_tasks = [
                t
                for t in crew_inst.tasks
                if t.name in target_task_names and t.name not in skip_tasks
            ]

            if not filtered_tasks:
                print(
                    "  ⏭️  All Sentiment macro tasks are fresh — skipping Sentiment crew entirely."
                )
                self.state.history += "Sentiment skipped: all macro tasks fresh.\n"
                return

            crew_inst.tasks = filtered_tasks

            inputs = SentimentAnalystCrewInputs(
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
            )
            result = crew_inst.kickoff(inputs=inputs.model_dump())
            self.state.shared_data["news_sentiment_analysis"] = str(result)
            self.state.history += (
                "Sentiment Analyst executed. Result recorded in State.\n"
            )
        except Exception as e:
            self.state.history += f"Sentiment Analyst Failed: {str(e)}\n"
            raise

    @listen(execute_sentiment)
    def execute_reporter(self):
        print(
            "\n[WeeklyReport Flow] 🚀 Launching Reporter Crew (Translation & Publishing Phase)..."
        )

        try:
            from stockiv.crews.reporter.reporter import ReporterCrew, ReporterCrewInputs

            reporter_inst = ReporterCrew()

            inputs = ReporterCrewInputs(
                source_md_path=self.state.shared_data["macro_sentiment_md_path"],
                pdf_output_path=self.state.shared_data["report_pdf_path"],
                report_title=self.state.shared_data["report_title"],
            )
            reporter_inst.run(inputs=inputs)
            self.state.history += "Reporter executed. Sent payload to Discord.\n"
        except Exception as e:
            self.state.history += f"Reporter Failed: {str(e)}\n"
            raise

    @listen(execute_reporter)
    def finish_flow(self):
        print("\n[WeeklyReport Flow] 🏁 Flow successfully completed.")
        print("Final Execution History Logged. Terminating.")
        return self.state.history


if __name__ == "__main__":
    flow = WeeklyReportFlow()
    # flow.plot(filename="./weekly.html")
    print("Kicking off Weekly Report Flow for testing...")
    result = flow.kickoff()
    print("Finished.")
