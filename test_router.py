import inspect
import crewai
import crewai.flow.flow

print("CrewAI Classes:", [name for name, obj in inspect.getmembers(crewai) if inspect.isclass(obj)])
try:
    print("Flow Classes:", [name for name, obj in inspect.getmembers(crewai.flow.flow) if inspect.isclass(obj)])
except Exception as e:
     print("Error Flow:", e)

