import sys

sys.path.append("/home/luattranb/Documents/projects/stock-agent/src")
from stockiv.crews.synthesizer.synthesizer import SynthesizerCrew

crew = SynthesizerCrew()
print("First pass agents:")
for a in crew.crew().agents:
    print(f" - {a.role}")
print("\nRevision agents:")
for a in crew.revision_crew().agents:
    print(f" - {a.role}")
