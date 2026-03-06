import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew

app = FastAPI(
    title="StockIV AI Integrations API",
    description="Webhook endpoints for N8N to trigger specific AI Crews.",
    version="1.0.0",
)


class TickerRequest(BaseModel):
    symbol: str


def _get_context_paths(symbol: str):
    """Helper to locate context files."""
    base_dir = Path(__file__).parent.parent.parent
    macro_context_file = base_dir / "data" / "raw" / "context" / f"{symbol}_macro_context.md"
    ticker_context_file = base_dir / "data" / "raw" / "context" / f"{symbol}_ticker_context.md"
    
    # We require the context to be crawled first
    if not macro_context_file.exists() or not ticker_context_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Context files for {symbol} not found. Ensure Collector Crew runs first."
        )
        
    return str(macro_context_file), str(ticker_context_file)


@app.post("/api/sentiment/market/weekly")
async def trigger_market_sentiment(request: TickerRequest):
    """
    TRIGGER: Scheduled Weekly via N8N
    Executes ONLY the summarize_market task to generate a Weekly Macro Report.
    """
    try:
        macro_path, ticker_path = _get_context_paths(request.symbol)
        
        now = datetime.now()
        year, week_num, _ = now.isocalendar()
        
        inputs = {
            "stock_symbols": request.symbol,
            "date": now.strftime("%Y-%m-%d"),
            "year": str(year),
            "week": str(week_num),
            "macro_context_file": macro_path,
            "ticker_context_file": ticker_path,
        }
        
        crew_instance = SentimentAnalystCrew().crew()
        
        # Isolate ONLY the market task
        crew_instance.tasks = [t for t in crew_instance.tasks if t.name == "summarize_market"]
        
        result = crew_instance.kickoff(inputs=inputs)
        return {"status": "success", "task": "summarize_market", "output": result.raw}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sentiment/ticker")
async def trigger_ticker_sentiment(request: TickerRequest):
    """
    TRIGGER: On-Demand via Discord (n8n Webhook)
    Executes ONLY the summarize_symbol task.
    """
    try:
        macro_path, ticker_path = _get_context_paths(request.symbol)
        
        now = datetime.now()
        year, week_num, _ = now.isocalendar()
        
        inputs = {
            "stock_symbols": request.symbol,
            "date": now.strftime("%Y-%m-%d"),
            "year": str(year),
            "week": str(week_num),
            "macro_context_file": macro_path,
            "ticker_context_file": ticker_path,
        }
        
        crew_instance = SentimentAnalystCrew().crew()
        
        # Isolate ONLY the symbol task
        crew_instance.tasks = [t for t in crew_instance.tasks if t.name == "summarize_symbol"]
        
        result = crew_instance.kickoff(inputs=inputs)
        return {"status": "success", "task": "summarize_symbol", "output": result.raw}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_server():
    """Run the API server on port 8000."""
    uvicorn.run("stockiv.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run_server()
