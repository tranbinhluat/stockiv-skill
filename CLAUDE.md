# CLAUDE.md

@AGENTS.md

## Claude Code layout

Claude Code reads the same skills as OpenCode via the `.claude/skills` symlink to `.opencode/skills`. Agents live in `.claude/agents/`, slash commands in `.claude/commands/`, and `.claude/settings.json` makes `stock-analyst` the default main agent. Agent and command bodies must stay identical to their `.opencode/` counterparts — `tests/test_claude_parity.py` enforces this. Edit skills only in `.opencode/skills/`.
