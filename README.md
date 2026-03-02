# StockIV

A stock analysis project using AI agent orchestration with [CrewAI](https://www.crewai.com/).

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Run the example:**
   ```bash
   uv run stockiv-run
   # or
   python -m stockiv
   ```

## Project Structure

```
stock-agent/
├── src/
│   └── stockiv/            # Main package
│       └── __init__.py     # Entry point with agents and crew
├── tools/                  # Custom tools
├── .env.example            # Environment variables template
└── pyproject.toml          # Project dependencies
```

## Requirements

- Python 3.12+
- ZhipuAI API key (GLM-4.7)
- (Optional) Serper API key for web search

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
