import pyrootutils

# Find the root once
ROOT = pyrootutils.find_root(search_from=__file__, indicator=".env")

# Define all paths relative to that root
DATA_DIR = ROOT / "data"

# Sub roots
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORT_DIR = DATA_DIR / "reports"

# Raw data paths
RAW_CONTEXT_DIR = RAW_DIR / "context"
RAW_ANNUAL_REPORT_DIR = RAW_DIR / "annual_reports"
RAW_CACHE_DIR = RAW_DIR / "cache"


# Processed data paths
PROCESSED_SENTIMENT_MARKET_DIR = PROCESSED_DIR / "sentiment" / "market"
PROCESSED_SENTIMENT_TICKER_DIR = PROCESSED_DIR / "sentiment" / "ticker"
PROCESSED_ANNUAL_REPORTS_DIR = PROCESSED_DIR / "annual_reports"
PROCESSED_SYNTHESIZER_DIR = PROCESSED_DIR / "synthesizer"

# Report paths  / Finalize Data
REPORT_MARKET_DIR = REPORT_DIR / "market"
REPORT_TICKER_DIR = DATA_DIR / "report"

CONFIG_DIR = ROOT / "src" / "stockiv" / "config"
LOGS_DIR = ROOT / "logs"

# Ensure they exist
for p in [
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    RAW_CONTEXT_DIR,
    RAW_ANNUAL_REPORT_DIR,
    RAW_CACHE_DIR,
    PROCESSED_SENTIMENT_MARKET_DIR,
    PROCESSED_SENTIMENT_TICKER_DIR,
    PROCESSED_ANNUAL_REPORTS_DIR,
    PROCESSED_SYNTHESIZER_DIR,
    REPORT_MARKET_DIR,
    REPORT_TICKER_DIR,
    LOGS_DIR,
]:
    p.mkdir(parents=True, exist_ok=True)
