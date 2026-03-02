# CLAUDE.md - Working on This CrewAI Project

This file tells Claude (me) how to help with this CrewAI project.

## Project Overview

**CrewAI Project** - An AI agent orchestration framework using CrewAI to create research and writing agents.

### Tech Stack
* **Language:** Python 3.12+
* **Framework:** CrewAI 1.9.3
* **Package Manager:** uv (NOT pip, NOT poetry)
* **Git:** Pre-commit hooks with secret detection
* **IDE:** VSCode

## Commands I Should Use

```bash
# Install dependencies
uv sync

# Run the main crew
uv run crewai-run

# Run as module
uv run python -m crewai_project

# Add dependencies
uv add <package>
uv add --dev <package>  # for dev dependencies

# Run pre-commit hooks manually
uv run pre-commit run --all-files

# Install/update pre-commit hooks
uv run pre-commit install
uv run pre-commit install-hooks
```

## Project Structure

```
crewai-project/
├── src/
│   └── crewai_project/
│       └── __init__.py     # Main entry point with agents
├── tools/                   # Custom CrewAI tools
├── .env.example            # API key template
├── .pre-commit-config.yaml # Pre-commit hooks (secret detection)
├── pyproject.toml          # Dependencies (hatchling build)
└── uv.lock                 # Locked dependencies
```

## How I Should Help

### Adding Features
1. Read existing code in `src/crewai_project/`
2. Follow existing patterns (Agent, Task, Crew structure)
3. Run `uv run pre-commit run --all-files` before committing

### Debugging
1. Check `.env` is configured (API keys)
2. Use `uv run` for all Python commands
3. Check `uv.lock` if dependencies seem wrong

### Git Workflow
* Pre-commit hooks automatically check for secrets
* If hooks fail, fix the issues and try again
* Commit messages should be descriptive but concise

### Security Rules
* NEVER commit `.env` file
* NEVER hardcode API keys
* detect-secrets will block commits with secrets
* Use `.env.example` for showing what keys are needed

## Things to Remember

* This project uses `uv` exclusively - no pip commands
* Pre-commit hooks protect against credential leaks
* The project is structured as a proper Python package under `src/`
* Main agents: Research Analyst + Tech Content Writer

## Environment Variables Required

```
OPENAI_API_KEY=sk-...       # Required for CrewAI
SERPER_API_KEY=...          # Optional - for web search
```

---

_Update this file as the project evolves._
