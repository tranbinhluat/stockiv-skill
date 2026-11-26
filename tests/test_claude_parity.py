"""Drift guard: .claude/ (Claude Code) must stay in sync with .opencode/ (OpenCode)."""

import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
OC_AGENTS = ROOT / ".opencode" / "agent"
OC_COMMANDS = ROOT / ".opencode" / "command"
CC_AGENTS = ROOT / ".claude" / "agents"
CC_COMMANDS = ROOT / ".claude" / "commands"

AGENT_STEMS = sorted(p.stem for p in OC_AGENTS.glob("*.md"))
COMMAND_STEMS = sorted(p.stem for p in OC_COMMANDS.glob("*.md"))

EXPECTED_MODELS = {
    "stock-analyst": "sonnet",
    "market-scout": "sonnet",
    "gatekeeper-reviewer": "opus",
    "annual-report-scanner": "haiku",
}


def split_frontmatter(path: Path) -> tuple[str, str]:
    """Frontmatter sits between the 1st and 2nd lines that are exactly '---'."""
    if not path.is_file():
        pytest.fail(f"missing file: {path.relative_to(ROOT)}")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    fences = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == "---"]
    if len(fences) < 2:
        pytest.fail(f"no frontmatter in {path.relative_to(ROOT)}")
    first, second = fences[0], fences[1]
    return "".join(lines[first + 1 : second]), "".join(lines[second + 1 :])


def field(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.*)$", frontmatter, re.MULTILINE)
    return match.group(1).strip() if match else None


@pytest.mark.parametrize("stem", AGENT_STEMS)
def test_agent_parity(stem):
    oc_fm, oc_body = split_frontmatter(OC_AGENTS / f"{stem}.md")
    cc_fm, cc_body = split_frontmatter(CC_AGENTS / f"{stem}.md")
    assert cc_body == oc_body
    assert field(cc_fm, "name") == stem
    assert field(cc_fm, "description") == field(oc_fm, "description")
    assert field(cc_fm, "model") in {"sonnet", "opus", "haiku"}


def test_agent_models():
    actual = {
        stem: field(split_frontmatter(CC_AGENTS / f"{stem}.md")[0], "model")
        for stem in EXPECTED_MODELS
    }
    assert actual == EXPECTED_MODELS


def test_scanner_is_read_only():
    fm, _ = split_frontmatter(CC_AGENTS / "annual-report-scanner.md")
    assert field(fm, "tools") == "Read, Grep, Glob"


@pytest.mark.parametrize("stem", COMMAND_STEMS)
def test_command_parity(stem):
    oc_fm, oc_body = split_frontmatter(OC_COMMANDS / f"{stem}.md")
    cc_fm, cc_body = split_frontmatter(CC_COMMANDS / f"{stem}.md")
    assert cc_body == oc_body
    assert field(cc_fm, "description") == field(oc_fm, "description")
    assert field(cc_fm, "argument-hint") is not None


def _stems(directory: Path) -> set[str]:
    return {p.stem for p in directory.glob("*.md")}


def test_no_extra_claude_files():
    assert _stems(CC_AGENTS) == _stems(OC_AGENTS)
    assert _stems(CC_COMMANDS) == _stems(OC_COMMANDS)


def test_skills_symlink():
    link = ROOT / ".claude" / "skills"
    assert link.is_symlink(), ".claude/skills is not a symlink"
    assert os.readlink(link) == "../.opencode/skills"
    skill = link / "deepdive-flow" / "SKILL.md"
    assert skill.is_file(), f"unreadable: {skill}"
    assert skill.read_text(encoding="utf-8")


def test_settings_default_agent():
    settings = ROOT / ".claude" / "settings.json"
    assert settings.is_file(), ".claude/settings.json missing"
    assert json.loads(settings.read_text(encoding="utf-8"))["agent"] == "stock-analyst"
    assert (CC_AGENTS / "stock-analyst.md").is_file()


def test_claude_md_imports_agents_md():
    claude_md = ROOT / "CLAUDE.md"
    assert claude_md.is_file(), "CLAUDE.md missing"
    assert "@AGENTS.md" in claude_md.read_text(encoding="utf-8").splitlines()
