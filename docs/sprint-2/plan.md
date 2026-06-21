# Sprint 2 — compare-flow + Fundamentals Dependency Fix

> **Sprint Goal:** Ship `compare-flow` SKILL.md (analyst-visible win) and fix `analyze-fundamentals` dependency contract to enable parallel Step 2 in deepdive-flow.
> **Branch:** `feat/sprint-2`
> **Estimated effort:** M · 4–7 days

---

## Context

Sprint 2 delivers the two commitments locked during the brainstorm vote:
1. **compare-flow** (Kira's Sprint 2 #1 condition) — design contract already written at `docs/sprint-1/compare-flow-design.md`
2. **`analyze-fundamentals` dependency contract fix** (Sage's Sprint 2 #2 condition) — restructure to accept partial execution, enabling parallel Step 2 in deepdive-flow

Also cleans up 3 known issues flagged in `docs/sprint-1/done.md`.

---

## Pre-Sprint (no commits needed — read-only)

Before touching any files, verify:
1. Sprint 1 plugin structure is correct: `ls .agents/plugins/stockiv-plugin/skills/` → 8 skills + `_template`
2. Read `docs/sprint-1/compare-flow-design.md` — this is the spec for Task 1
3. Read `analyze-fundamentals/SKILL.md` carefully — note the Part II (needs sentiment) vs Part III (doesn't) boundary

---

## Prioritized Task List

| # | Task | Owner | Est | Description |
|---|------|-------|-----|-------------|
| 1 | Write `compare-flow/SKILL.md` | Nova + Kira | 2h | New orchestrator skill. Full spec below. |
| 2 | Fix `analyze-fundamentals` dependency contract | Sage | 2h | Split into quant-phase + qual-phase. Conditional dependency on sentiment. See spec below. |
| 3 | Rewrite `deepdive-flow` Step 2 for parallelism | Sage | 1h | Add conditional parallel branch when macro cached. See spec below. |
| 4 | Fix agent path typos in `weekly-flow/SKILL.md` | Milo | 15m | `.agents.md` → `.agent.md` in two subagent references |
| 5 | Fix sentiment path in `skill-routing.md` + `knowledge-map.md` | Milo | 30m | Update spec path to match actual versioned path `{TICKER}/{YEAR}_W{WW}_sentiment.md` |
| 6 | Register `compare-flow` in `skill-routing.md` | Milo | 30m | Move from `[planned]` to registered, fill all fields |
| 7 | Update `AGENTS.md` routing table | Milo | 15m | Add `/compare TICKER1 TICKER2` row |
| 8 | Write `docs/sprint-2/done.md` | Nova | 30m | Sprint done doc |

---

## Work Schedule

### Phase 1 — compare-flow (Task 1)
- Write `compare-flow/SKILL.md` from design contract
- Commit: `feat: add compare-flow skill`

### Phase 2 — Fundamentals + Deepdive Parallelism (Tasks 2–3)
- Restructure `analyze-fundamentals` into two phases
- Update `deepdive-flow` Step 2 for conditional parallelism
- Commit: `feat: split analyze-fundamentals into quant/qual phases, enable parallel deepdive Step 2`

### Phase 3 — Bug Fixes + Registry Updates (Tasks 4–7)
- Fix `weekly-flow` agent path typos
- Fix sentiment path in routing/knowledge docs
- Register compare-flow in routing registry
- Update AGENTS.md
- Commit: `fix: agent path typos, sentiment path, register compare-flow in routing`

### Phase 4 — Done Doc (Task 8)
- Commit: `chore: sprint 2 done`

---

## Detailed Specs

---

### Task 1 — `compare-flow/SKILL.md` spec

Create: `.agents/plugins/stockiv-plugin/skills/compare-flow/SKILL.md`

**Frontmatter:**
```yaml
---
name: compare-flow
description: Run a side-by-side GCCP comparison of two Vietnamese stocks. Use this skill when the user types /compare TICKER1 TICKER2, asks "compare FPT vs MWG", "which is better", or wants a peer analysis of two tickers. Runs full deepdive pipeline on both tickers then compiles a comparison report.
---
```

**Skill content must cover:**

1. **Trigger parsing** — extract two tickers from the command. If only one provided, ask for the second.

2. **Pre-flight check** — for each ticker, check if `data/processed/synthesizer/{TICKER}/financial_summary.md` exists and is < 7 days old. If stale/missing, run `collect-data` for that ticker first.

3. **Parallel data collection** — if both need fresh data:
   ```
   Run collect-data for TICKER1 and TICKER2 in parallel (invoke both as subagents simultaneously).
   Wait for both to complete before proceeding.
   ```

4. **Sequential per-ticker analysis** — for EACH ticker (can run in parallel if context allows, but at minimum sequential is acceptable):
   - Step A: analyze-sentiment (ticker mode)
   - Step B: analyze-fundamentals (quant phase only, parallel with A when macro cached)
   - Step C: analyze-fundamentals (qual phase, waits for A + B)
   - Step D: analyze-valuation

5. **Gatekeeper review** — invoke `Gatekeeper Reviewer` ONCE with BOTH analysis outputs. Prompt: *"Review this side-by-side GCCP comparison of {T1} vs {T2}. Validate that both tickers' numbers are accurate, logic is sound, and the comparison verdict is justified."*

6. **Compile comparison report** — save to `reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md`:
   ```markdown
   # {T1} vs {T2} — GCCP Comparison
   _Generated: {date}_
   
   ## Executive Summary
   | | {T1} | {T2} |
   |---|---|---|
   | Lynch Category | ... | ... |
   | Quality Verdict | GOOD_COMPANY / BORDERLINE / AVOID | ... |
   | Valuation Verdict | BUY NOW / WAIT / AVOID | ... |
   | Target Buy Price | {VND} | {VND} |
   | Current Price | {VND} | {VND} |
   | Upside to Target | {%} | {%} |
   
   ## Head-to-Head: Key Ratios
   | Metric | {T1} | {T2} | Better |
   |---|---|---|---|
   | ROE (5Y avg) | | | |
   | ROA (5Y avg) | | | |
   | Net Margin | | | |
   | FCF Margin | | | |
   | D/E Ratio | | | |
   | Revenue CAGR (5Y) | | | |
   | P/E | | | |
   | PEG (if Fast Grower) | | | |
   
   ## Qualitative Summary
   ### {T1}
   {3-sentence summary: Lynch category, moat, main risk}
   
   ### {T2}
   {3-sentence summary: Lynch category, moat, main risk}
   
   ## Verdict
   **If forced to choose one:** {TICKER} — {1-sentence rationale}
   **Caveat:** {context — e.g., "FPT is higher quality but more expensive; MWG offers more upside if turnaround thesis holds"}
   ```

7. **Publish to Discord** — run `uv run stockiv-publish --file reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md --channel ticker`

8. **Progress updates** — show after each major step:
   ```
   [1/6] ✅ Data collected for {T1} and {T2}
   [2/6] ✅ Analysis complete for {T1} — {quality}, {valuation}
   [3/6] ✅ Analysis complete for {T2} — {quality}, {valuation}
   [4/6] ✅ Gatekeeper: APPROVED
   [5/6] ✅ Comparison report compiled
   [6/6] ✅ Published to Discord
   ```

---

### Task 2 — `analyze-fundamentals` dependency contract fix

**File:** `.agents/plugins/stockiv-plugin/skills/analyze-fundamentals/SKILL.md`

This is a **content change** — the first in this project. Take care.

**Current problem:** The skill declares total dependency on `analyze-sentiment` at the top, but only Part II (qualitative) actually uses `{TICKER}_sentiment.md`. Part III (quantitative: ROE/ROA/margins/forensics) only needs `financial_summary.md`.

**Change:** Restructure the `## Depends On` section and add an **execution mode** flag:

Replace current `## Depends On` block:
```markdown
## Depends On

- `collect-data` — must have run (`financial_summary.md` required)
- `analyze-sentiment` — must have run (`{TICKER}_sentiment.md` required)
```

With:
```markdown
## Depends On

**Quant phase (Part III only):**
- `collect-data` — must have run (`financial_summary.md` required)
- No sentiment dependency — can run immediately after collect-data

**Qual phase (Part II — default when running standalone):**
- `collect-data` — must have run
- `analyze-sentiment` — must have run (`{TICKER}_sentiment.md` required)

## Execution Mode

This skill can be called in two modes:

### Mode A — Full (default for standalone `/fundamentals <TICKER>`)
Runs Part III first, then Part II. Requires both `financial_summary.md` and `{TICKER}_sentiment.md`.

### Mode B — Quant-only (called by `deepdive-flow` in parallel with sentiment)
Runs Part III ONLY. Requires only `financial_summary.md`. Does NOT output `{TICKER}_fundamentals.md` — outputs `{TICKER}_fundamentals_quant.md` as intermediate file.
Triggered when: deepdive-flow detects macro sentiment cache exists and calls with `[quant-only]` flag.

### Mode C — Qual-only (called by `deepdive-flow` after quant + sentiment both complete)
Runs Part II ONLY, reading `{TICKER}_fundamentals_quant.md` + `{TICKER}_sentiment.md`.
Merges outputs into final `{TICKER}_fundamentals.md`.
Triggered when: deepdive-flow has both `{TICKER}_fundamentals_quant.md` and `{TICKER}_sentiment.md`.
```

**Also update `## Input Files`:**
```markdown
## Input Files

**Always required:**
- `data/processed/synthesizer/{TICKER}/financial_summary.md` — quantitative baseline

**Required for Full or Qual-only mode:**
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md` — qualitative context
  (Use most recent weekly file — check `data/processed/sentiment/ticker/{TICKER}/` for latest `_W{WW}_` file)

**Intermediate file (Quant-only output, Qual-only input):**
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`
```

**Output file section — update:**
```markdown
## Output File

**Full mode / Qual-only mode (final output):**
`data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

**Quant-only mode (intermediate output):**
`data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`
```

Keep all other sections (Part II analysis, Part III analysis, forensic checks, output structure) completely unchanged.

---

### Task 3 — `deepdive-flow` Step 2 parallelism

**File:** `.agents/plugins/stockiv-plugin/skills/deepdive-flow/SKILL.md`

**Change:** Modify Step 2 only. Replace current Step 2 block with a conditional parallel branch:

Current Step 2:
```markdown
## Step 2 — Analyze Sentiment
Run the sentiment analysis inline (refer to the `analyze-sentiment` skill).
...
**Wait for completion.** Sentiment output is required by Step 3.
```

Replace with:
```markdown
## Step 2 — Parallel Analysis (Sentiment + Quant Fundamentals)

Check if this week's macro sentiment cache exists:
```bash
ls data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md 2>/dev/null
```

**If macro cache EXISTS (common case — weekly-flow ran this week):**

Run Step 2A and Step 2B in parallel — spawn both as concurrent subagents:

**Step 2A (parallel) — Ticker Sentiment:**
Run `analyze-sentiment` in ticker-only mode (skip macro collection since cache exists).
Output: `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

**Step 2B (parallel) — Quant Fundamentals (Part III only):**
Run `analyze-fundamentals` in `[quant-only]` mode.
Reads only: `financial_summary.md`
Output: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`

**Wait for BOTH 2A and 2B to complete.**

Then run Step 2C (sequential — requires both 2A and 2B):

**Step 2C — Qual Fundamentals (Part II only):**
Run `analyze-fundamentals` in `[qual-only]` mode.
Reads: `{TICKER}_fundamentals_quant.md` + `{TICKER}_sentiment.md`
Output: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

---

**If macro cache DOES NOT EXIST (first run of the week):**

Run sequentially:
1. `analyze-sentiment` (full — collects macro + ticker sentiment)
2. `analyze-fundamentals` (full mode — both Part III and Part II)

This path is slower but produces identical output to the parallel path.

---

After Step 2 completes (either path), confirm both outputs exist:
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

Then proceed to Step 3 (Analyze Valuation — previously Step 4).
```

**Also update progress line 2:**
```
[2/7] ✅ Sentiment + Fundamentals complete (parallel) — macro: {regime}, quality: {verdict}
```

---

## Success Criteria

- [ ] `compare-flow/SKILL.md` exists in plugin with correct frontmatter
- [ ] compare-flow SKILL.md covers: trigger parsing, pre-flight, parallel collection, per-ticker analysis, gatekeeper-once, comparison report format, Discord publish
- [ ] `analyze-fundamentals/SKILL.md` has `## Execution Mode` section with Mode A/B/C
- [ ] `analyze-fundamentals/SKILL.md` dependency declaration is conditional (quant vs qual)
- [ ] `deepdive-flow/SKILL.md` Step 2 has macro-cache conditional with parallel branch
- [ ] `weekly-flow/SKILL.md` typo fixed: `.agents.md` → `.agent.md`
- [ ] `skill-routing.md` sentiment path matches actual versioned path
- [ ] `skill-routing.md` compare-flow entry moved from `[planned]` to registered
- [ ] `AGENTS.md` has `/compare TICKER1 TICKER2` row

---

## What's NOT in This Sprint

| Feature | Reason |
|---|---|
| Screener flow | Sprint 3 |
| Watchlist digest | Sprint 3 |
| `framework.md` splitting (Concept C) | Sprint 3+ |
| Multi-ticker parallel substrate | Sprint 3 |
