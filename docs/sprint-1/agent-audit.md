# Sprint 1 — Agent Location Audit (I3)

> **Purpose:** Confirm exact paths of all agent definition files before migration into plugin structure.
> **Date:** 2026-06-21 | **Branch:** `feat/plugin-migration`

---

## Findings

### Agent Files — Current Locations

| Agent | Current Path | File Format | Exists? |
|---|---|---|---|
| Gatekeeper Reviewer | `.github/agents/gatekeeper-reviewer.agent.md` | YAML frontmatter + Markdown | ✅ Yes |
| Stock Analyst | `.github/agents/stock-analyst.agent.md` | YAML frontmatter + Markdown | ✅ Yes |
| Market Scout | `.github/agents/market-scout.agent.md` | YAML frontmatter + Markdown | ✅ Yes |

### `.agents/agents/` Directory

**Does NOT exist.** Agent files are exclusively in `.github/agents/`.

### Other Locations Checked

| Path | Status |
|---|---|
| `.agents/agents/` | ❌ Does not exist |
| `.github/agents/` | ✅ Contains all 3 agent files |
| Root directory | No agent files |

---

## Agent File Format (YAML Frontmatter + Markdown)

Each agent uses the same format:
```yaml
---
name: <Agent Name>
description: <one-line description>
tools: [...]
model: [...]       # model array (some agents use 'agents' field too)
---

# <Agent Name> Agent

<Full instruction body in Markdown>
```

---

## Cross-References in SKILL.md Files

Two skills reference agent paths using relative-style comments (informational only — not actual import paths):

| Skill | Reference | Current Path Mentioned |
|---|---|---|
| `weekly-flow` | Agent path comment | `../.github/agents/stock-analyst.agents.md` |
| `weekly-flow` | Subagent mention | `../.github/agents/market-scout.agents.md` |
| `deepdive-flow` | Agent roles section | References agents by name (not file path) |

> **Note:** These are documentation references only — not import paths. The `.agents.md` extension used in `weekly-flow` appears to be a typo (should be `.agent.md`). Flagged as Sprint 2 review item — do NOT edit SKILL.md content in Sprint 1.

---

## Target Plugin Paths

| Agent | Target Path in Plugin | Migration Action |
|---|---|---|
| Gatekeeper Reviewer | `.agents/plugins/stockiv-plugin/agents/gatekeeper-reviewer.agent.md` | Copy (original stays in `.github/agents/`) |
| Stock Analyst | `.agents/plugins/stockiv-plugin/agents/stock-analyst.agent.md` | Copy (original stays in `.github/agents/`) |
| Market Scout | `.agents/plugins/stockiv-plugin/agents/market-scout.agent.md` | Copy (original stays in `.github/agents/`) |

---

## Key Finding ✅

**All 3 agent files confirmed in `.github/agents/`. No agents in `.agents/agents/` (directory does not exist).  
Migration strategy: COPY only — originals must remain in `.github/agents/` for GitHub Copilot harness compatibility.**
