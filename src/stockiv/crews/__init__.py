"""
StockIV Crews Package

This package contains all the crews for the StockIV stock analysis system.
Each crew is responsible for a specific aspect of the analysis workflow.

Crews:
- Collector: Gathers stock data from various sources
- QuantAnalyst: Performs quantitative analysis
- SentimentAnalyst: Analyzes market sentiment
- Synthesizer: Combines analysis from multiple sources
- Reporter: Generates comprehensive reports
- Director: Guides and validates the analysis workflow
- Orchestrator: Coordinates all crews in the workflow
"""

from stockiv.crews.collector.collector import CollectorCrew
from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew
from stockiv.crews.reporter.reporter import ReporterCrew
from stockiv.crews.director.director import DirectorCrew
from stockiv.crews.orchestrator.orchestrator import StockOrchestratorFlow

__all__ = [
    "CollectorCrew",
    "SentimentAnalystCrew",
    "SynthesizerCrew",
    "ReporterCrew",
    "DirectorCrew",
    "StockOrchestratorFlow",
]
