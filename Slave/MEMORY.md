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
- LLM: Gemini 3 Flash
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
- **CRITICAL:** Always try testing your new features and code changes before committing them.
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

**⚠️ KNOWN BUG (CrewAI + Qwen/Anthropic):**
- Using `output_pydantic` forces `tool_choice="required"` in the Anthropic API call.
- If you use a reasoning model (like `qwen-max` or `qwen3.5-plus`) in "thinking mode," it will reject the `tool_choice=required` parameter or abruptly crash by returning a raw `ToolUseBlock` array instead of a string.
- *Workaround:* Remove `output_pydantic` from the Task. Let the LLM output raw JSON text, and use `json.loads()` + manual Pydantic validation inside your python code.

**Recommended pattern:**
- Use `output_pydantic` for decision/data pipeline tasks (Director, Orchestrator)
- Use `output_file` for final deliverables (Reporter)
- Combine: Pydantic for parsing + `.to_markdown()` for human review
- Define models in `models.py` within crew directory
- Import and use in task: `output_pydantic=MyModel`

**CrewAI Flow Architecture Pattern (2026-03-07):**
- **Purpose**: To orchestrate single or multi-crew interactions securely and manage state consistently.
- **Class Structure:** Create `MyCrewFlow(Flow[MyState])` and manage internal inputs/outputs with `@start()` and `@listen(task_name)` decorators.
- **Pattern**:
  - Sub-task `@listen(init)` runs `crew.kickoff()`
  - Sub-task `@listen(crew_run)` extracts `result.pydantic` and physically saves markdown to disk.
- Exposes `await flow.kickoff_async(inputs={...})` to `api.py` callers.

**Shared LLM Configuration Pattern:**
- Create `src/stockiv/agents/` package with `base.py`
- Centralize `gemini_llm` or `primary_llm` instance to avoid repetition
- All crews import: `from stockiv.agents import primary_llm`
- Use `llm=primary_llm` in Agent definitions

**Data Storage Architecture (Collector Pattern):**
- **Structured Data (vnstock):** Written directly to local SQLite DB (`data/stockiv.db`).
  - *Why:* Prevents huge Context Window blowouts. Downstream Quant Analysts use `DatabaseSearchTool` with custom SQL queries.
- **Unstructured Data (Brave Search/News):** Written to local JSON cache (`data/raw/cache/`).
  - *Why:* Easy for LLMs to read/summarize.
  - To pass data persistently across completely separate runs, use `output_file: data/raw/context/{stock_symbols}_context.md`.
- **Processed Sentiment Data:** The Sentiment Analyst crew writes outputs directly to disk:
  - `data/processed/sentiment/market/{stock_symbols}_market_sentiment.md`
  - `data/processed/sentiment/ticker/{stock_symbols}_ticker_sentiment.md`
- **Strict API Rate Limiting:** External API calls (like Brave Search 30/day limit) MUST check the local JSON cache before firing `requests.get()`.

**Data Fetching Constraints (vnstock):**
- **Must use `vnstock` 3.x (e.g. `3.4.2`).**
- **Authentication Required:** VCI and KBS upstream APIs currently return 401/403 for 10-year financial statements without a paid account. The `VNSTOCK_API_KEY` must be loaded via `os.environ.get()` to bypass this.
- **Syntax:** Use OOP `Quote(symbol, source="KBS")` for prices and `Finance(symbol, source="KBS")` for statements. Melt wide DataFrames into narrow SQLite tables.
- **Market Indices limitation:** The `VCI` and `KBS` providers explicitly restrict fetching the `ratio_summary` or `events` for broad market indices (e.g., `VNINDEX`). Avoid requesting explicit P/E or P/B ratios for indices; instead rely entirely on the price `Quote.history()` data.

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


**Orchestrator & Telemetry (2026-03-05)**
- **LLM in Flow Routing:** Replaced simple regex routing with an LLM prompt that enforces JSON output syntax for robust dynamic routing. Always provide a legacy regex fallback.
- **Telemetry:** Added `tracing=True` to all Crew classes so execution runs populate the dashboard at `app.crew.ai`.
- **Telemetry Execution Auth:** In background worker shells, tests will emit "ephemeral" anonymous trace links unless `CREWAI_API_KEY` is explicitly declared in `.env` and loaded via python before execution (e.g. `source .env && uv run test.py`).


**Tool Architecture (2026-03-05)**
- **API Efficiency:** Before making external `requests.get()` calls, tools should execute a local SQLite `SELECT MAX()` cache-check.
- **Compound Keys for Time-Series:** Metrics like P/E and P/B change daily with price fluctuations. They must be cached on a `(ticker, date)` compound primary key, not just `(ticker, year_report)`.
- **Hybrid Period Retrieval:** When pulling financial statements, pull BOTH `period="year"` and `period="quarter"` simultaneously. This supports 10-year Graham history checks plus responsive TTM (Trailing Twelve Months) math when Q1 reports drop.
- **Regex Fallbacks for VCI:** `vnstock`'s VCI events API frequently returns `value=NaN` for historical dividends. Tools must dynamically parse the `event_title` (e.g. "1.000VND/CP", "1000 đồng/cổ phiếu") with regex to fill in pipeline gaps.

**Vietstock Scraping Architecture (2026-03-07)**
- **Static Bucket Routing:** Avoid general search engines (Brave Search limits) by deducing static buckets directly. E.g., Vietstock URLs resolve cleanly as `https://static2.vietstock.vn/data/{HOSE|HNX|UPCOM}/{year}/BCTN/VN/{ticker}_Baocaothuongnien_{year}.{pdf|zip}`. Fast `HEAD` requests validate these instantly.
- **Dynamic Year Fallback:** The current calendar year `Y` rarely has reports published yet. Scripts should immediately test `Y-1` and `Y-2` chronologically to ensure data hits.
- **ZIP Extraction:** Financial endpoints often bundle large reports in `.zip`. Tools MUST inspect the response and use `zipfile` extraction before parsing to Markdown.

**Memory & Context Ingestion Pattern (2026-03-06):**
- Crews needing long-term memory across tasks should initialize with `memory=True` and configure a local embedder (e.g. `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace provider).
- **Note on CrewAI Memory**: The extraction of entities/summaries for the knowledge base defaults to OpenAI. If `OPENAI_API_KEY` is not present, the embedder will still work locally, but entity extraction will fail with a warning. This is acceptable for simple local document retrieval.
- To read generated markdown contexts (like `FPT_macro_context.md`), agents MUST be explicitly equipped with the `FileReadTool` from `crewai_tools` and instructed to use it in `tasks.yaml`.

**Orchestration & Scheduling (n8n Webhook Architecture):**
- StockIV prefers decoupled architecture for execution triggers. Instead of writing complex cron scheduling inside Python, tasks are separated into individual `tasks.yaml` actions and executed via a simple FastAPI wrapper (`api.py`).
- This allows external tools like **N8N** to handle Discord triggers or Cron timings and simply `POST` to the respective endpoint.
  - *Weekly Market:* `POST /api/sentiment/market/weekly` (Cron Scheduled)
  - *On-Demand Ticker:* `POST /api/sentiment/ticker` (Discord Triggered)

**CrewAI Memory Tuning (2026-03-06):**
- CrewAI's vector database relies heavily on the embedder provider. If the default `huggingface` API provider crashes with `ValueError: could not convert string to float: 'error'`, the proper fix is to explicitly configure `provider: "sentence-transformer"` with `config: {"model_name": "all-MiniLM-L6-v2"}` inside `memory=Memory(...)`.
  - *Why:* This forces the application to download local ONNX/PyTorch models, running inference offline and completely isolating the database from HuggingFace rate limits.
- Short-term memory retention is configured by passing explicit `recency_weight` configurations into the Crew DB parameters.

**Hierarchical Delegation Pattern (Synthesizer Q&A 2026-03-07):**
- **Batching Questions:** To save LLM tokens and execution time, instruct 'manager' agents to ask multiple questions in a single `ask_question_to_coworker` message.
- **Strict Subordinate Output:** Since CrewAI delegation doesn't natively enforce nested `output_pydantic` schemas for coworkers, heavily prompt the subordinate agent's backstory with a strict text format (e.g. `Question | Status: MENTIONED/NOT_MENTIONED | Exact Quote | Summary`).
- **Path Resolution:** Coworkers equipped with `FileReadTool()` natively read the current working directory but can struggle with relative paths. Always pass or ensure `os.path.abspath()` is used when testing file reads in standalone mode.
- **Hierarchical Delegation Bug (CrewAI 1.10.1):** When `process=Process.hierarchical`, any task defined in `tasks.yaml` **must NOT** have a hardcoded `agent: [worker_name]`. If `agent:` is declared, the framework dynamically copies that worker's tools directly onto the Task itself. The Manager agent intercepts this tool-equipped Task, inherits the tools, and permanently bypasses its `Delegate` tool by simply executing the task APIs directly.
  - *Fix:* Always leave `agent:` completely blank in `tasks.yaml` when using a Hierarchical workflow. Scoping tools exactly to the workers (`collector.py`) forces the toolless Manager to accurately fall back onto using its standard Delegation Tooling.

**Discord MCP Integration Pattern (2026-03-08):**
- **Transport Setup:** Use `MCPServerStdio` with `command="npx"` and `args=["-y", "discord-mcp"]`.
- **Token Prefix Requirement:** The `discord-mcp` package directly passes the token to the Discord HTTP `Authorization` header. You **must** prefix it with `"Bot "` (e.g. `env={"DISCORD_BOT_TOKEN": f"Bot {discord_token}"}`). If you pass just the raw token string, Discord will return `401 Unauthorized`.
- **Bot Permissions:** Ensure the Discord Bot has "Message Content Intent" turned on in the developer portal, and has explicit channel read/write permissions where the tests/tools are being run.
- **FileReadTool Argument Parsing:** When instructing LLMs to use `FileReadTool` with specific paths, explicitly forbid them from passing the optional `start_line` and `line_count` arguments as empty strings (e.g., `""`). Passing empty strings to these fields throws a fatal Pydantic integer parsing error in CrewAI `v0.100+`.
- **Quality Gates & Chunking:** Before an Agent publishes to Discord, implement a "CRITICAL QUALITY BOUNDARY" prompt to ensure it actually parses the document and verifies it is a report (preventing stack traces from reaching the channel). Furthermore, explicitly instruct the LLM to chunk any Markdown payload longer than 1900 characters and call the `discord_send_message` tool multiple times sequentially to bypass the hard 2000-character Discord API limit.

**Dynamic Output Path Injection (2026-03-08):**
- **Pattern:** Passing `self.state.shared_data["my_path"]` down to Crew initialization `kickoff(inputs=self.state.shared_data)`.
- **YAML Mapping:** In `tasks.yaml`, use double quotes around variables to interpolate strings instead of crashing PyYAML parser into dictionaries:
  ```yaml
  output_file: "{my_path}"
  ```
- **PDF Exporting:** Standardize rendering local markdown directly into executive PDFs using `markdown` & `weasyprint` injected inside a CrewAI Tool instead of relying on external API document parsing.

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
- **Directory Roles:**
  - `tools/` strictly reserved for custom CrewAI `@tool` methods (e.g., `vnstock_tools.py`).
  - `tests/` strictly reserved for validation scripts (e.g., `test_collector.py`). Tests should implement and demonstrate CrewAI `Flow` constructs to show how agents/crews interact.
  - `scripts/` strictly reserved for developer utilities (e.g., `view_logs.py`).
- `logs/` directory stores execution logs in JSONL format
- `src/stockiv/knowledge/` contains 4 markdown files: framework, criteria, market_context, evidence_standard
- `memory/knowledge_base_review.md` contains detailed issues & action items for knowledge base

---

*Update this file with significant lessons, decisions, and context as the project evolves.*
