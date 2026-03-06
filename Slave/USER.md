# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

* **Name:** Luat Tran
* **What to call them:** Luat
* **Pronouns:** he/him
* **Timezone:** US/Eastern (assume until told otherwise)
* **Location:** WSL2 on Linux

## Context

Luat is a software engineer working on AI agent orchestration using CrewAI. He's setting up a stock analysis project with:

* **Tech Stack:** Python 3.12, CrewAI, Gemini 3 Flash, uv (package manager), git
* **Current Project:** StockIV - Stock analysis with AI agents
* **Tools:** VSCode, WSL2, pre-commit hooks for security
* **Preferences:**
  * Uses uv for dependency management (not pip/poetry)
  * Values security (pre-commit hooks to prevent credential leaks)
  * Likes clean git history with meaningful commits
  * Prefers concise communication
  * Tests should use CrewAI `Flow` where possible to demonstrate how agents/crews are connected via flows

## Things to Remember

* Project uses `uv run` for executing commands
* Pre-commit hooks are installed - they'll catch secrets before commits
* `.env` file is gitignored - API keys stay local
* Main entry point: `uv run stockiv-run` or `python -m stockiv`

---

_The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference._
