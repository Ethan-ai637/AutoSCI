#!/usr/bin/env python3
import importlib
import platform
import sys

from _common import SKILL_VERSION, ANALYSIS_PLAN_SCHEMA_VERSION, POWER_PLAN_SCHEMA_VERSION

REQUIRED = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "openpyxl"]
OPTIONAL = []

print(f"scientific-data-analysis: {SKILL_VERSION}")
print(f"analysis-plan schema: {ANALYSIS_PLAN_SCHEMA_VERSION}")
print(f"power-plan schema: {POWER_PLAN_SCHEMA_VERSION}")
print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {platform.platform()}")
failed = False
if sys.version_info < (3, 10):
    print("Python >=3.10 is required")
    failed = True
for name in REQUIRED + OPTIONAL:
    try:
        mod = importlib.import_module(name)
        print(f"{name}: {getattr(mod, '__version__', 'installed')}")
    except Exception as e:
        label = "REQUIRED" if name in REQUIRED else "optional"
        print(f"{name}: MISSING ({label}) - {e}")
        if name in REQUIRED:
            failed = True
sys.exit(1 if failed else 0)
