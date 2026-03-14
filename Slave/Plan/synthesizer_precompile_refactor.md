# Refactor: Pre-compile Synthesizer Baseline Data

The user noted that asking the `data_specialist` LLM to sequentially invoke `append_to_file` to write 5 large Markdown tables is prone to hallucination and skipping (as seen in the isolated test).

To fix this, we will write a normal Python function to execute these tools deterministically *before* the Synthesizer crew even starts, ensuring the `FPT_financial_summary.md` file is perfectly formatted every time.

## Proposed Changes

### [MODIFY] `src/stockiv/crews/synthesizer/synthesizer.py`

1. **Add a Pre-Execution Method**
   Create a new method `pre_compile_baseline_metrics(self, inputs: dict)` inside the `SynthesizerCrew` class.
   This method will manually instantiate and sequentially call the data extraction tools:
   - `FetchCurrentMarketSnapshotTool()._run(ticker)`
   - `FetchRecentFinancialsTool()._run(ticker)`
   - `FetchPeerComparisonsTool()._run(ticker)`
   - `CalculateFrameworkMetricsTool()._run(ticker)`

   It will then assemble these results into a unified Markdown string and write it directly to the `financial_summary_path` provided in the inputs.

2. **Adjust the Data Specialist Agent**
   - The Data Specialist no longer needs the `collect_baseline_metrics` task.
   - However, the manager might still want to ask the Data Specialist ad-hoc data questions. So we will keep the agent around but remove its primary starting task.

### [MODIFY] `src/stockiv/crews/synthesizer/config/tasks.yaml`

1. **Remove `collect_baseline_metrics`**
   - Delete the entire YAML block for this task. It is now handled deterministically by Python.

### [MODIFY] `src/stockiv/main.py`

1. **Invoke the Pre-Compilation Step**
   - Before calling `SynthesizerCrew().crew().kickoff(...)`, add a step to call `SynthesizerCrew().pre_compile_baseline_metrics(inputs)`.
   - This ensures the file exists for the Synthesizer Manager to read.
