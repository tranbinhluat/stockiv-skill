import asyncio
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from crewai.agent import Agent
from crewai.flow.flow import Flow, listen, start
from src.stockiv.agents.base import get_llm


# Define a structured output format
class MarketAnalysis(BaseModel):
    key_trends: List[str] = Field(description="List of identified market trends")
    market_size: str = Field(description="Estimated market size")
    competitors: List[str] = Field(description="Major competitors in the space")


# Define flow state
class MarketResearchState(BaseModel):
    product: str = ""
    analysis: MarketAnalysis | None = None


# Create a flow class
class MarketResearchFlow(Flow[MarketResearchState]):
    @start()
    def initialize_research(self) -> Dict[str, Any]:
        print(f"Create a mock research for {self.state.product}")
        return {"product": self.state.product}

    @listen(initialize_research)
    async def analyze_market(self) -> Dict[str, Any]:
        # Create an Agent for market research
        analyst = Agent(
            role="Market Research Analyst",
            goal=f"Create a mock analysis for {self.state.product}",
            backstory="You are an experienced market analyst with expertise in "
            "identifying market trends and opportunities.",
            verbose=True,
            llm=get_llm("qwen3-coder-plus"),
        )

        # Define the research query
        query = f"""
        Create a mock research for the market of {self.state.product}. Include:
        1. Key market trends
        2. Market size
        3. Major competitors

        Format your response according to the specified structure.
        """

        # Execute the analysis with structured output format
        result = await analyst.kickoff_async(query, response_format=MarketAnalysis)
        if result.pydantic:
            print("result", result.pydantic)
        else:
            print("result", result)

        # Return the analysis to update the state
        return {"analysis": result.pydantic}

    @listen(analyze_market)
    def present_results(self, analysis) -> None:
        print("\nMarket Analysis Results")
        print("=====================")

        if isinstance(analysis, dict):
            # If we got a dict with 'analysis' key, extract the actual analysis object
            market_analysis = analysis.get("analysis")
        else:
            market_analysis = analysis

        if market_analysis and isinstance(market_analysis, MarketAnalysis):
            print("\nKey Market Trends:")
            for trend in market_analysis.key_trends:
                print(f"- {trend}")

            print(f"\nMarket Size: {market_analysis.market_size}")

            print("\nMajor Competitors:")
            for competitor in market_analysis.competitors:
                print(f"- {competitor}")
        else:
            print("No structured analysis data available.")
            print("Raw analysis:", analysis)


# Usage example
async def run_flow():
    flow = MarketResearchFlow()
    flow.plot("MarketResearchFlowPlot")
    result = await flow.kickoff_async(inputs={"product": "AI-powered chatbots"})
    return result


# Run the flow
if __name__ == "__main__":
    asyncio.run(run_flow())
