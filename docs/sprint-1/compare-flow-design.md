# compare-flow Design Contract (Sprint 1 Design Note)

**Status:** Design only — SKILL.md is Sprint 2 #1

## Trigger
`/compare TICKER1 TICKER2`

## Pipeline
1. collect-data TICKER1 (parallel with step below)
2. collect-data TICKER2 (parallel with step above)
3. deepdive pipeline TICKER1 (sequential: sentiment → fundamentals → valuation)
4. deepdive pipeline TICKER2 (sequential: sentiment → fundamentals → valuation)
5. gatekeeper reviews BOTH reports in a single review pass
6. compile comparison table (side-by-side: verdicts, key ratios, target prices)
7. publish-discord (single combined post)

## Output Format
One combined markdown file: `reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md`
One PDF (same content as markdown).
NOT two separate PDFs — this creates friction for Discord post.

## Gatekeeper Behavior
Runs ONCE on the combined comparison output, not twice (once per ticker).
Gatekeeper prompt: "Review this side-by-side GCCP comparison for accuracy and publishability."

## Design Decisions Made
- Single combined output (not two separate reports)
- Gatekeeper runs once on combined output
- Parallel collection, sequential per-ticker analysis
- Trigger: `/compare TICKER1 TICKER2` (exactly two tickers in Sprint 2)
