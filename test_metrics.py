import sys

sys.path.append("/home/luattranb/Documents/projects/stock-agent/src")
sys.path.append("/home/luattranb/Documents/projects/stock-agent/tools")
from sqlite_tools import CalculateFrameworkMetricsTool, FetchRecentFinancialsTool

print("--- METRICS ---")
print(CalculateFrameworkMetricsTool()._run("FPT"))
print("\n--- FINANCIALS ---")
print(FetchRecentFinancialsTool()._run("FPT"))
