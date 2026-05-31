# Design Document: Discord-Based Human-In-The-Loop (HITL)

**Goal**: Replace CLI `input()` with a persistent Discord slash command approval system using an SQLite state bridge and a 2-hour polling loop.

## Architecture
- **State Bridge**: SQLite table `pending_approvals` in `data/stockiv.db`.
- **Flow Control**: Polling loop in `ReportLoopFlow` (src/stockiv/flows/report_loop.py).
- **Communication**: Discord message with PDF attachments (Synthesizer & Director).
- **Interface**: Slash commands `/approve <id>` and `/reject <id> [feedback]`.

## Data Schema (`pending_approvals`)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique request ID |
| ticker | TEXT | Stock symbol |
| status | TEXT | PENDING / APPROVED / REJECTED |
| feedback | TEXT | Human rejection reason |
| timestamp | DATETIME | When the request was created |

## Workflow
1. Flow reaches HITL.
2. Generates PDFs (Synthesizer vN, Director vN).
3. Posts summary + PDF files to Discord with `id`.
4. Polls SQLite every 60s for `status != 'PENDING'`.
5. Timeout after 2 hours → `route_to_failure`.
6. User runs `/approve` or `/reject` on Discord.
7. Slash command handler updates SQLite.
8. Flow detects change, resumes/fails accordingly.
