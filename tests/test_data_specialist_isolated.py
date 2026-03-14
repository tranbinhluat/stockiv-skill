# ruff: noqa: E402
import os
import sys
from pathlib import Path

# Setup paths to ensure imports work
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from crewai import Crew, Process
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew, SynthesizerCrewInputs


def run_isolated():
    os.environ["CREWAI_STORAGE_DIR"] = str(
        project_root / "data" / "processed" / "synthesizer" / "FPT" / "crewai_storage"
    )

    # Initialize the crew components
    s_crew = SynthesizerCrew()

    # Isolate just the data specialist and its baseline metrics task
    test_crew = Crew(
        agents=[s_crew.data_specialist()],
        tasks=[s_crew.collect_baseline_metrics()],
        process=Process.sequential,
        verbose=True,
        tracing=True,
    )

    output_path = str(
        project_root
        / "data"
        / "processed"
        / "synthesizer"
        / "FPT"
        / "FPT_financial_summary_isolated.md"
    )

    # Provide the necessary inputs for the templating engine
    inputs = SynthesizerCrewInputs(
        stock_symbols="FPT",
        date="2026-03-14",
        financial_summary_path=output_path,
        annual_reports_dir=str(project_root / "data" / "processed" / "annual_reports"),
    )

    print("Starting isolated task run for FPT...")
    print(f"Expected output path: {output_path}")

    test_crew.kickoff(inputs=inputs.model_dump())

    print("\n--- EXECUTION FINISHED ---")
    if os.path.exists(output_path):
        print(f"Output successfully written to {output_path}")
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"Generated file has {len(lines)} lines.")
    else:
        print(f"WARNING: Output file was not generated at {output_path}")


if __name__ == "__main__":
    run_isolated()
