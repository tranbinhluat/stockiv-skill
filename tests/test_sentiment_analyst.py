import os
import sys
from pathlib import Path

# Add the src folder to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Local embedder requirement (using HuggingFace models via Chroma)
os.environ["CHROMA_HUGGINGFACE_API_KEY"] = "dummy_key"  # pragma: allowlist secret


from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew


def test_sentiment_analyst():
    print("Testing Sentiment Analyst Crew with mocked data...")
    stock_symbols = "FPT"
    current_date = "2026-03-06"  # Hardcoded for test predictability
    current_year = "2026"
    current_week = "10"

    # Setup mock file paths
    base_dir = Path(__file__).parent.parent
    macro_context_file = (
        base_dir / "data" / "raw" / "context" / f"{stock_symbols}_macro_context.md"
    )
    ticker_context_file = (
        base_dir / "data" / "raw" / "context" / f"{stock_symbols}_ticker_context.md"
    )
    market_output_file = (
        base_dir
        / "data"
        / "processed"
        / "sentiment"
        / "market"
        / f"{current_year}_W{current_week}_market_sentiment.md"
    )

    print(f"Reading Macro Context from: {macro_context_file}")
    print(f"Reading Ticker Context from: {ticker_context_file}")

    inputs = {
        "stock_symbols": stock_symbols,
        "date": current_date,
        "year": current_year,
        "week": current_week,
        "macro_context_file": str(macro_context_file),
        "ticker_context_file": str(ticker_context_file),
    }

    # Initialize Crew instance
    crew_instance = SentimentAnalystCrew().crew()

    # Skip market sentiment task if file already exists for this week
    if market_output_file.exists():
        print(
            f"\nMarket sentiment for {current_year}-W{current_week} already exists. Skipping summarize_market task."
        )
        crew_instance.tasks = [
            t for t in crew_instance.tasks if t.name != "summarize_market"
        ]

    if not crew_instance.tasks:
        print(
            "\nAll sentiment tasks for this context have already been completed today. Exiting."
        )
        return

    result = crew_instance.kickoff(inputs=inputs)

    print("\n" + "=" * 50)
    print("Sentiment Analyst Crew Result:")
    print("=" * 50)
    print(result.raw)


if __name__ == "__main__":
    test_sentiment_analyst()
