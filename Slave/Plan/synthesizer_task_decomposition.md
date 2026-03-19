# Synthesizer Task Decomposition Plan
> **Status:** APPROVED (2026-03-19)
> **Branch:** `refactor/synthesizer-task-decomposition`

## Goal
Break the monolithic `compile_evaluation_report` (7-step, ~5K chars) into 5 focused sequential tasks. Move GCCP framework (~26K chars) out of manager backstory → inject per-task.

## Architecture: Before vs After

### Before (3 tasks)
```
detect_quantitative_anomalies → forensic_annual_report_review → compile_evaluation_report (7 steps, all framework in backstory)
```

### After (7 tasks)
```
detect_quantitative_anomalies
  → forensic_annual_report_review
    → evaluate_qualitative_goodness  [Part II + industry_guides]
      → evaluate_quantitative_goodness  [Part III + financial_reading_guide]
        → evaluate_cheap_price  [Part IV-V + criteria + market_context]
          → compile_final_report  [output format only]
```

Each downstream task sees all upstream context via CrewAI sequential context passing.

## File Changes

### `agents.yaml`
- **Remove** `{gccp_knowledge}` from `synthesizer_manager` backstory
- Keep: coworker rules, anti-hallucination rules, delegation rules, tool rules
- Framework knowledge moves entirely to task descriptions

### `tasks.yaml`
- **Remove** `compile_evaluation_report`
- **Add** 4 new tasks:

| Task | Framework Injected | Reads | Delegates To |
|---|---|---|---|
| `evaluate_qualitative_goodness` | Part II + industry_guides | sentiment + annual reports | forensic_accountant, market_researcher, data_specialist |
| `evaluate_quantitative_goodness` | Part III + financial_reading_guide | financial_summary + anomaly context | data_specialist |
| `evaluate_cheap_price` | Part IV-V + criteria + market_context | financial_summary + upstream qualitative context | data_specialist |
| `compile_final_report` | Output schema only | all upstream outputs | data_specialist (final charts) |

- **Update** `evaluate_feedback` — inject framework sections since backstory no longer has them

### `synthesizer.py`
- Remove GCCP backstory injection from `synthesizer_manager()` method
- Add 4 new `@task` methods with per-task framework injection via `kb.*` properties
- Update `crew()` task list: 3 → 7 tasks
- Update `_build_evaluate_feedback_task()` to inject `kb.framework` + `kb.criteria` + `kb.market_context`

### `report_loop.py`
- Minimal changes. `SynthesizerCrew.run()` API contract unchanged.
- `output_file` moves from `compile_evaluation_report` to `compile_final_report`

## Design Decisions
1. Industry/Lynch + Business Model + Management stay together in `evaluate_qualitative_goodness`
2. Charts generated inline per-task (not a separate visual task)
3. Revision stays as single "patch full report" task (`evaluate_feedback`)
4. All tasks assigned to `synthesizer_manager` agent (same as before)

## Verification
1. `uv run pre-commit run --all-files`
2. Crew instantiation smoke test (7 tasks, 5 agents)
3. Full report loop via `uv run python -m stockiv` for FPT
