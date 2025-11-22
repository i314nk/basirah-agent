"""
Test GuruFocus cache structure
"""
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("GURUFOCUS CACHE STRUCTURE TEST")
print("=" * 60)
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache for AOS
print("Warming cache for AOS...")
agent._warm_cache_for_synthesis("AOS", current_year=2024)
print()

# Check what's in the cache
print("=" * 60)
print("CACHE CONTENTS")
print("=" * 60)
print()

gf_cache = agent.tool_cache.get("gurufocus", {})
print(f"GuruFocus cache keys: {list(gf_cache.keys())}")
print()

# Check financials cache
if "AOS_financials" in gf_cache:
    gf_financials = gf_cache["AOS_financials"]
    print("AOS_financials structure:")
    print(f"  Top-level keys: {list(gf_financials.keys())}")
    print()

    if "data" in gf_financials:
        data = gf_financials["data"]
        print(f"  data keys: {list(data.keys())}")
        print(f"  Has raw_data: {'raw_data' in data}")
        print()

        if "financials" in data:
            financials = data["financials"]
            print(f"  financials keys: {list(financials.keys())[:10]}...")
            print(f"  financials is empty: {len(financials) == 0}")
            print()

            # Check raw_data to see what the API actually returned
            if "raw_data" in data:
                raw_data = data["raw_data"]
                print(f"  raw_data keys: {list(raw_data.keys())[:10] if raw_data else 'None'}...")
                print()

                if raw_data:
                    # Check for Fiscal Year
                    fiscal_year = raw_data.get("Fiscal Year", [])
                    print(f"  raw_data['Fiscal Year']: {fiscal_year[:5] if isinstance(fiscal_year, list) and len(fiscal_year) >= 5 else fiscal_year}")
                    print()

            if "fiscal_periods" in financials:
                fiscal_periods = financials["fiscal_periods"]
                print(f"  [OK] fiscal_periods FOUND: {fiscal_periods[:5] if len(fiscal_periods) >= 5 else fiscal_periods}")
            else:
                print(f"  [FAIL] fiscal_periods NOT FOUND in financials")
                if len(financials) > 0:
                    print(f"  Available keys: {list(financials.keys())}")
                else:
                    print(f"  financials dict is completely empty - processing failed!")
        else:
            print(f"  [FAIL] 'financials' key NOT FOUND in data")
    else:
        print(f"  ✗ 'data' key NOT FOUND in gf_financials")
else:
    print("✗ AOS_financials NOT FOUND in cache")

print()
print("=" * 60)
