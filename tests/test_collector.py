import sys
import os
import json

# Ensure tools can be imported properly for standalone testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from stockiv.crews.collector.collector import CollectorCrew

def test_collector():
    print("Initializing Collector Crew...")
    collector_base = CollectorCrew()
    crew = collector_base.crew()
    
    print("\nKicking off Collector Crew for stock 'FPT'...")
    # NOTE: Since financial_statements task is currently a placeholder due to 
    # API locks, and we don't want to burn Brave API unnecessarily during automated tests,
    # we'll just test the initialization here.
    
    agents = crew.agents
    tasks = crew.tasks
    
    print(f"Loaded {len(agents)} agents:")
    for a in agents:
        print(f" - {a.role}")
        
    print(f"\nLoaded {len(tasks)} tasks:")
    for t in tasks:
        print(f" - {t.description.splitlines()[0]}")
        
if __name__ == "__main__":
    test_collector()
