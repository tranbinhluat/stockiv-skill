# Claude Code Support — Implementation Plan

Goal: make this repo work in **Claude Code** in addition to **OpenCode**. Append only — the OpenCode setup stays untouched and remains the source of truth for skills. Core (Python CLI tools, skills content, agent prompts) stays identical across both harnesses; only the harness wiring (frontmatter, folder layout, settings) differs.

Spec: user decisions (2026-11-26), recorded here as binding:
- Skills: `.claude/skills` is a **symlink** to `../.opencode/skills` (single source of truth).
- Packaging: **project-level `.claude/` dir** (no plugin / marketplace).
- Primary agent: `.claude/settings.json` sets `"agent": "stock-analyst"` so the main Claude Code session runs as the analyst (Claude Code's equivalent of OpenCode `mode: primary`).
- Models: stock-analyst = `sonnet`, market-scout = `sonnet`, gatekeeper-reviewer = `opus`, annual-report-scanner = `haiku`.

## Global Constraints

1. **Do not modify** anything under `.opencode/`, nor `opencode.json`, `tools/`, `src/`, `scripts/`, `data/`, `pyproject.toml`, `uv.lock`.
2. Python is always run via `uv run` (e.g. `uv run pytest tests/test_claude_parity.py -v`). Never pip/venv.
3. Claude agent/command **body** (everything after the closing frontmatter `---` line) must be **byte-identical** to the matching OpenCode file's body. Only frontmatter differs.
4. Frontmatter split rule: a file's frontmatter is between the 1st and 2nd lines that are exactly `---`; body is everything after the 2nd such line. Later `---` lines (e.g. markdown horizontal rules in `gatekeeper-reviewer.md`) belong to the body. OpenCode frontmatter is **not valid YAML** (`websearch: *` in market-scout) — never YAML-parse OpenCode files.
5. `description` values in Claude files are copied verbatim from the matching OpenCode file.
6. One commit per task, conventional-commit style matching repo history (`feat: ...`, `docs: ...`, `test: ...`).
7. Files end with a single trailing newline, no trailing whitespace (pre-commit hooks `end-of-file-fixer`, `trailing-whitespace`, `check-json`).

## File Structure (end state)

```
CLAUDE.md                         # new — imports AGENTS.md for Claude Code
.claude/
├── settings.json                 # new — default agent + permissions (mirrors opencode.json)
├── skills -> ../.opencode/skills # new — symlink
├── agents/                       # new — 4 files, Claude frontmatter + OpenCode body
│   ├── stock-analyst.md
│   ├── market-scout.md
│   ├── gatekeeper-reviewer.md
│   └── annual-report-scanner.md
└── commands/                     # new — 10 files, Claude frontmatter + OpenCode body
    ├── collect.md compare.md deepdive.md fundamentals.md publish.md
    └── report.md sentiment.md shortlist.md valuation.md weekly.md
tests/test_claude_parity.py       # new — drift guard between .opencode and .claude
AGENTS.md                         # edit — one appended layout line
.gitignore                        # edit — ignore .claude/settings.local.json
README.md                         # edit — Claude Code usage section
```

---

## Task 1: Parity test (drift guard)

**File:** create `tests/test_claude_parity.py` (pytest, stdlib only — no PyYAML).

Write the test first; it is expected to FAIL now (`.claude/` does not exist yet) and pass after Tasks 2–4. Repo root = `Path(__file__).resolve().parent.parent`.

Helpers (module-level, small):
- `split_frontmatter(path) -> tuple[str, str]`: per Global Constraint 4, return `(frontmatter_text, body_text)`. Read with `encoding="utf-8"`.
- `field(frontmatter_text, key) -> str | None`: return value of the first line matching `^{key}:\s*(.*)$` (stripped), else `None`. Plain regex, no YAML.

Tests (use `pytest.mark.parametrize` over the OpenCode files so each file shows as its own case; ids = file stem):
1. `test_agent_parity[stem]` — for every `.opencode/agent/*.md`:
   - `.claude/agents/{stem}.md` exists
   - Claude body == OpenCode body (exact string equality)
   - Claude `name` == `stem`
   - Claude `description` == OpenCode `description`
   - Claude `model` is in `{"sonnet", "opus", "haiku"}`
2. `test_agent_models` — exact mapping: `{"stock-analyst": "sonnet", "market-scout": "sonnet", "gatekeeper-reviewer": "opus", "annual-report-scanner": "haiku"}`.
3. `test_scanner_is_read_only` — `.claude/agents/annual-report-scanner.md` has `tools` field equal to `Read, Grep, Glob`.
4. `test_command_parity[stem]` — for every `.opencode/command/*.md`:
   - `.claude/commands/{stem}.md` exists
   - Claude body == OpenCode body
   - Claude `description` == OpenCode `description`
   - Claude `argument-hint` field is present (not `None`)
5. `test_no_extra_claude_files` — set of stems in `.claude/agents` == set in `.opencode/agent`; same for `.claude/commands` vs `.opencode/command`.
6. `test_skills_symlink` — `.claude/skills` is a symlink, `os.readlink` == `../.opencode/skills`, and `.claude/skills/deepdive-flow/SKILL.md` is a readable file.
7. `test_settings_default_agent` — `json.loads(.claude/settings.json)["agent"] == "stock-analyst"` and `.claude/agents/stock-analyst.md` exists.
8. `test_claude_md_imports_agents_md` — `CLAUDE.md` exists and contains a line exactly `@AGENTS.md`.

Verify: `uv run pytest tests/test_claude_parity.py -v` → all tests FAIL or ERROR because `.claude/` is missing (expected RED). Record the output in the report. The suite must not fail with a collection/import error — parametrize ids must collect (they come from `.opencode/`, which exists).

Commit: `test: add opencode/claude-code parity guard`

---

## Task 2: Scaffolding — symlink, settings, CLAUDE.md, AGENTS.md, .gitignore

1. Symlink: from repo root, `ln -s ../.opencode/skills .claude/skills` (create `.claude/` first). Relative target exactly `../.opencode/skills`.
2. Create `.claude/settings.json` with exactly this content:
   ```json
   {
     "$schema": "https://json.schemastore.org/claude-code-settings.json",
     "agent": "stock-analyst",
     "permissions": {
       "allow": [
         "Bash",
         "Read",
         "WebSearch",
         "WebFetch"
       ],
       "deny": [
         "Bash(rm *)",
         "Read(./.env)",
         "Read(./**/.env)"
       ]
     }
   }
   ```
   (Mirrors `opencode.json`: bash allowed except `rm`, `.env` unreadable. `.env.example` stays readable.)
3. Create `CLAUDE.md` with exactly:
   ```markdown
   # CLAUDE.md

   @AGENTS.md

   ## Claude Code layout

   Claude Code reads the same skills as OpenCode via the `.claude/skills` symlink to `.opencode/skills`. Agents live in `.claude/agents/`, slash commands in `.claude/commands/`, and `.claude/settings.json` makes `stock-analyst` the default main agent. Agent and command bodies must stay identical to their `.opencode/` counterparts — `tests/test_claude_parity.py` enforces this. Edit skills only in `.opencode/skills/`.
   ```
4. `AGENTS.md`: directly after the existing line starting `**OpenCode layout:**`, insert one blank line and then this line:
   `**Claude Code layout:** agents in `.claude/agents/`, slash commands in `.claude/commands/`, skills via `.claude/skills` → `.opencode/skills` symlink, default agent set in `.claude/settings.json`. Bodies mirror `.opencode/` (enforced by `tests/test_claude_parity.py`).`
   Change nothing else in AGENTS.md.
5. `.gitignore`: append a line `.claude/settings.local.json` (after a blank line, with a `# Claude Code local settings` comment line above it).

Verify: `uv run pytest tests/test_claude_parity.py -v` → `test_skills_symlink`, `test_claude_md_imports_agents_md` PASS; `test_settings_default_agent` still FAILS (agent file comes in Task 3) — that is expected. `git ls-files -s .claude/skills` shows mode `120000`. `uv run python -c "import json;json.load(open('.claude/settings.json'))"` succeeds.

Commit: `feat: add claude code scaffolding (settings, CLAUDE.md, skills symlink)`

---

## Task 3: Claude Code agents

Create 4 files in `.claude/agents/`. For each: new frontmatter (below), then the **exact body** of the matching `.opencode/agent/{name}.md` (Global Constraint 3). Generate bodies mechanically (e.g. a shell/awk/python one-off that copies everything after the 2nd `---` line) — do not retype them. Do not commit any helper script.

Frontmatter key order: `name`, `description`, `model`, then `tools` if present. `description` copied verbatim from the OpenCode file. Drop all OpenCode-only keys (`mode`, `hidden`, `user-invocable`, `variant`, `reasoningEffort`, `websearch`, `webfetch`, `agents`, `permission`).

| file | model | tools |
|---|---|---|
| `stock-analyst.md` | `sonnet` | (omit — inherits all, needs Agent tool to call subagents) |
| `market-scout.md` | `sonnet` | (omit — inherits all incl. WebSearch/WebFetch/Bash) |
| `gatekeeper-reviewer.md` | `opus` | (omit) |
| `annual-report-scanner.md` | `haiku` | `Read, Grep, Glob` (mirrors OpenCode read/grep allow, edit/bash deny) |

Example (annual-report-scanner):
```
---
name: annual-report-scanner
description: Read-only forensic scanner for Vietnamese company annual report markdown.
model: haiku
tools: Read, Grep, Glob
---
<exact OpenCode body>
```

Verify: `uv run pytest tests/test_claude_parity.py -v` → all agent tests, `test_agent_models`, `test_scanner_is_read_only`, `test_settings_default_agent` PASS; agent half of `test_no_extra_claude_files` satisfied (command half still fails until Task 4 — expected). Also `diff <(awk 'c>=2;/^---$/{c++}' .opencode/agent/X.md) <(awk 'c>=2;/^---$/{c++}' .claude/agents/X.md)` is empty for all four (sanity).

Commit: `feat: add claude code agents mirroring opencode agents`

---

## Task 4: Claude Code slash commands

Create 10 files in `.claude/commands/`, one per `.opencode/command/*.md`, same filename. Frontmatter: `description` (verbatim from OpenCode), then `argument-hint` from the table. Body = exact OpenCode body (copy mechanically). Drop the OpenCode `agent:` key — the default agent from `.claude/settings.json` already makes the main session `stock-analyst`.

| file | argument-hint |
|---|---|
| `collect.md` | `<TICKER> \| --macro` |
| `compare.md` | `<TICKER1> <TICKER2>` |
| `deepdive.md` | `<TICKER>` |
| `fundamentals.md` | `<TICKER>` |
| `publish.md` | `[TICKER]` |
| `report.md` | `[TICKER]` |
| `sentiment.md` | `[TICKER]` |
| `shortlist.md` | `[--force]` |
| `valuation.md` | `<TICKER>` |
| `weekly.md` | `[no review]` |

(The `\|` above is markdown table escaping; the file value is `<TICKER> | --macro`. Quote values in frontmatter with double quotes, e.g. `argument-hint: "<TICKER> | --macro"`, so `<`, `[`, `|` are YAML-safe.)

Verify: `uv run pytest tests/test_claude_parity.py -v` → **all** tests PASS. Then full suite `uv run pytest tests/ -v` — report results (pre-existing failures unrelated to this work: note them, don't fix).

Commit: `feat: add claude code slash commands mirroring opencode commands`

---

## Task 5: README — Claude Code usage

Edit `README.md` only. Append-style changes; do not remove or reword OpenCode content.

1. In the intro paragraph (line starting `Interact via **opencode**`), change it to say it runs on **opencode** or **Claude Code** — minimal word change.
2. In **Quick Start**, after the existing step `# 3. Open opencode and run` block, add a sibling note: in Claude Code, run `claude` in the repo root; `stock-analyst` is the default agent (from `.claude/settings.json`) and the same slash commands work (`/deepdive FPT`, `/weekly`).
3. In **Architecture**, after the `.opencode/` tree block, add a short `.claude/` tree (settings.json, skills symlink, agents/, commands/) plus one sentence: bodies mirror `.opencode/`, skills are shared via symlink, parity enforced by `tests/test_claude_parity.py`. Include the Claude model mapping (stock-analyst/market-scout = sonnet, gatekeeper-reviewer = opus, annual-report-scanner = haiku).
4. In **Project Structure** tree, add `CLAUDE.md` and `.claude/` entries next to `.opencode/`.

Keep additions concise (≈25 lines total). No other README changes.

Verify: `git diff --stat` touches only README.md; rendered markdown fences balanced (`grep -c '^```' README.md` is even).

Commit: `docs: document claude code support in README`
