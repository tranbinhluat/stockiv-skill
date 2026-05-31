# Implementation Plan: Discord-Based Human-In-The-Loop (HITL)

**Task Complexity**: Complex

## Phases

### Phase 1: Database & Tooling Enhancement
- **Action**: Create `approvals` table in `data/stockiv.db`.
- **Action**: Ensure `tools/discord_publisher_tool.py` handles dual-report attachments.
- **Agent**: `data_engineer` & `devops_engineer`
- **Validation**: Manual script to insert and verify message dispatch.

### Phase 2: Flow Modification (The "Bridge")
- **Action**: Refactor `src/stockiv/flows/report_loop.py` with polling logic.
- **Logic**: Use `pdf_exporter_tool` to generate attachments. If `REJECTED` or `TIMEOUT`, proceed to `route_to_failure`.
- **Agent**: `coder`
- **Validation**: Mock SQLite state change in a unit test.

### Phase 3: Discord Slash Command Implementation (The "Listener")
- **Action**: Implement `/approve` and `/reject` handler.
- **Action**: Update SQLite `approvals` table.
- **Agent**: `coder` & `devops_engineer`
- **Validation**: End-to-end test with simulated slash command.

### Phase 4: Final Cleanup & Documentation
- **Action**: Update documentation and remove CLI `input()` blocks.
- **Agent**: `technical_writer`
- **Validation**: All tests pass.
