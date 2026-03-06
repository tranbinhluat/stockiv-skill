"""
test_synthesizer.py

Test script to validate the monolithic Chief Synthesizer's capability
to analyze and evaluate quantitative/qualitative data concurrently against the injected `kb`.
"""

from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew


def test_synthesizer():
    print("🚀 Instantiating Monolithic Synthesizer Crew...")
    crew = SynthesizerCrew().crew()

    inputs = {"stock_symbols": "FPT", "date": "2026-03-06"}

    print("\n🚀 Kicking off the Synthesis and Evaluation task...")
    result = crew.kickoff(inputs=inputs)

    print("\n" + "=" * 50)
    print("FINAL CHIEF SYNTHESIZER EVALUATION:")
    print("=" * 50)

    # Render the Pydantic object as beautiful Markdown
    if hasattr(result, "pydantic") and result.pydantic:
        md_text = result.pydantic.to_markdown()
        print(md_text)

        # Physically save the markdown report
        import os

        out_dir = "data/processed/synthesizer"
        os.makedirs(out_dir, exist_ok=True)
        out_path = f"{out_dir}/{inputs['stock_symbols']}_GCCP_report.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"\n✅ Report successfully saved to: {out_path}")
    else:
        print(result.raw)

    print("=" * 50 + "\n")


if __name__ == "__main__":
    test_synthesizer()
