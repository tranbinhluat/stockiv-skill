# StockIV: Gemini CLI Context

@Slave/SOUL.md
@Slave/IDENTITY.md
@Slave/USER.md

## Project Overview
**StockIV** - Stock analysis using AI agent orchestration with CrewAI.

## Tech Stack
* **Language:** Python 3.12+
* **Framework:** CrewAI 1.9.3
* **LLM:** Google Gemini 2.5 Pro
* **Package Manager:** uv (NOT pip, NOT poetry)
* **Git:** Pre-commit hooks with secret detection

## Memory Management Strategy

1.  **Project Memory**: Refer to `Slave/MEMORY.md` for architectural patterns and project history.
2.  **Daily Logs**: Refer to `memory/YYYY-MM-DD.md` (today/yesterday) for recent task status.
3.  **Update Rule**: After completing ANY task (crew updates, features, fixes), update:
    *   `memory/$(date +%Y-%m-%d).md` with daily progress.
    *   `Slave/MEMORY.md` with significant lessons, decisions, or new patterns.
4.  **Global Memory**: Use `save_memory` for personal facts or preferences that apply across ALL projects.

## Project Structure
```
stock-agent/
├── src/
│   └── stockiv/
│       ├── agents/         # Shared LLM & Base Agent config
│       ├── crews/          # Specific crews (Collector, Analyst, etc.)
│       └── __init__.py     # Main entry point
├── tools/                   # Custom tools & testing scripts
├── logs/                    # Execution logs (JSONL format)
├── memory/                  # Daily context logs
└── Slave/                   # AI Identity and long-term memory
```

## Commands Reference

```bash
# Install dependencies
uv sync

# Run the main crew
uv run stockiv-run

# Run as module
uv run python -m stockiv

# Add dependencies
uv add <package>
uv add --dev <package>

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

## Workflow Constraints
- **UV Exclusive**: Never use `pip` or `poetry`.
- **Security**: Pre-commit hooks automatically check for secrets. Never commit `.env`.
- **Commit Protocol**: Regularly commit work after every new feature, change, or fix.
- **Commit Format**: Descriptive title + body with `By: luattb`.
- **Testing**: Run `uv run pre-commit run --all-files` before committing.
