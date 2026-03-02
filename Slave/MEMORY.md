# MEMORY.md - Long-Term Memory

**Security:** ONLY load in main session (direct chat with Luat). DO NOT share in group chats or shared contexts.

---

## About Luat Tran

**Tech Stack & Preferences:**
- Uses **uv** for package management (never pip/poetry)
- Python 3.12+, WSL2 on Linux
- Values security (pre-commit hooks, secret detection)
- Prefers concise communication over pleasantries
- Likes clean git history with meaningful commits

**Current Project: CrewAI**
- Location: `/home/luattranb/Documents/projects/crewai`
- Framework: CrewAI 1.9.3 for AI agent orchestration
- Structure: Proper Python package under `src/crewai_project/`
- Entry point: `uv run crewai-run` or `python -m crewai_project`

**Key Commands (use uv always):**
```bash
uv sync              # Install dependencies
uv add <pkg>         # Add dependency
uv run crewai-run    # Run the crew
uv run pre-commit run --all-files  # Run security hooks
```

---

## Project History

**2026-03-03 - Initial Setup**
- Created CrewAI project with uv, Python 3.12
- Set up pre-commit hooks with detect-secrets for credential leak protection
- Added research + writing agents as example
- Created OpenClaw-style memory system (IDENTITY, SOUL, USER, AGENTS, CLAUDE)

**Security Measures:**
- `.env` is gitignored (API keys stay local)
- detect-secrets scans for leaked credentials before commits
- Private key detection blocks SSH/PEM keys
- Large file check (>1MB) prevents accidental commits

---

## Patterns to Follow

**Adding New Agents/Crews:**
1. Read existing code in `src/crewai_project/`
2. Follow Agent → Task → Crew pattern
3. Use `uv run` for all Python commands
4. Run pre-commit before committing

**Git Workflow:**
- Pre-commit hooks automatically check for secrets
- If hooks fail, fix issues and try again
- Commit format: descriptive title + body with `By: Luat`

**Code Style:**
- ruff for linting, ruff-format for formatting
- Run `uv run pre-commit run --all-files` to check

---

## Things to Remember

- This is a learning/exploration project for CrewAI
- Main agents currently: Research Analyst + Tech Content Writer
- `tools/` directory exists for custom CrewAI tools

---

*Update this file with significant lessons, decisions, and context as the project evolves.*
