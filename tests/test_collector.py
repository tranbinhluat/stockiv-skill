def test_collector():
    print("Initializing Collector Crew...")
    # collector_base = CollectorCrew()
    # crew = collector_base.crew()

    # print("\n[TEST] Initiating MOCK execution of Collector Crew for stock 'FPT'...")

    # # We inject a blatant dry-run instruction to force the LLMs to skip actual tool usage
    # mock_instruction = "Help me collect data for MWG stock"

    # try:
    #     # Kickoff the crew with the injected mock instructions
    #     result = crew.kickoff(
    #         inputs={
    #             "stock_symbols": mock_instruction,
    #             "market_context_path": "data/raw/context/market_context.md",
    #             "ticker_context_path": "data/raw/context/MWG_ticker_context.md",
    #             "annual_report_md_dir": "data/processed/annual_reports",
    #             "annual_report_pdf_dir": "data/raw/annual_reports",
    #         }
    #     )

    #     print("\n\n=========================================")
    #     print("MOCK EXECUTION COMPLETED SUCCESSFULLY!")
    #     print("=========================================")
    #     print("FINAL CREW OUTPUT:")
    #     print(result)

    # except Exception as e:
    #     print(f"\n[ERROR] Mock Execution failed: {str(e)}")


if __name__ == "__main__":
    test_collector()
