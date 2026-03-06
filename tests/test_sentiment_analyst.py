import os
import sys
from pathlib import Path

# Add the src folder to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Local embedder requirement (using HuggingFace models via Chroma)
os.environ["CHROMA_HUGGINGFACE_API_KEY"] = "dummy_key" # pragma: allowlist secret

from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew

def test_sentiment_analyst():
    print("Testing Sentiment Analyst Crew with mocked data...")
    stock_symbols = "FPT"
    
    # Setup mock file paths
    base_dir = Path(__file__).parent.parent
    macro_context_file = base_dir / "data" / "raw" / "context" / f"{stock_symbols}_macro_context.md"
    ticker_context_file = base_dir / "data" / "raw" / "context" / f"{stock_symbols}_ticker_context.md"
    
    print(f"Reading Macro Context from: {macro_context_file}")
    print(f"Reading Ticker Context from: {ticker_context_file}")
    
    inputs = {
        "stock_symbols": stock_symbols,
        "macro_context_file": str(macro_context_file),
        "ticker_context_file": str(ticker_context_file),
    }

    crew = SentimentAnalystCrew().crew()
    result = crew.kickoff(inputs=inputs)
    
    print("\n" + "="*50)
    print("Sentiment Analyst Crew Result:")
    print("="*50)
    print(result.raw)

if __name__ == "__main__":
    test_sentiment_analyst()
