"""
test_data_interpreter.py

Test script to ensure the new Synthesizer Crew (Data Interpreter)
correctly receives the raw string framework from the KnowledgeBase.
"""

from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew

def test_interpreter():
    print("🚀 Instantiating Synthesizer Crew...")
    crew = SynthesizerCrew().crew()
    
    inputs = {
        "stock_symbols": "FPT",
        "date": "2026-03-06"
    }

    print("\n🚀 Kicking off the Data Interpreter task...")
    result = crew.kickoff(inputs=inputs)
    
    print("\n" + "="*50)
    print("FINAL DATA INTERPRETER SUMMARY:")
    print("="*50)
    print(result.raw)
    print("="*50 + "\n")

if __name__ == "__main__":
    test_interpreter()
