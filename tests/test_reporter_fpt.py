import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from stockiv.crews.reporter.reporter import ReporterCrew

load_dotenv()


def run_reporter_test():
    print("🚀 Launching Isolated Reporter Crew for FPT Sentiment Test...")
    fpt_md = os.path.abspath(
        "data/processed/sentiment/ticker/FPT/2026_W11_FPT_sentiment_test.md"
    )
    fpt_pdf = os.path.abspath(
        "data/processed/reports/FPT/2026_W11_FPT_sentiment_test.pdf"
    )
    os.makedirs(os.path.dirname(fpt_pdf), exist_ok=True)

    try:
        crew_fpt = ReporterCrew().crew()
        crew_fpt.kickoff(
            inputs={
                "stock_symbols": "FPT",
                "report_title": "FPT Sentiment Analysis Test",
                "report_file_path": fpt_md,
                "pdf_output_path": fpt_pdf,
            }
        )
        print("\n✅ FPT Reporter Finished.")
    except Exception as e:
        print(f"\n❌ Error during FPT Reporter execution: {e}")

    print("\n🚀 Launching Isolated Reporter Crew for Market Sentiment Test...")
    market_md = os.path.abspath(
        "data/processed/sentiment/market/2026_overall_market_sentiment_test.md"
    )
    market_pdf = os.path.abspath(
        "data/processed/reports/market/2026_overall_market_sentiment_test.pdf"
    )
    os.makedirs(os.path.dirname(market_pdf), exist_ok=True)

    try:
        crew_market = ReporterCrew().crew()
        crew_market.kickoff(
            inputs={
                "stock_symbols": "Vietnam Market",
                "report_title": "Vietnam Market Sentiment Analysis Test",
                "report_file_path": market_md,
                "pdf_output_path": market_pdf,
            }
        )
        print("\n✅ Market Reporter Finished.")
    except Exception as e:
        print(f"\n❌ Error during Market Reporter execution: {e}")


if __name__ == "__main__":
    run_reporter_test()
