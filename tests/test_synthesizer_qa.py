"""
test_synthesizer_qa.py

Standalone script to test the interaction between the Lead Synthesizer and the Forensic Accountant.
Focuses specifically on the Q&A delegation loop over an Annual Report document.
"""

from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew
from crewai import Crew, Process, Task
import os
import shutil


def test_synthesizer_qa_loop():
    print("🚀 Initializing test environment...")

    # Ensure a dummy annual report exists for the accountant to read
    os.makedirs("data/raw/annual_reports", exist_ok=True)
    report_target = os.path.abspath("data/raw/annual_reports/FPT_annual_report.md")

    # Copy the preview from tests/ if our target report doesn't exist
    if not os.path.exists(report_target):
        if os.path.exists("tests/FPT_Baocaothuongnien_2024_preview.md"):
            shutil.copy("tests/FPT_Baocaothuongnien_2024_preview.md", report_target)
            print(f"Created mocked report at {report_target}")
        else:
            with open(report_target, "w") as f:
                f.write("""# FPT 2024 Annual Report

## 1. Accounting Policies
The company applies a straight-line depreciation policy. Buildings are depreciated over 10 to 25 years, while machinery and equipment are depreciated over 3 to 7 years.

## 2. Market Outlook
The board discussed the potential of AI and semiconductor markets.

## 3. Related Party Transactions
During the year, the company recorded a transaction of 500 billion VND with its subsidiary, FPT Software, for IT infrastructure leasing.
""")
            print(f"Created rich dummy report at {report_target}")

    print("\n🚀 Instantiating Synthesizer Crew...")
    synth = SynthesizerCrew()

    lead_agent = synth.lead_synthesizer()
    accountant_agent = synth.forensic_accountant()

    from crewai_tools import FileReadTool

    accountant_agent.tools = [FileReadTool(file_path=report_target)]

    qa_task = Task(
        description="""
        Your sole task is to determine the forensic accounting integrity for FPT.
        You MUST delegate a BATCH of 3 questions to your coworker `forensic_accountant`.
        You must ask them:
        1. What is the explicit depreciation policy and useful life of assets?
        2. Are there any related party transactions mentioned? Provide the numbers.
        3. Do they mention "alien invasions" or UFOs?

        Remember:
        - Delegate this ALL IN ONE MESSAGE.
        - The accountant will reply with a strict format containing 'MENTIONED' or 'NOT_MENTIONED' and Exact Quotes.
        """,
        expected_output="A summary report of the accountant's exact structured answers.",
        agent=lead_agent,
    )

    test_crew = Crew(
        agents=[lead_agent, accountant_agent],
        tasks=[qa_task],
        process=Process.sequential,
        verbose=True,
    )

    print("\n🚀 Kicking off the Q&A testing delegation loop...")
    result = test_crew.kickoff(inputs={"stock_symbols": "FPT"})

    print("\n" + "=" * 50)
    print("FINAL Q&A SUMMARY FROM LEAD:")
    print("=" * 50)
    print(result.raw)


if __name__ == "__main__":
    test_synthesizer_qa_loop()
