"""
Knowledge Base Utility

Loads the Markdown files containing the GCCP framework and rules so they
can be dynamically injected into CrewAI tasks as strings.
"""

import os
from pathlib import Path

# The directory where this script lives is the knowledge base directory
KB_DIR = Path(__file__).parent


class KnowledgeBase:
    """Loads the core GCCP investment rules from Markdown files."""

    def __init__(self):
        self._framework = None
        self._criteria = None
        self._market_context = None
        self._evidence_standard = None
        self._industry_guides = None
        self._financial_reading_guide = None

    def _read_file(self, filename: str) -> str:
        """Reads a markdown file from the knowledge directory."""
        filepath = KB_DIR / filename
        if not filepath.exists():
            return f"Error: Knowledge base file '{filename}' not found at {filepath}"
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading '{filename}': {str(e)}"

    @property
    def framework(self) -> str:
        """The core Good Company Cheap Price framework."""
        if self._framework is None:
            self._framework = self._read_file("framework.md")
        return self._framework

    @property
    def criteria(self) -> str:
        """The Graham/Greenblatt/Lynch selection criteria."""
        if self._criteria is None:
            self._criteria = self._read_file("criteria.md")
        return self._criteria

    @property
    def market_context(self) -> str:
        """Market phases and VN-Index requirements."""
        if self._market_context is None:
            self._market_context = self._read_file("market_context.md")
        return self._market_context

    @property
    def evidence_standard(self) -> str:
        """The zero-trust evidence rule set."""
        if self._evidence_standard is None:
            self._evidence_standard = self._read_file("evidence_standard.md")
        return self._evidence_standard

    @property
    def industry_guides(self) -> str:
        """Specific metrics for Vietnamese industries."""
        if self._industry_guides is None:
            self._industry_guides = self._read_file("industry_guides.md")
        return self._industry_guides

    @property
    def financial_reading_guide(self) -> str:
        """The anomaly detection toolkit based on double-entry accounting."""
        if self._financial_reading_guide is None:
            self._financial_reading_guide = self._read_file("financial_reading_guide.md")
        return self._financial_reading_guide

# Create a singleton instance for easy import
kb = KnowledgeBase()
