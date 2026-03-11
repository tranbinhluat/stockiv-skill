# Synthesizer Crew Refactor v2: Hierarchical + File-Based Feedback Loop

**Status:** IMPLEMENTED ✅ (2026-03-11)
**Branch:** `feature/synthesizer-hierarchical-refactor`

## Summary

Refactored the Synthesizer crew from a fragile `SynthesizerFlow` (5-step pipeline with parallel branches)
to a clean `Process.hierarchical` manager delegation pattern matching the Collector crew.

## Architecture

- **3 agents:** `synthesizer_manager` (manager, delegates), `data_specialist` (worker), `forensic_accountant` (worker)
- **3 tasks:** `collect_baseline_metrics`, `forensic_annual_report_review`, `compile_evaluation_report`
- **Manager tools:** `FileReadTool`, `DirectoryReadTool(sentiment)`, `search_market_context`
- **Anti-hallucination rule:** Manager STRICTLY FORBIDDEN from reading annual reports

## File-Based Versioned Feedback Loop

Each Synthesizer ↔ Director loop writes versioned files to disk:
```
data/processed/synthesizer/{ticker}/
├── {ticker}_GCCP_report_v1.md
├── {ticker}_director_review_v1.md
├── {ticker}_GCCP_report_v2.md
├── {ticker}_director_review_v2.md
└── charts/
```

## Files Changed

- `src/stockiv/crews/synthesizer/synthesizer.py` — deleted Flow, hierarchical crew
- `src/stockiv/crews/synthesizer/config/agents.yaml` — 3 agents with boundary rules
- `src/stockiv/crews/synthesizer/config/tasks.yaml` — 3 GCCP-aligned tasks
- `src/stockiv/crews/synthesizer/README.md` — updated docs
- `src/stockiv/crews/director/director.py` — FileReadTool, file-based review output
- `src/stockiv/crews/director/config/tasks.yaml` — reads from file path
- `src/stockiv/flows/report_loop.py` — versioned feedback loop
- `tests/test_synthesizer.py` — updated inputs
- `tests/test_synthesizer_flow.py` — DELETED
