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

**Current Project: StockIV**
- Location: `/home/luattb/Documents/Work/stockew`
- Framework: CrewAI 1.9.3 for AI agent orchestration
- LLM: Gemini 2.5 Pro
- Structure: Proper Python package under `src/stockiv/`
- Entry point: `uv run stockiv-run` or `python -m stockiv`

**Key Commands (use uv always):**
```bash
uv sync              # Install dependencies
uv add <pkg>         # Add dependency
uv run stockiv-run   # Run the crew
uv run pre-commit run --all-files  # Run security hooks
```

---

## Project History

**2026-03-03 - Initial Setup**
- Created CrewAI project with uv, Python 3.12
- Set up pre-commit hooks with detect-secrets for credential leak protection
- Added research + writing agents as example
- Created OpenClaw-style memory system (IDENTITY, SOUL, USER, AGENTS, CLAUDE)
- Configured Gemini 2.5 Pro as the LLM
- Added event-based logging with LoggingCallback and ConsoleCallback

**Security Measures:**
- `.env` is gitignored (API keys stay local)
- detect-secrets scans for leaked credentials before commits
- Private key detection blocks SSH/PEM keys
- Large file check (>1MB) prevents accidental commits

---

## Patterns to Follow

**Crew Architecture Pattern (CrewAI @CrewBase):**
```python
# Each crew follows this structure:
src/stockiv/crews/<crew_name>/
├── <crew_name>.py        # @CrewBase class
├── config/
│   ├── agents.yaml       # role/goal/backstory
│   └── tasks.yaml        # description/expected_output

# Usage:
from stockiv.crews import CollectorCrew
crew = CollectorCrew()
result = crew.crew().kickoff(inputs={"key": "value"})
```

**7 StockIV Crews:**
- collector - Data gathering from sources
- quant_analyst - Quantitative analysis (metrics, ratios)
- sentiment_analyst - Market sentiment/mood analysis
- synthesizer - Combine multi-source analysis
- reporter - Generate comprehensive reports
- director - Validate analysis quality
- orchestrator - Coordinate workflow between crews

**Adding New Agents/Crews:**
1. Read existing code in `src/stockiv/crews/`
2. Follow @CrewBase pattern with YAML configs
3. Use `uv run` for all Python commands
4. Run pre-commit before committing

**Git Workflow:**
- Pre-commit hooks automatically check for secrets
- If hooks fail, fix issues and try again
- Commit format: descriptive title + body with `By: luattb`

**Code Style:**
- ruff for linting, ruff-format for formatting
- Run `uv run pre-commit run --all-files` to check

**OpenClaw to CrewAI Migration Pattern:**
- OpenClaw SOUL.md files contain agent/crew specifications
- Map SOUL concepts to CrewAI YAML format:
  - `role/goal/backstory` → `agents.yaml`
  - `task description/expected_output` → `tasks.yaml`
  - "Spawn subagent" → `crew.kickoff()` with inputs
  - Approve/Reject/MORE_INFO → `output_pydantic` with decision enum
- Workflow: Orchestrator coordinates, Director approves (independent quality gate)

**CrewAI Structured Output Pattern (2025):**
| Output Type | Use Case | Access Method |
|-------------|----------|---------------|
| `output_pydantic` | Type-safe structured data, task-to-task passing | `result.pydantic` |
| `output_json` | Structured data as dictionary | `result.json_dict` |
| `output_file` | Persistent storage for reports/audit | File system |
| `raw` (default) | Plain text | `result.raw` |

**Key constraint:** Each task can only use ONE output format.

**Recommended pattern:**
- Use `output_pydantic` for decision/data pipeline tasks (Director, Orchestrator)
- Use `output_file` for final deliverables (Reporter)
- Combine: Pydantic for parsing + `.to_markdown()` for human review
- Define models in `models.py` within crew directory
- Import and use in task: `output_pydantic=MyModel`

**Shared LLM Configuration Pattern:**
- Create `src/stockiv/agents/` package with `base.py`
- Centralize `gemini_llm` instance to avoid repetition
- All crews import: `from stockiv.agents import gemini_llm`
- Use `llm=gemini_llm` in Agent definitions

**Knowledge Base Pattern:**
```
src/stockiv/knowledge/
├── framework.md          # GCCP methodology (Good Company Cheap Price)
├── criteria.md           # Graham/Greenblatt/Lynch selection criteria
├── market_context.md     # VN-Index market states & data protocols
├── evidence_standard.md  # Evidence tiers & audit trail requirements
├── industry_guides.md    # Vietnam-specific industry analysis (8 industries)
└── base.py              # KnowledgeBase class (pending)
```

**Framework.md Structure (2026-03-03):**
```
PART I: GOOD COMPANY
├── A. QUALITATIVE (50%)
│   ├── Industry (with analysis steps → industry_guides.md)
│   ├── Business Model
│   └── Management Quality (4 pillars, MQS score)
└── B. QUANTITATIVE (50%)
    ├── Profitability (ROA, ROE, margins)
    ├── Financial Health (ratios)
    └── Growth
    ├── Simplified Rating System (threshold-based)
    └── Rating Algorithm (pseudo-code)

PART II: CHEAP PRICE
├── Market Cycle Awareness (P/E thresholds → market_context.md)
├── Valuation Metrics (P/B, P/E, P/E×P/B)
├── Valuation Methods (DCF, Relative, SOTP)
└── Margin of Safety

PART III: RANKING (Greenblatt Magic Formula)
PART IV: TIER COMPARISON RULES
PART V: CHECKLIST
PART VI: RELATED RESOURCES (links to all 5 files)
```

**Purpose:** Shared framework for Director (validation) and Synthesizer (analysis)

**Usage:**
- Director validates against framework/criteria/evidence standards
- Synthesizer applies framework/criteria for analysis
- Market context updated daily by Collector crew
- See `memory/knowledge_base_review.md` for detailed issues & action items
- Market cycle awareness: Check VN-Index P/E → adjust margin of safety


---

## Critical Rules

**ALWAYS Update Memory After Work:**
- When completing ANY task (crew updates, features, fixes):
  1. Update `memory/YYYY-MM-DD.md` with what was done
  2. Update `Slave/MEMORY.md` with patterns/lessons learned
  3. Add memory update to TODO list at START of task
- This is non-negotiable. User will remind you if you forget.
- Memory updates are part of "task complete" — not optional

---

## Things to Remember

- This is a learning/exploration project for CrewAI + stock analysis
- Main agents currently: Research Analyst + Tech Content Writer
- `tools/` directory exists for custom tools
- `logs/` directory stores execution logs in JSONL format
- `src/stockiv/knowledge/` contains 4 markdown files: framework, criteria, market_context, evidence_standard
- `memory/knowledge_base_review.md` contains detailed issues & action items for knowledge base

---

*Update this file with significant lessons, decisions, and context as the project evolves.*
