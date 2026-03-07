import os
import asyncio
from stockiv.crews.synthesizer.synthesizer import SynthesizerFlow


async def run_flow():
    # Force tracing on for this test run
    os.environ["CREWAI_TRACING_ENABLED"] = "true"

    print("🚀 Initializing Synthesizer Flow...")
    flow = SynthesizerFlow()

    # Optional: Generate the HTML plot of the flow state machine
    # try:
    #     flow.plot("SynthesizerFlowPlot.html")
    #     print("✅ Plot generated at SynthesizerFlowPlot.html")
    # except Exception as e:
    #     print(f"⚠️ Could not generate flow plot: {e}")

    inputs = {"stock_symbols": "FPT", "date": "2026-03-06"}

    print("\n🚀 Executing Synthesizer Flow Async...")
    await flow.kickoff_async(inputs=inputs)

    print("\n" + "=" * 50)
    print("✅ Flow Execution Complete")
    print("=" * 50)
    print(
        "Flow ran successfully. Report physically saved by the @listen(run_synthesizer_crew) node."
    )
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(run_flow())
