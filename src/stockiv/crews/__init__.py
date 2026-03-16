"""
StockIV Crews Package

This package contains all the crews for the StockIV stock analysis system.
Each crew is responsible for a specific aspect of the analysis workflow.

Crews:
- Collector: Gathers stock data from APIs (vnstock, Brave Search, PDF reports)
- SentimentAnalyst: Analyzes macro and ticker-specific market sentiment
- Synthesizer: Interprets data against GCCP framework, produces evaluation reports
- Director: Validates analysis quality, detects anomalies, gates publication
- Reporter: Translates, exports PDF, and publishes reports to Discord
- Orchestrator: Classifies user requests and extracts target tickers
"""

from stockiv.crews.collector.collector import CollectorCrew
from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew
from stockiv.crews.reporter.reporter import ReporterCrew
from stockiv.crews.director.director import DirectorCrew
from stockiv.crews.orchestrator.orchestrator import OrchestratorCrew

__all__ = [
    "CollectorCrew",
    "SentimentAnalystCrew",
    "SynthesizerCrew",
    "ReporterCrew",
    "DirectorCrew",
    "OrchestratorCrew",
]
