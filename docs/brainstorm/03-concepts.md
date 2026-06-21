# Brainstorm — Phase 3: Concept Synthesis

**Date:** 2026-06-21  
**Synthesized from:** Phase 1 ideation + Phase 2 debate

---

> Three distinct architecture concepts emerged from the debate.  
> Each is a coherent, self-consistent proposal — not a mix of preferences.  
> All concepts share the same data pipeline (`data/`, `reports/`) and CLI tools (`stockiv-collect`, `stockiv-report`, `stockiv-publish`).

---

## Concept A — Conservative Migration

**One-line:** Package the existing 8 skills into the plugin format. Zero content changes.

### What Changes

The `.agents/skills/` flat directory is retired. All skills move to `stockiv-plugin`. Agent definitions get a home. AGENTS.md gets a routing table. Nothing else.

### Target Structure

```
.agents/
  plugins/
    stockiv-plugin/
      plugin.json                            ← { name, description, version }
      skills/
        collect-data/
          SKILL.md                           ← moved verbatim from .agents/skills/
        analyze-sentiment/
          SKILL.md                           ← moved verbatim
        analyze-fundamentals/
          SKILL.md                           ← moved verbatim
        analyze-valuation/
          SKILL.md                           ← moved verbatim
        deepdive-flow/
          SKILL.md                           ← moved verbatim
        weekly-flow/
          SKILL.md                           ← moved verbatim
        draft-report/
          SKILL.md                           ← moved verbatim
        publish-discord/
          SKILL.md                           ← moved verbatim
        _template/
          SKILL.md                           ← new: scaffolded boilerplate
      agents/
        stock-analyst/
          agent.json                         ← migrated from .agents/agents/
        gatekeeper-reviewer/
          agent.json                         ← migrated from .agents/agents/
        market-scout/
          agent.json                         ← migrated from .agents/agents/
      references/
        knowledge-map.md                     ← new: skill → knowledge file index
  skills/
    skill-creator/                           ← stays flat; excluded from plugin
      SKILL.md
      agents/
      references/
      eval-viewer/
```

### What Does NOT Change

- Every `SKILL.md` content is byte-for-byte identical to today's version
- All data paths: `data/processed/synthesizer/{TICKER}/`, `data/processed/sentiment/`, `data/raw/context/`, `reports/ticker/`
- All CLI commands: `uv run stockiv-collect`, `uv run stockiv-report`, `uv run stockiv-publish`
- deepdive-flow pipeline logic (still sequential: collect → sentiment → fundamentals → valuation)
- `weekly-flow` human review gate behavior

### AGENTS.md Update

Replace current prose trigger block with an explicit routing table:

```markdown
## Plugin: stockiv-plugin

| Trigger | Skill | Flow Type | Notes |
|---|---|---|---|
| `/weekly`, "báo cáo tuần", "weekly report", "macro weekly" | `weekly-flow` | Orchestrator | Macro pipeline; human review gate default ON |
| `/deepdive`, `/deepdive <TICKER>`, "phân tích sâu", "deep dive" | `deepdive-flow` | Orchestrator | Full GCCP; 7-step pipeline |
| `/collect <TICKER>`, "fetch data for" | `collect-data` | Atomic | Data freshness check first |
| `/sentiment [TICKER]`, "market mood", "macro outlook" | `analyze-sentiment` | Atomic | Standalone or upstream of deepdive |
| `/fundamentals <TICKER>`, "is this good company" | `analyze-fundamentals` | Atomic | Requires collect + sentiment first |
| `/valuation <TICKER>`, "is it cheap", "target price" | `analyze-valuation` | Atomic | Requires fundamentals first |
| `/report [TICKER]`, "export report", "generate PDF" | `draft-report` | Atomic | Requires all analysis files |
| `/publish`, "send to Discord" | `publish-discord` | Atomic | Gatekeeper APPROVED required |
```

### `references/knowledge-map.md` (new file)

```markdown
# Knowledge Map — stockiv-plugin

Maps each skill to the knowledge files it reads, and which sections.

| Skill | Knowledge Files | Sections |
|---|---|---|
| `analyze-fundamentals` | `src/stockiv/knowledge/framework.md` | Part II (Qualitative), Part III (Quantitative) |
| `analyze-fundamentals` | `src/stockiv/knowledge/industry_guides.md` | Industry classification criteria |
| `analyze-fundamentals` | `src/stockiv/knowledge/financial_reading_guide.md` | Ratio interpretation |
| `analyze-valuation` | `src/stockiv/knowledge/framework.md` | Part IV (Market phase), Part V (Target price) |
| `analyze-valuation` | `src/stockiv/knowledge/criteria.md` | Graham checklist, valuation method by Lynch type |
| `analyze-sentiment` | `src/stockiv/knowledge/evidence_standard.md` | Citation rules |
| `collect-data` | `src/stockiv/knowledge/data_reading_guide.md` | Data interpretation |
| ALL skills | `src/stockiv/knowledge/framework.md` | Part I (Investing vs. Trading — master directive) |
```

### Pros
- Zero regression risk — no SKILL.md content changed
- Ships in 3–5 days (mostly file moves + one new AGENTS.md + two new files)
- Creates the clean foundation Sprint 2 builds on
- Explicit rollback: keep `.agents/skills/` as archive for one sprint
- Validates the plugin structure with actual skills before adding new ones

### Cons
- No analyst-visible improvement — no new flows, no new commands
- deepdive-flow is still sequential (4 wait cycles)
- Monolithic flow structure unchanged
- Still no screener, compare, or watchlist

### Effort
**S–M · 3–5 days · Zero SKILL.md content risk**

---

## Concept B — Full Restructure

**One-line:** Plugin packaging + atomic/flow separation + subagent parallelism + compare-flow in Sprint 1.

### What Changes

Everything in Concept A, plus: formalize the atomic vs. orchestrator split with directory structure, rewrite `deepdive-flow` and `weekly-flow` to explicitly delegate to atomic skills, restructure `analyze-fundamentals` to enable parallel execution, and ship `compare-flow` and formal `agent.json` definitions.

### Target Structure

```
.agents/
  plugins/
    stockiv-plugin/
      plugin.json
      skills/
        atomic/
          collect-data/SKILL.md
          analyze-sentiment/SKILL.md
          analyze-fundamentals/SKILL.md      ← REWRITTEN: split into quant phase + qual phase
          analyze-valuation/SKILL.md
          draft-report/SKILL.md
          publish-discord/SKILL.md
        flows/
          deepdive-flow/SKILL.md             ← REWRITTEN: delegates to atomic skills, parallelizes Step 2
          weekly-flow/SKILL.md               ← REWRITTEN: delegates to atomic skills
          compare-flow/SKILL.md              ← NEW: side-by-side GCCP comparison
        _template/SKILL.md
      agents/
        stock-analyst/agent.json
        gatekeeper-reviewer/agent.json
        market-scout/agent.json
        fundamentals-analyst/agent.json      ← NEW: dedicated quant analysis agent
        valuation-analyst/agent.json         ← NEW: dedicated valuation agent
      references/
        knowledge-map.md
```

### Key Rewrites

**`analyze-fundamentals` — split execution model:**
```
Phase A (quant — no sentiment dependency):
  - Input: financial_summary.md only
  - Output: partial_fundamentals_quant.md
  - Runs: ROE/ROA/margins, cash generation, forensic checks (Part III)
  
Phase B (qual — sentiment required):
  - Input: partial_fundamentals_quant.md + {TICKER}_sentiment.md
  - Output: {TICKER}_fundamentals.md (complete)
  - Runs: Lynch category, industry classification, tailwinds/headwinds (Part II)
```

**`deepdive-flow` — parallel Step 2:**
```
Step 1: collect-data (sequential, gating)
Step 2A: analyze-sentiment [ticker mode]   ← parallel
Step 2B: analyze-fundamentals [Phase A]    ← parallel (if macro cached)
          ↓ join ↓
Step 3: analyze-fundamentals [Phase B]     ← qual, needs both 2A + 2B
Step 4: analyze-valuation
Step 5: gatekeeper review
Step 6: draft-report
Step 7: publish-discord
```

**`compare-flow` — new:**
```
Input: TICKER1, TICKER2
Step 1: collect-data for TICKER1, collect-data for TICKER2 (parallel)
Step 2: deepdive pipeline for each ticker (sequential per ticker)
Step 3: gatekeeper reviews both reports
Step 4: compile comparison table (side-by-side verdicts, ratios, targets)
Step 5: publish-discord (single comparison post)
Output: reports/compare/{TICKER1}_vs_{TICKER2}_comparison.md
```

### Pros
- Analyst gets `compare-flow` immediately — visible win
- Parallelism reduces deepdive wall-clock time by one sequential step
- Clean atomic/flow separation makes Sprint 3+ flows trivial to add
- Formal `agent.json` definitions enforce agent scope boundaries

### Cons
- Significant SKILL.md content risk: `analyze-fundamentals` rewrite is the riskiest change in the codebase — it's the most complex atomic skill (160+ lines), referenced by valuation and draft-report
- `compare-flow` format decisions (one PDF vs two, gatekeeper once vs twice) need design upfront
- Two-sprint worth of work compressed into one — high delivery risk
- If `analyze-fundamentals` rewrite introduces bugs, they're invisible until a full deepdive run (end-to-end, Step 3)

### Effort
**L · 2–3 weeks · High SKILL.md content risk**

---

## Concept C — Knowledge-First Plugin ("The Living Framework")

**One-line:** Before restructuring flows, bring the GCCP framework itself into the plugin as a versioned, navigable first-class artifact — then let structure follow.

### What Changes

Concept C is not primarily about plugin packaging or flow parallelism. Its thesis: the root pain isn't flat vs. nested structure — it's that `src/stockiv/knowledge/framework.md` is the intellectual backbone of the entire system but is invisible to the plugin layer. Skills reference it by path, not by meaning. A new skill author has to read a 500-line framework document to find the 40 lines relevant to their skill. The fix: bring the framework into the plugin's `references/` as a navigable, section-addressable document, then build a **skill registry** (`skill-routing.md`) that is the authoritative source for both AGENTS.md routing and developer skill authorship.

### Target Structure

```
.agents/
  plugins/
    stockiv-plugin/
      plugin.json
      references/
        framework/
          part-i-foundation.md              ← extracted from framework.md
          part-ii-qualitative.md            ← extracted (used by: analyze-fundamentals)
          part-iii-quantitative.md          ← extracted (used by: analyze-fundamentals)
          part-iv-market-phase.md           ← extracted (used by: analyze-valuation)
          part-v-target-price.md            ← extracted (used by: analyze-valuation)
        industry_guides.md                  ← symlink or copy from src/stockiv/knowledge/
        criteria.md                         ← symlink or copy from src/stockiv/knowledge/
        evidence_standard.md               ← symlink or copy from src/stockiv/knowledge/
        skill-routing.md                    ← NEW: authoritative skill registry
      skills/
        [same as Concept A — no atomic/flow split yet]
      agents/
        [same as Concept A]
```

### The Skill Registry (`references/skill-routing.md`)

This is the key innovation of Concept C. A single machine-readable (and human-readable) registry of all skills:

```markdown
# Skill Registry — stockiv-plugin

## Registered Skills

### collect-data
- **Trigger:** `/collect <TICKER>`, `/collect --macro`
- **Type:** atomic
- **Inputs:** (none — generates data from CLI)
- **Outputs:** `data/raw/context/{TICKER}_ticker_context.md`, `data/processed/synthesizer/{TICKER}/financial_summary.md`
- **Knowledge refs:** `framework/part-i-foundation.md`
- **Required before:** analyze-sentiment, analyze-fundamentals, analyze-valuation

### analyze-sentiment
- **Trigger:** `/sentiment [TICKER]`
- **Type:** atomic
- **Inputs:** `data/raw/context/{TICKER}_ticker_context.md`, `data/raw/context/market_context.md`
- **Outputs:** `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`, `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`
- **Knowledge refs:** `framework/part-ii-qualitative.md`, `evidence_standard.md`
- **Required before:** analyze-fundamentals

### [... all 8 skills ...]

## Planned Skills (Sprint 2+)

### compare-flow [planned]
- **Trigger:** `/compare TICKER1 TICKER2`
- **Type:** flow
- **Inputs:** 2× financial_summary.md, 2× fundamentals.md, 2× valuation.md
- **Outputs:** `reports/compare/{TICKER1}_vs_{TICKER2}_comparison.md`
- **Design notes:** gatekeeper runs independently per ticker; single comparison PDF output
```

### How AGENTS.md Becomes a Thin Pointer

AGENTS.md stops duplicating trigger logic. It becomes:

```markdown
## Harness: stockiv-plugin

**Route all requests via skill registry:**  
See `.agents/plugins/stockiv-plugin/references/skill-routing.md` for full trigger patterns and skill routing.

**Summary triggers:**
| Pattern | Skill |
|---|---|
| `/weekly` | weekly-flow |
| `/deepdive` | deepdive-flow |
| (see skill-routing.md for all others) |  |
```

### Why This Is Distinct

Concept A migrates the structure. Concept B rewrites the logic. Concept C changes the **authorship model**: instead of each skill being an isolated document that happens to reference framework.md, skills become entries in a registry that expresses their relationships. The framework is split into navigable parts so skills reference `part-iii-quantitative.md` not a blob. Planned skills appear in the registry before their SKILL.md is written — the registry is the sprint plan.

### Pros
- Solves the actual daily developer pain: "where do I start?" has one answer — `skill-routing.md`
- Framework splitting makes each part shorter and more focused; `analyze-fundamentals` no longer needs to say "Read Part II and Part III" — it just imports `part-ii-qualitative.md`
- Sprint 2 flows appear in the registry immediately as `[planned]` — the roadmap is the registry
- AGENTS.md becomes stable; it only changes when the registry changes

### Cons
- **Splitting `framework.md` is risky.** The file header says *"MASTER DIRECTIVE — All Crews MUST strictly adhere."* It may be intentionally monolithic. Splitting it creates potential for drift — Part IV references Part II concepts; splitting them may break cross-references.
- More files = more maintenance surface
- `skill-routing.md` becomes a critical single point of failure — if it's wrong, agents route incorrectly
- The benefit over Concept A + a good README is debatable for a small team

### Effort
**M–L · 1–2 weeks · Medium risk (framework splitting is non-trivial)**

---

## Concept Comparison Matrix

| Dimension | Concept A | Concept B | Concept C |
|---|---|---|---|
| Sprint 1 deliverable | Plugin packaging | Plugin + parallelism + compare-flow | Plugin + framework split + skill registry |
| SKILL.md content changes | None | 3 rewrites (fundamentals, deepdive-flow, weekly-flow) | None to skill SKILL.md; framework.md is split |
| New skills in Sprint 1 | None | compare-flow | None (planned registry entry only) |
| Analyst-visible change | None | compare-flow | None |
| Migration risk | Low | High (fundamentals rewrite) | Medium (framework split) |
| Extends cleanly to Sprint 2 | Yes — add flows in skills/ | Yes — add flows in skills/flows/ | Yes — add entries to skill registry |
| Unique strength | Zero regression | Feature velocity | Developer experience |
| Unique weakness | No analyst win in Sprint 1 | Too much in one sprint | Framework split risk; over-engineering for team size |

---

*Phase 4 team vote in `04-team-vote.md`.*
