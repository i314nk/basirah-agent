"""
Debug historical arrays in GuruFocus cache
"""
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("HISTORICAL ARRAYS DEBUG")
print("=" * 60)
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache for AOS
print("Warming cache for AOS...")
agent._warm_cache_for_synthesis("AOS", current_year=2024)
print()

# Get the cached data
gf_financials = agent._get_from_cache("gurufocus_tool", "AOS_financials")

if gf_financials and gf_financials.get("success"):
    data = gf_financials.get("data", {})
    financials = data.get("financials", {})

    print("=" * 60)
    print("FINANCIALS KEYS")
    print("=" * 60)
    print(f"All keys: {list(financials.keys())}")
    print()

    # Check for historical key
    if "historical" in financials:
        print("[OK] 'historical' key EXISTS")
        historical = financials["historical"]
        print(f"Historical keys: {list(historical.keys())}")
        print()

        # Check each array
        for key, array in historical.items():
            print(f"{key}:")
            print(f"  Type: {type(array)}")
            print(f"  Length: {len(array) if isinstance(array, list) else 'N/A'}")
            if isinstance(array, list) and len(array) > 0:
                print(f"  First 3 values: {array[:3]}")
                print(f"  Last 3 values: {array[-3:]}")
            else:
                print(f"  Values: {array}")
            print()
    else:
        print("[FAIL] 'historical' key DOES NOT EXIST")
        print()

    # Check fiscal_periods
    if "fiscal_periods" in financials:
        fiscal_periods = financials["fiscal_periods"]
        print(f"fiscal_periods: {fiscal_periods}")
        print(f"fiscal_periods length: {len(fiscal_periods)}")
    else:
        print("[FAIL] 'fiscal_periods' key DOES NOT EXIST")

else:
    print("[FAIL] Failed to get GuruFocus financials from cache")

print()
print("=" * 60)
