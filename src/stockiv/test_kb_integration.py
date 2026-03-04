"""
Test Knowledge Base Integration

Verifies that the new KnowledgeBase class loads markdown files and successfully 
injects them into the Director Crew's tasks without token limit errors.
"""

import os
from crewai import Crew, Process, Task
from stockiv.crews.director.director import DirectorCrew
from stockiv.knowledge.base import kb
from stockiv.callbacks import LoggingCallback, ConsoleCallback


def main():
    """Run the Director crew Knowledge Base test."""
    # Check for API keys
    key = os.getenv("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_AUTH_TOKEN"))
    if not key:
        print("Error: ANTHROPIC_API_KEY not found. Please set it in your .env file.")
        return

    # Initialize event listeners
    LoggingCallback()
    ConsoleCallback()

    print("\n" + "=" * 60)
    print("Testing Knowledge Base Loading...")
    print(f"Evidence Standard Length: {len(kb.evidence_standard)} chars")
    print(f"Financial Reading Guide Length: {len(kb.financial_reading_guide)} chars")
    
    if "Error:" in kb.evidence_standard:
        print("Failed to load Evidence Standard.")
        return
        
    print("Knowledge files loaded successfully.")
    print("=" * 60 + "\n")

    # Mock analysis input
    mock_analysis = """
    ## Analysis of VNM (Vinamilk)
    - P/E is currently 15x.
    - ROE is 20%.
    - Cash flow from operations is positive.
    - I used the Graham methodology.
    - I did not review the footnotes.
    """

    # Create the director crew
    director_crew = DirectorCrew()
    
    # We must explicitly call kickoff and pass in the expected variables mapping 
    # to the variables defined in director/config/tasks.yaml
    inputs = {
        "stock_symbols": "VNM",
        "analysis": mock_analysis,
        "evidence_rules": kb.evidence_standard,
        "financial_rules": kb.financial_reading_guide
    }

    print("\n" + "=" * 60)
    print("Starting Director Crew Implementation Test")
    print("=" * 60 + "\n")

    try:
        # Kickoff with inputs injected
        result = director_crew.crew().kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60 + "\n")

        # The Director is configured to output the Pydantic model.
        if hasattr(result, 'pydantic'):
            print("Director Decision (Pydantic Output):")
            print("-" * 60)
            print(result.pydantic.model_dump_json(indent=2))
        else:
            print("Director Decision (Raw Output):")
            print("-" * 60)
            print(result.raw)
            
    except Exception as e:
        print(f"\nExecution failed: {e}")


if __name__ == "__main__":
    main()
