# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

* **Name:** Luat Tran
* **What to call them:** Luat
* **Pronouns:** he/him
* **Timezone:** US/Eastern (assume until told otherwise)
* **Location:** WSL2 on Linux

## Context

Luat is a software engineer working on AI agent orchestration using CrewAI. He's setting up a new project with:

* **Tech Stack:** Python 3.12, CrewAI, uv (package manager), git
* **Current Project:** CrewAI agent framework for research and writing tasks
* **Tools:** VSCode, WSL2, pre-commit hooks for security
* **Preferences:**
  * Uses uv for dependency management (not pip/poetry)
  * Values security (pre-commit hooks to prevent credential leaks)
  * Likes clean git history with meaningful commits
  * Prefers concise communication

## Things to Remember

* Project uses `uv run` for executing commands
* Pre-commit hooks are installed - they'll catch secrets before commits
* `.env` file is gitignored - API keys stay local
* Main entry point: `uv run crewai-run` or `python -m crewai_project`

---

*The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.*
