# CLAUDE.md

@AGENTS.md

## Claude Code layout

Claude Code reads the same skills as OpenCode via the `.claude/skills` symlink to `.opencode/skills`. Agents live in `.claude/agents/`, slash commands in `.claude/commands/`, and `.claude/settings.json` makes `stock-analyst` the default main agent. Agent and command bodies must stay identical to their `.opencode/` counterparts — `tests/test_claude_parity.py` enforces this. Edit skills only in `.opencode/skills/`.

## Claude Code harness notes

Shared skills and agent bodies are written for OpenCode. When running in Claude Code:

- The OpenCode `task` tool is Claude Code's `Agent` tool. A reference to `.opencode/agent/<name>.md` means the `<name>` subagent (`.claude/agents/<name>.md`).
- Subagents cannot spawn subagents. Only the main thread (`stock-analyst`) may invoke `market-scout`, `annual-report-scanner`, and `gatekeeper-reviewer`.
- When a flow says to run a step as a (concurrent) subagent and that step itself needs `market-scout` or `annual-report-scanner` (e.g. `collect-data` and `analyze-fundamentals` inside `deepdive-flow` Step 2 or `compare-flow`), either run that step in the main thread, or first invoke the inner agent from the main thread and pass its output file path to the step's subagent. Never skip the inner agent or do its work inline in a generic subagent.
