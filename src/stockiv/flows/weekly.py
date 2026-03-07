"""
Weekly Report Flow - Runs Collector (context tasks only) and Sentiment Analyst.
"""

from crewai.flow.flow import Flow, listen, start
import sys
import os
from pathlib import Path

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
        print(f"\n[WeeklyReport Flow] 🚀 Launching Collector Crew (Macro News Only)...")

        if self.state.is_mock:
            print(f"[WeeklyReport Flow - MOCK] Bypassing Collector Crew...")
            self.state.history += f"Collector executed (MOCK). Result: Mocked Dataset\n"
            return 

        try:
            collector_inst = CollectorCrew()
            crew_inst = collector_inst.crew()
            
            # Filter the tasks to ONLY include macro context tool
            target_task_names = ["fetch_macro_context_task"]
            filtered_tasks = [t for t in crew_inst.tasks if t.name in target_task_names]
            
            if not filtered_tasks:
                raise ValueError("Could not find context tasks in the CollectorCrew configuration.")
            
            crew_inst.tasks = filtered_tasks
            
            # We must also ensure any dependencies (context) on removed tasks are cleared
            # Since fetch_macro doesn't depend on financials, and fetch_ticker depends on macro,
            # this subset stands alone properly.
            
            result = crew_inst.kickoff()
            self.state.history += f"Collector (Macro News Only) executed. Result: {str(result)}\n"
        except Exception as e:
            self.state.history += f"Collector (Macro News Only) Failed: {str(e)}\n"

    @listen(execute_collector_news)
    def execute_sentiment(self):
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        year, week_num, _ = now.isocalendar()
        
        print(f"\n[WeeklyReport Flow] 🚀 Launching Sentiment Analyst Crew (Macro Phase)... (Year: {year}, Week: {week_num})...")

        if self.state.is_mock:
            self.state.history += f"Sentiment Analyst executed (MOCK).\n"
            return
            

        try:
            sentiment_inst = SentimentAnalystCrew()
            crew_inst = sentiment_inst.crew()
            
            # Isolate ONLY the macro sentiment tasks
            target_task_names = ["summarize_current_week_macro", "synthesize_recent_trends"]
            filtered_tasks = [t for t in crew_inst.tasks if t.name in target_task_names]
            
            if not filtered_tasks:
                raise ValueError("Could not find macro sentiment tasks in the SentimentAnalystCrew configuration.")
                
            crew_inst.tasks = filtered_tasks
            
            result = crew_inst.kickoff(inputs={
                "date": current_date,
                "year": str(year),
                "week": str(week_num)
            })
            self.state.shared_data["news_sentiment_analysis"] = str(result)
            self.state.history += f"Sentiment Analyst executed. Result recorded in State.\n"
        except Exception as e:
            self.state.history += f"Sentiment Analyst Failed: {str(e)}\n"
        
    @listen(execute_sentiment)
    def finish_flow(self):
        print(f"\n[WeeklyReport Flow] 🏁 Flow successfully completed.")
        print("Final Execution History Logged. Terminating.")
        return self.state.history
