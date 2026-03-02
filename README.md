# CrewAI Project

A project demonstrating AI agent orchestration using [CrewAI](https://www.crewai.com/).

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
   uv run crewai-run
   # or
   python -m crewai_project
   ```

## Project Structure

```
crewai-project/
├── src/
│   └── crewai_project/   # Main package
│       └── __init__.py   # Entry point with agents and crew
├── tools/                # Custom tools
├── .env.example          # Environment variables template
└── pyproject.toml        # Project dependencies
```

## Requirements

- Python 3.12+
- OpenAI API key
- (Optional) Serper API key for web search

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
