"""
test_synthesizer.py

Test script to validate the refactored Synthesizer Crew with hierarchical
manager delegation pattern (Process.hierarchical).
"""

import os
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew, SynthesizerCrewInputs
from stockiv.config.paths import (
    PROCESSED_SYNTHESIZER_DIR,
    PROCESSED_ANNUAL_REPORTS_DIR,
    PROCESSED_SENTIMENT_TICKER_DIR,
)


def test_synthesizer():
    # Force tracing on for this test run
    os.environ["CREWAI_TRACING_ENABLED"] = "true"

    ticker = "FPT"
    synthesizer_ticker_dir = PROCESSED_SYNTHESIZER_DIR / ticker
    charts_dir = synthesizer_ticker_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Instantiating Hierarchical Synthesizer Crew...")
    crew_instance = SynthesizerCrew()
    crew = crew_instance.crew()

    print(f"  Process: {crew.process}")
    print(f"  Manager: {crew.manager_agent.role}")
    print(f"  Workers: {[a.role for a in crew.agents]}")
    print(f"  Tasks: {len(crew.tasks)}")

    inputs = SynthesizerCrewInputs(
        stock_symbols=ticker,
        date="2026-03-11",
        financial_summary_path=str(
            synthesizer_ticker_dir / f"{ticker}_financial_summary.md"
        ),
        annual_reports_dir=str(PROCESSED_ANNUAL_REPORTS_DIR),
        synthesizer_output_dir=str(synthesizer_ticker_dir),
        sentiment_dir=str(PROCESSED_SENTIMENT_TICKER_DIR),
        ticker_sentiment_path=str(
            PROCESSED_SENTIMENT_TICKER_DIR / ticker / "2026_W11_sentiment.md"
        ),
        report_version=1,
    )

    print("\n🚀 Kicking off Hierarchical Synthesis and Evaluation...")
    result = crew_instance.run(inputs=inputs)

    print("\n" + "=" * 50)
    print("FINAL SYNTHESIZER EVALUATION:")
    print("=" * 50)

    # Render the Pydantic object as beautiful Markdown
    if hasattr(result, "pydantic") and result.pydantic:
        md_text = result.pydantic.to_markdown()
        print(md_text)

        # Physically save the markdown report
        out_path = synthesizer_ticker_dir / f"{ticker}_GCCP_report_v1.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"\n✅ Report successfully saved to: {out_path}")
    else:
        print(result.raw)

    print("=" * 50 + "\n")


if __name__ == "__main__":
    test_synthesizer()
