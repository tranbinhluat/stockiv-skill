import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from stockiv.crews.collector.collector import CollectorCrew

crew = CollectorCrew().crew()
print(f"Hierarchical Process: {crew.process}")
print(f"Manager Agent: {crew.manager_agent.role if crew.manager_agent else 'None'}")
print(
    f"Manager tools before kickoff: {[t.name for t in crew.manager_agent.tools] if crew.manager_agent and crew.manager_agent.tools else 'None'}"
)
print()
for t in crew.tasks:
    agent_role = getattr(t.agent, "role", "None") if t.agent else "None"
    tools_list = (
        [getattr(tool, "name", str(tool)) for tool in getattr(t, "tools", [])]
        if getattr(t, "tools", None)
        else "None"
    )
    print(f"Task '{t.name}':")
    print(f"  agent: {agent_role}")
    print(f"  tools: {tools_list}")
