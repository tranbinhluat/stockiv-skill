# MEMORY.md - Long-Term Memory

**Security:** ONLY load in main session (direct chat with Luat). DO NOT share in group chats or shared contexts.

---

## About Luat Tran & Project Config

**Tech Stack & Preferences:**
- Uses **uv** for package management (never pip/poetry)
- Python 3.12+, WSL2 on Linux
- Values security (pre-commit hooks, secret detection)
- Prefers concise communication over pleasantries
- Likes clean git history with meaningful commits

**Current Project: StockIV**
- Location: `~/Documents/projects/stock-agent`
- Framework: CrewAI 1.9.3 for AI agent orchestration
- LLM: Qwen models via DashScope (qwen3.5-plus, qwen3-coder-plus, qwen3-max, qwen2.5-vl-72b-instruct)
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

## Project Structure & Architecture

**6 StockIV Crews:**
- collector - Data gathering from APIs (vnstock, Brave Search, PDF reports)
- sentiment_analyst - Macro and ticker-specific sentiment analysis
- synthesizer - GCCP framework evaluation engine
- director - Quality control & anomaly detection
- reporter - Translation, PDF export, Discord publishing
- orchestrator - User request classification & routing

**Directory Roles:**
- `src/stockiv/crews/` - Location for individual crews.
- `tools/` strictly reserved for custom CrewAI `@tool` methods (e.g., `vnstock_tools.py`).
- `tests/` strictly reserved for validation scripts (e.g., `test_collector.py`). Tests should implement and demonstrate CrewAI `Flow` constructs.
- `scripts/` strictly reserved for developer utilities (e.g., `view_logs.py`).
- `logs/` directory stores execution logs in JSONL format.
- `src/stockiv/knowledge/` contains markdown files summarizing our strategies (framework, criteria, market context, evidence standard).

**Crew Architecture Pattern:**
```python
# Each crew follows this structure:
src/stockiv/crews/<crew_name>/
├── <crew_name>.py        # @CrewBase class
├── README.md             # Visual doc with Mermaid diagrams of data flow
├── config/
│   ├── agents.yaml       # role/goal/backstory
│   └── tasks.yaml        # description/expected_output

# Usage:
from stockiv.crews import CollectorCrew
crew = CollectorCrew()
result = crew.crew().kickoff(inputs={"key": "value"})

# Critical Rule: All Crews MUST explicitly enable `tracing=True`
# in the @crew initialization so the user knows what's happening.
```

## Security & Workflow

**Security Measures:**
- `.env` is gitignored (API keys stay local).
- `detect-secrets` scans for leaked credentials before commits.
- Private key detection blocks SSH/PEM keys.
- Large file check (>1MB) prevents accidental commits.

**Git Workflow:**
- **CRITICAL:** Always try testing your new features and code changes before committing them.
- **CRITICAL:** Always create a new branch before developing a new feature. This isolates the work and makes rollbacks easy.
- Commit format: descriptive title + body with `By: luattb`.
- Run `uv run pre-commit run --all-files` to check ruff linting and formatting before committing.

**Code Style:**
- ruff for linting, ruff-format for formatting.

---

## Patterns to Follow

### LLM Quirks & Workarounds
- **Qwen / Anthropic Tool Calling Bug**: Using `output_pydantic` forces `tool_choice="required"` in Anthropic API calls. Reasoning models (like `qwen-max` or `qwen3.5-plus`) will reject this or output a raw `ToolUseBlock` which crashes the system.
  - *Workaround:* Remove `output_pydantic` from the Task. Let the LLM output raw JSON text, and use `json.loads()` + manual Pydantic validation inside your Python code.
- **Missing Tool Call Execution**: Qwen skips tool calls entirely when `output_pydantic` is set, going straight to the final answer hallucinated from its pre-training.
  - *Fix:* Pre-read files in flow code and inject content via variable interpolation in task prompts. Keep `FileReadTool` on agent for additional reads.
- **FileReadTool None Bug**: The schema has `start_line`/`line_count` as `int|None`. Qwen serializes `None` as a string `"None"`, breaking validation. For custom tools, use `@tool` with ONLY string parameters. Explicitly forbid language models from passing empty strings to `start_line` / `line_count`.

### CrewAI Flow Architecture
- **Class Structure:** Create `MyCrewFlow(Flow[MyState])` to orchestrate multi-crew interactions securely. Use `@start()` and `@listen(task_name)` decorators.
- **Strongly Typed Inputs**: Instead of passing untyped dictionaries, explicitly define a Pydantic `BaseModel` for the required inputs. E.g., add `def run(self, inputs: MyCrewInputs)` returning `self.crew().kickoff(inputs=inputs.model_dump())`.
- **Dynamic Output Path Injection:** Pass `self.state.shared_data["my_path"]` down to Crew initialization `kickoff(inputs=self.state.shared_data)`. In `tasks.yaml`, use double quotes around variables to interpolate strings instead of crashing the PyYAML parser: `output_file: "{my_path}"`.
- **Feedback Loop**: `crew.replay()` is functionally broken since UUIDs regenerate. Instead, use a dual crew pattern: `crew()` for first pass, `revision_crew()` for feedback, communicating via file-based context injection state.
- **Structured Outputs**: Use `output_pydantic` for decision tasks (Director), use `output_file` for final deliverables (Reporter). *Key constraint:* Each task can only use ONE output format.
- **Shared LLM:** Create `src/stockiv/agents/base.py` and centralize the `primary_llm` instance to avoid repetition.
- **Orchestrator LLM in Flow Routing:** Replace simple regex routing with an LLM prompt that enforces JSON output syntax for robust dynamic routing. Automatically provide a regex fallback just in case.

### Data Validation & Pipeline
- **EAV format confusion**: Tools outputting one row per metric confuses LLMs. Use PIVOT TABLE format (columns=periods, rows=items) in `FetchRecentFinancialsTool`.
- **Token Truncation via Huge Mapping Tables**: Dumping raw data spanning 4+ years and 4+ quarters across multiple separated tables (Income/Balance/Cashflow × Yearly/Quarterly) creates payloads too massive for standard LLM completion windows (resulting in mid-markdown hard truncation). **Fix:** Merge periods into shared composite columns (e.g., `2025 | 2024 | ... | 2025-Q4 | 2025-Q3`) to dramatically reduce Markdown syntax overhead and tokens.
- **LLM Hallucinations on prices**: LLMs hallucinate current prices. `FetchCurrentMarketSnapshotTool` returns definitive values. Task prompt must explicitly state: "copy verbatim, do NOT approximate".
- **Director validation process**: Director MUST receive `financial_summary.md` as ground truth (STEP 0.5) to cross-check.
- **Case Sensitivity**: CrewAI coworker delegation is case-sensitive: use exact lowercase role names e.g. "data specialist".

### Memory & Orchestration
- **CrewAI Memory**: Crews needing long-term memory should initialize with `memory=True` and configure a local embedder (e.g., `model_name: "all-MiniLM-L6-v2"`) so inference happens locally, bypassing HuggingFace rate limits.
- **n8n Webhook Architecture**: StockIV prefers decoupled architecture for scheduled execution triggers. Tasks are exposed via FastAPI wrappers (`api.py`) so external tools like n8n can issue POST requests (e.g. `POST /api/sentiment/market/weekly`).

### Tools & API Usage
- **Cache checks**: Before making external requests, execute a local SQLite `SELECT MAX()` cache check.
- **Data storage strategy**: Structured data (vnstock) is written to SQLite (`data/stockiv.db`). Unstructured data (Brave Search/News) is written to local JSON caches (`data/raw/cache/`).
- **Compound Keys for Time-Series**: Cache metrics like P/E and P/B on a `(ticker, date)` compound primary key, not just `(ticker, year_report)`.
- **API Specifics (vnstock)**: Must use `vnstock` 3.x. Requires `VNSTOCK_API_KEY` for 10-year financials from VCI/KBS providers. Market Indices lack `ratio_summary`. Macro APIs are fully unavailable on free tiers – rely on textual reports.

### Lessons Learned & Best Practices

1.  **AI Math Capabilities:** Explicitly state the math formula used inside the output of the ground-truth calculation tools (e.g. `Lynch PEG Ratio: 2.19 (Formula: P/E / (EPS CAGR + Dividend Yield))`). Otherwise, validator agents (like the Director) might attempt to retroactively verify the math using a *different* standard formula and falsely reject accurate numbers.
2.  **Tool Output Constraints vs AI Complaints:** If an API limits data (e.g., vnstock limits to ~4 years), ensure the downstream formatting tools don't artificially restrict it further (e.g., limiting to 3 years). Always display the maximum span of data available, and specifically state the time ranges used when calculating averages/CAGRs so the LLM doesn't complain about "missing" intermediate years.
3.  **Local LLMs & AI Usage Tokens:** When using a local LLM proxy (e.g., Anthropic provider format via litellm/vllm), CrewAI 1.9.3 might not receive or parse the `token_usage` headers correctly (especially if `parallel_tool_calls=False`), resulting in missing AI token statistics in the logs.
4. **Keep SQLite Queries Simple**: The `query_stock_database` tool should only do simple SELECTs, not complex aggregation to avoid SQLite version issues. Delegate math to Python.
5. **JSON Ratios Over EAV**: If you need multi-metric JSON (ROE, margin), query `ratio_summary` instead of hunting through EAV `financial_ratios`.

### Hierarchical Delegation & Agent Limits
- **Batching Questions**: Instruct 'manager' agents to ask multiple questions in a single `ask_question_to_coworker` message to save tokens.
- **Strict Subordinate Output**: Enforce strict text formats in subordinate agent's backstory (e.g., `Question | Status: MENTIONED/NOT_MENTIONED | Exact Quote | Summary`).
- **Hierarchical Tooling Bug**: When using `Process.hierarchical`, ANY task defined in `tasks.yaml` must NOT have a hardcoded `agent:`. If assigned, the Manager steals the tools from the worker and bypasses delegation.
- **ReAct Limits**: Put `max_iter` limit natively inside `agents.yaml` not inside `tasks.yaml`. `tasks.yaml` only supports `max_retries` for recovering from parsing failures.

### Path & Platform Integrations
- **Path Centralization**: All project paths are centralized in `src.stockiv.config.paths` using `pyrootutils.find_root()` and `pathlib.Path`.
- **Discord MCP**: Use `MCPServerStdio` with `command="npx"` and `args=["-y", "discord-mcp"]`. Token must be prefixed with `Bot `. Chunk markdown payloads larger than 1900 characters due to Discord limits.
- **Terminal Output Interception**: A global `TeeLogger` in `src/stockiv/utils/logger.py` overrides `sys.stdout` and `sys.stderr` to safely duplicate raw terminal strings to files in the `logs/` directory.

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

*Update this file with significant lessons, decisions, and context as the project evolves.*
\n### Recent Learnings (Synthesizer Agent)
- Instead of using the native CrewAI BaseTool `max_usage_count` limits which are internal/undocumented in older versions, it is safer to create a dedicated agent (e.g., `market_researcher`) to wrap external tools. This way we can explicitly prompt the agent to strictly limit the number of tool usages per delegation (e.g., 1 search per delegation) and per full review (e.g., max 5 searches).

### Separation of Forensic Concerns (Synthesizer Crew Updates - Mar 15)
- **The Problem**: Asking a semantic search agent (`forensic_accountant`) to do mathematical trend analysis (e.g. comparing inventory growth to COGS over multi-year periods) forces it to read unstructured text for structured data, resulting in failures.
- **Architectural Fix**: Created a dedicated `quantitative_risk_analyst` agent bound *only* to reading the pre-compiled `financial_summary_path` to hunt for numerical anomalies (Earnings Quality, Working Capital bloat). We stripped all math away from the `forensic_accountant` and restricted it entirely to narrative text search (Auditor Trust, Off-Balance-Sheet items) within the `annual_reports_dir`.
