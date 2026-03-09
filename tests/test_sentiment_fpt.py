import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew

load_dotenv()

def run_sentiment_test():
    ticker = "FPT"
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    year, week, _ = now.isocalendar()

    report_title = f"{year}_W{week:02d}_{ticker}_sentiment_test"
    report_md_path = os.path.abspath(f"data/processed/sentiment/ticker/{ticker}/{report_title}.md")
    overall_report_md_path = os.path.abspath(f"data/processed/sentiment/market/{year}_overall_market_sentiment_test.md")
    
    market_context_path = os.path.abspath("data/raw/context/market_context.md")
    ticker_context_path = os.path.abspath(f"data/raw/context/{ticker}_ticker_context.md")
    
    os.makedirs(os.path.dirname(report_md_path), exist_ok=True)
    os.makedirs(os.path.dirname(overall_report_md_path), exist_ok=True)

    print(f"🚀 Launching Isolated Sentiment Analyst Crew for {ticker}...")
    
    try:
        crew = SentimentAnalystCrew()
        result = crew.crew().kickoff(
            inputs={
                "stock_symbols": ticker,
                "date": current_date,
                "year": str(year),
                "week": str(week),
                "report_title": report_title,
                "report_md_path": report_md_path,
                "overall_report_md_path": overall_report_md_path,
                "market_context_path": market_context_path,
                "ticker_context_path": ticker_context_path,
            }
        )
        print("\n✅ Execution Finished. Output:")
        print("-------------------------------")
        print(result)
        print("-------------------------------")
        print(f"Wrote outputs to {report_md_path} and {overall_report_md_path} (if used internally).")
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")

if __name__ == "__main__":
    run_sentiment_test()
