from datetime import datetime
from dotenv import load_dotenv

from stockiv.config.paths import (
    MARKET_SENTIMENT_DIR,
    PROCESSED_SENTIMENT_TICKER_DIR,
    RAW_CONTEXT_DIR,
)
from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew

load_dotenv()


def run_sentiment_test():
    ticker = "FPT"
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    year, week, _ = now.isocalendar()

    report_title = f"{year}_W{week:02d}_{ticker}_sentiment_test"

    # Use centralized paths
    ticker_dir = PROCESSED_SENTIMENT_TICKER_DIR / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    report_md_path = str(ticker_dir / f"{report_title}.md")
    overall_report_md_path = str(
        MARKET_SENTIMENT_DIR / f"{year}_overall_market_sentiment_test.md"
    )

    market_context_path = str(RAW_CONTEXT_DIR / "market_context.md")
    ticker_context_path = str(RAW_CONTEXT_DIR / f"{ticker}_ticker_context.md")

    print(f"🚀 Launching Isolated Sentiment Analyst Crew for {ticker}...")

    market_sentiment_dir = str(MARKET_SENTIMENT_DIR)
    ticker_sentiment_path = str(ticker_dir / f"{year}_W{week:02d}sentiment.md")

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
                "market_sentiment_dir": market_sentiment_dir,
                "market_context_path": market_context_path,
                "ticker_context_path": ticker_context_path,
                "ticker_sentiment_path": ticker_sentiment_path,
            }
        )
        print("\n✅ Execution Finished. Output:")
        print("-------------------------------")
        print(result)
        print("-------------------------------")
        print(
            f"Wrote outputs to {report_md_path} and {overall_report_md_path} (if used internally)."
        )
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")


if __name__ == "__main__":
    run_sentiment_test()
