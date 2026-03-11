# Synthesizer Crew Refactor: Remove Flow, Adopt Hierarchical Manager Pattern

The current Synthesizer crew uses a custom `SynthesizerFlow` (5-step pipeline with parallel branches) to orchestrate 3 agents across 5 tasks. This is fragile, bypasses CrewAI's native delegation, and duplicates orchestration logic that should live in the crew itself.

**Goal:** Refactor the Synthesizer to use the same **hierarchical manager delegation pattern** as the Collector crew — a single `Process.hierarchical` crew where the manager delegates work to subordinates.

## User Review Required

> [!IMPORTANT]
> The `SynthesizerFlow` class and `SynthesizerState` class will be **deleted** from `synthesizer.py`. All orchestration moves into CrewAI's native hierarchical process. The `report_loop.py` flow will continue to call `SynthesizerCrew.run()` as before — only the internal implementation changes.

> [!WARNING]
> The test file `test_synthesizer_flow.py` will need to be **deleted or rewritten** since it directly imports `SynthesizerFlow`. The existing `test_synthesizer.py` should continue working with minor updates.

## Proposed Changes

### Synthesizer Crew Core

#### [MODIFY] [synthesizer.py](file:///home/luattranb/Documents/projects/stock-agent/src/stockiv/crews/synthesizer/synthesizer.py)

**1. Delete `SynthesizerFlow` and `SynthesizerState`** (lines 434–617)
- Remove the entire Flow class, all `@start`/`@listen`/`and_` logic
- Remove unused imports: `Flow`, `listen`, `start`, `and_`

**2. Restructure `SynthesizerCrew` to use hierarchical process** (lines 318–431)
- Add a `synthesizer_manager` agent (the current `lead_synthesizer` becomes the manager)
- The manager gets `allow_delegation=True`, **no tools** (same pattern as Collector's `collector_manager`)
- Workers (`data_specialist`, `forensic_accountant`) keep their tools
- Change `crew()` method:
  - Use `Process.hierarchical` with `manager_agent=self.synthesizer_manager()`
  - Filter manager out of worker list (follow Collector pattern)
- Keep all 5 tasks — they're assigned to workers but managed hierarchically
- The `run()` method stays the same interface, but now internally kicks off a single hierarchical crew

**3. Simplify `SynthesizerCrewInputs`**
- Remove flow-specific fields (`manager_directives`, `accountant_findings`, `chart_links`, `financial_summary`) — these were only used for inter-step state passing in the Flow
- Keep: `stock_symbols`, `date`, `financial_summary_path`, `annual_reports_dir`, `synthesizer_output_dir`, `sentiment_dir`, `ticker_sentiment_path`
- Add: `feedback` (Optional[str]) — Director's rejection feedback from previous loop iteration. When present, the manager prioritizes addressing the cited weaknesses

**4. Keep Pydantic output models** (`BaselineMetrics`, `SynthesizerReport`)
- These remain unchanged — they define the structured output contract

---

### Agent Prompts

#### [MODIFY] [agents.yaml](file:///home/luattranb/Documents/projects/stock-agent/src/stockiv/crews/synthesizer/config/agents.yaml)

**1. Rename `lead_synthesizer` → `synthesizer_manager`**
- Role: "Chief Synthesis Orchestrator"
- Remove all references to "Phase 1" / "Phase 2" (Flow-era concepts)
- Add explicit delegation instructions (same pattern as Collector's `collector_manager`):
  - Delegate data extraction to `data_specialist`
  - Delegate annual report forensics to `forensic_accountant`
  - Delegate chart/visualization to `data_specialist`
- Manager does NOT have tools for reading annual reports or creating charts
- Manager IS guided to delegate these to subordinates
- Manager handles the final GCCP analysis and report compilation using context from delegated task results

**2. Update `data_specialist`**
- Remove "Phase 1" / "Phase 2" language
- Add chart output notification: must report back exact file paths/markdown embeds to manager
- Add boundary rule: reject tasks outside its scope (forensic questions)

**3. Update `forensic_accountant`**
- Add boundary rule: reject tasks outside its scope (chart drawing, data queries)
- **Unavailability protocol:** If annual report markdown is not found in `{annual_reports_dir}`, must respond with clear `ANNUAL_REPORT_NOT_AVAILABLE` status — no guessing
- Designed to answer both the standard 4 forensic checks AND ad-hoc follow-up questions delegated by the manager during analysis
- Clean up the response format instructions

---

### Task Prompts (GCCP-Aligned Step-by-Step)

#### [MODIFY] [tasks.yaml](file:///home/luattranb/Documents/projects/stock-agent/src/stockiv/crews/synthesizer/config/tasks.yaml)

Reduced from 5 to **3 predefined tasks**. The manager dynamically delegates chart creation to the `data_specialist` during compilation based on what findings need visual highlighting.

---

#### Task 1: `collect_baseline_metrics` → assigned to `data_specialist`

> **Goal:** Create a comprehensive, self-contained financial baseline markdown report.

**Steps:**
1. Use `FetchRecentFinancialsTool` for `{stock_symbols}` — 3–4 years of data + latest quarter
2. Use `FetchPeerComparisonsTool` for `{stock_symbols}` — VNINDEX baseline and top competitor ratios
3. Organize into **readable markdown tables**: Current Metrics, VNINDEX, Income Statement (with YoY%), Balance Sheet, Profitability Ratios (ROE/ROA/Margins), Cash Flow (OCF/FCF), Fundamental Ratios (P/E/P/B/EV-EBITDA), Peer Comparison
4. Save to `{financial_summary_path}`

**Expected output:** `BaselineMetrics` Pydantic model as rich markdown tables. No prose — purely organized raw data.

---

#### Task 2: `forensic_annual_report_review` → assigned to `forensic_accountant`

> **Goal:** Check annual report availability, then run 4 standard GCCP forensic checks.

**Steps:**
1. List files in `{annual_reports_dir}`, find `{stock_symbols}` annual report
2. **If NOT found:** Respond with `ANNUAL_REPORT_NOT_AVAILABLE` status and stop immediately. Do not guess or fabricate data.
3. **If found:** Read the full annual report markdown
4. Run 4 checks (per `financial_reading_guide.md`): **Fake Revenue** (receivables vs revenue), **Margin Squeeze** (declining margins), **Hidden Debt** (off-balance-sheet, related parties), **Inventory Bloat** (inventory vs COGS)
5. Per check: Status (MENTIONED/NOT_MENTIONED), Exact Quote, Summary

**Expected output:** Either `ANNUAL_REPORT_NOT_AVAILABLE` or structured Q&A with evidence.

---

#### Task 3: `compile_evaluation_report` → assigned to `synthesizer_manager`

> **Goal:** Synthesize all inputs into a structured GCCP report. Delegate chart creation dynamically based on findings.

**Step 0 — Handle Feedback** *(if `{feedback}` is provided)*
- Read Director's rejection feedback, identify weaknesses cited
- Delegate additional data/charts to subordinates if needed, revise criticized sections

**Step 1 — Read All Inputs**
- Read baseline from `{financial_summary_path}`, ticker sentiment from `{ticker_sentiment_path}`, market sentiment from `{sentiment_dir}`
- Receive forensic findings from Task 2 context

**Step 2 — Classify Industry Dynamics** *(GCCP Part II.1)*
- Classify: Slow Growth / Sustainable / Fast Growth / Cyclical
- Reference `industry_guides.md` thresholds

**Step 3 — Evaluate Good Company: Qualitative** *(GCCP Part II.2–3)*
- Business Model (Input → Engine → Output), Management & Governance
- Use ticker sentiment for recent news / management statements
- **Active Q&A:** If manager spots unclear numbers or company claims, delegate follow-up questions to `forensic_accountant` (e.g., "What does the annual report say about related party transactions?" or "Find the exact revenue breakdown by segment")
- **Unavailability guard:** If Task 2 returned `ANNUAL_REPORT_NOT_AVAILABLE`, manager must NOT delegate further annual report questions to `forensic_accountant` — rely solely on baseline metrics and sentiment data
- Determine `business_model_is_good`, `management_is_good`

**Step 4 — Evaluate Good Company: Quantitative** *(GCCP Part III)*
- Capital Structure, Profitability (ROE>15%, ROA>6%), Cash Generation (OCF>NI, FCF>5%)
- Incorporate forensic accountant findings, flag anomalies
- **Active Q&A:** Delegate specific forensic questions as they arise (e.g., "Why did other payables spike 300% in Q3?" or "What is the inventory aging breakdown?") — same unavailability guard applies
- Determine `is_good`

**Step 5 — Delegate Visualizations** *(dynamic, based on findings)*
- Based on Steps 2–4 findings, delegate to `data_specialist` **specific charts** that highlight key discoveries (e.g., "Draw a chart showing the margin squeeze from 2023→2025" or "Show revenue vs receivables growth to visualize the fake revenue risk")
- Data specialist saves charts to `{synthesizer_output_dir}/charts/`, reports back markdown embed links
- Not fixed charts — manager decides what visuals best support the narrative

**Step 6 — Evaluate Cheap Price** *(GCCP Part IV)*
- Market Phase (Crisis/Fair/Bubble), Graham/Lynch criteria, Peer Comparison, Relative Valuation, Margin of Safety
- Determine `valuation_is_cheap`

**Step 7 — Target Price & Actionable Suggestion** *(GCCP Part V)*
- Calculate Fair Value → apply MoS → Suggested Buy Price
- Actionable: "BUY NOW" / "WAIT FOR P/E TO DROP TO Xx" / "AVOID"
- Critical Warnings

**Step 8 — Compile Final Report**
- Embed chart images, use clickable inline markdown links for citations
- Output as `SynthesizerReport` JSON matching Pydantic schema

**Expected output:** `SynthesizerReport` Pydantic JSON → saved as `{synthesizer_output_dir}/{stock_symbols}_GCCP_report.md`.

---

### Visualization Storage

**New folder structure for chart outputs:**
```
data/processed/synthesizer/{ticker}/
├── {ticker}_financial_summary.md    # Baseline metrics (Task 1)
├── {ticker}_GCCP_report.md          # Final report (Task 4)
└── charts/                          # NEW: dedicated chart folder
    ├── {ticker}_revenue_chart.png
    ├── {ticker}_margins_chart.png
    └── ...
```

The `data_specialist` saves charts to `{synthesizer_output_dir}/charts/` and returns the exact markdown embed syntax (e.g., `![Revenue](data/processed/synthesizer/FPT/charts/FPT_revenue_chart.png)`) so the manager can embed them in the final report.

---

### Consumer Updates

#### [MODIFY] [report_loop.py](file:///home/luattranb/Documents/projects/stock-agent/src/stockiv/flows/report_loop.py)

- Remove import of `SynthesizerCrewInputs` fields that no longer exist (`manager_directives`)
- Update `execute_synthesizer()` to pass the new simplified inputs

#### [MODIFY] [__init__.py](file:///home/luattranb/Documents/projects/stock-agent/src/stockiv/crews/__init__.py)

- Remove any re-export of `SynthesizerFlow` if present (currently only `SynthesizerCrew` is exported — no change needed)

---

### Test Updates

#### [DELETE] [test_synthesizer_flow.py](file:///home/luattranb/Documents/projects/stock-agent/tests/test_synthesizer_flow.py)

- This test imports `SynthesizerFlow` which will no longer exist

#### [MODIFY] [test_synthesizer.py](file:///home/luattranb/Documents/projects/stock-agent/tests/test_synthesizer.py)

- Update to work with new `SynthesizerCrewInputs` fields
- Add `synthesizer_output_dir`, `annual_reports_dir`, `sentiment_dir` inputs

---

### Documentation

#### [MODIFY] [README.md](file:///home/luattranb/Documents/projects/stock-agent/src/stockiv/crews/synthesizer/README.md)

- Rewrite to reflect new architecture: hierarchical process, 3 agents, 3 tasks
- Update architecture mermaid diagram (remove Flow pipeline, show hierarchical delegation)
- Update agent descriptions (manager has no tools, delegates everything)
- Update task breakdown table (3 tasks, dynamic visualization)
- Remove Flow Pipeline section entirely
- Update storage section (add `charts/` subfolder)

---

## Verification Plan

### Automated Tests

1. **Import check** — verify the module loads without errors:
   ```bash
   uv run python -c "from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew, SynthesizerCrewInputs; print('OK')"
   ```

2. **Crew instantiation** — verify hierarchical crew builds correctly:
   ```bash
   uv run python -c "
   from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew
   c = SynthesizerCrew()
   crew = c.crew()
   print(f'Process: {crew.process}')
   print(f'Manager: {crew.manager_agent.role}')
   print(f'Workers: {[a.role for a in crew.agents]}')
   print(f'Tasks: {len(crew.tasks)}')
   "
   ```

3. **Pre-commit hooks**:
   ```bash
   uv run pre-commit run --all-files
   ```

### Manual Verification

Since this crew calls real LLM APIs (Gemini) and real database queries, a full end-to-end test requires API keys and data in `stockiv.db`. **Luat, please run the following after the refactor to validate:**

```bash
# Quick smoke test with the existing test script
uv run python tests/test_synthesizer.py
```

Watch for:
- Manager correctly delegating data collection to `data_specialist`
- Manager correctly delegating forensic questions to `forensic_accountant`
- Manager dynamically delegating chart creation to `data_specialist` based on findings
- Charts saved to `data/processed/synthesizer/{ticker}/charts/`
- Final markdown report generated with embedded chart links
