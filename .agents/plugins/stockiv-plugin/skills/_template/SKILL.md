---
name: {SKILL_NAME}
description: {ONE_LINE_DESCRIPTION}
---

# {Skill Name}

{Brief description of what this skill does and when to use it.}

## What This Skill Does

{Step-by-step description of the skill's workflow.}

## Depends On

{List skills or files that must exist before this skill runs. Use skill-routing.md as reference.}

## Inputs

{Files or data this skill reads. Format: `path/to/file.md` — written by `skill-name`}

## Outputs

{Files this skill writes. Format: `path/to/file.md`}

## Freshness Check

{Describe when to skip execution because output is already fresh. E.g.: "Skip if output files < 7 days old unless --force flag set."}

## Execution Steps

### Step 1 — {Step Name}
{What the agent does in this step. Be specific about CLI commands, file reads, or analysis tasks.}

### Step 2 — {Step Name}
{...}

## Output to User

{What the agent shows the user when this skill completes. Format, summary table, file paths, etc.}

## Error Handling

{What to do if a required input file is missing, a CLI command fails, or data is stale.}
