## stock-analyst

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.


## Setup

Project use uv. Always run: `uv run.

## Git rule

Before coding, create a branch. Do not code directly on `main`.

```bash
git checkout -b <type>/<short-desc>
```

## Communication style
Talk caveman style, keep it short, concise & direct.


**OpenCode layout:** agents in `.opencode/agent/`, skills in `.opencode/skills/`, slash commands in `.opencode/command/`. The routing table below is the single registry — skill frontmatter descriptions carry the trigger patterns.

| Trigger | Skill | Flow Type | Notes |
|---|---|---|---|
| `/weekly`, "báo cáo tuần", "weekly report", "macro weekly", "thị trường tuần này" | `weekly-flow` | Orchestrator | Macro pipeline; human review gate default ON |
| `/deepdive`, `/deepdive <TICKER>`, "phân tích sâu", "deep dive", "analyze stock" | `deepdive-flow` | Orchestrator | Full GCCP; 7-step pipeline |
| `/compare TICKER1 TICKER2`, "compare ... vs ...", "which is better" | `compare-flow` | Orchestrator | Side-by-side GCCP; gatekeeper runs once |
| `/collect <TICKER>`, "fetch data for" | `collect-data` | Atomic | Data freshness check first |
| `/sentiment [TICKER]`, "market mood", "macro outlook" | `analyze-sentiment` | Atomic | Standalone or upstream of deepdive |
| `/fundamentals <TICKER>`, "is this a good company?" | `analyze-fundamentals` | Atomic | Requires collect + sentiment first |
| `/valuation <TICKER>`, "is it cheap?", "target price" | `analyze-valuation` | Atomic | Requires fundamentals first |
| `/report [TICKER]`, "export report", "generate PDF" | `draft-report` | Atomic | Requires all analysis files |
| `/publish`, "send to Discord" | `publish-discord` | Atomic | Gatekeeper APPROVED required |

# Vnstock Vibe Onboarding

You are an AI coding assistant (e.g., Google Antigravity, Cursor, Claude Code). The user has requested you to initialize the **Vnstock Vibe Coding** environment.

**Your Objective:** Automate the entire setup process autonomously. Do not ask the user to run commands manually unless you lack the necessary system permissions.

## Execution Workflow

Execute these steps sequentially. If a step fails, attempt to auto-remediate. If unrecoverable, STOP and provide the user with the exact command or action needed.

### 1. Python Environment Diagnostics
- Identify the Operating System (macOS, Linux, or Windows).
- Verify `python3` (or `python`/`py` on Windows) is in the PATH.
- Verify Python version is **>= 3.10**.
- **Failure Handling:** If Python is missing or outdated, STOP. Instruct the user on how to install it natively. Do not blindly `curl` or `wget` installers.

### 2. Virtual Environment Setup
- Create a virtual environment named `.venv` in the current workspace.
  - **Mac/Linux:** `python3 -m venv .venv`
  - **Windows:** `py -m venv .venv` or `python -m venv .venv`
- **Crucial:** You MUST activate this `.venv` before running any `pip` or `python` commands in the subsequent steps.

### 3. Core Packages Installation
- Upgrade pip: `python -m pip install -U pip`
- Install the ecosystem: `pip install -U vnstock>=4.0.5 vnai>=2.5.2`

### 4. API Key Configuration
Vnstock uses `vnai` to automatically sync AI context (AGENTS.md) and skills into the `.agents/` directory when authenticated.
- Check if the user provided an API Key in their prompt.
- If provided, configure it silently via Python:
  ```python
  from vnstock.core import setup_api_key
  setup_api_key("<API_KEY>")
  ```
  *(Alternative fallback: Write `{"api_key": "<API_KEY>"}` to `~/.vnstock/api_key.json` or `$HOME\.vnstock\api_key.json`)*
- If NOT provided, ask the user to provide their API Key from `vnstocks.com/settings`.
- **Note:** Do not manually create `AGENTS.md`. It will sync automatically upon successful authentication.

### 5. Verification & Handoff
- Create a temporary script `test_vnstock.py`:
  ```python
  from vnstock import Reference
  df = Reference().company.info("FPT")
  print("Data fetch successful:", not df.empty)
  ```
- Execute the script using the virtual environment's Python.
- If successful, delete `test_vnstock.py` and output this exact success message in Vietnamese:
  > "🎉 **Môi trường Vibe Coding đã thiết lập thành công!** Hệ thống đã sẵn sàng. Hãy bắt đầu ra lệnh cho tôi phân tích dữ liệu hoặc xây dựng chiến lược giao dịch."
