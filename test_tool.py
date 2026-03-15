from tools.sqlite_tools import CalculateFrameworkMetricsTool

tool = CalculateFrameworkMetricsTool()
res = tool._run("FPT")
print(res)
