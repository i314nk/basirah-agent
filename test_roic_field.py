"""
Check ROIC field in GuruFocus keyratios data
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("ROIC FIELD INVESTIGATION")
print("=" * 60)
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache
print("Warming cache for AOS...")
agent._warm_cache_for_synthesis("AOS", current_year=2024)
print()

# Get the cached keyratios data
gf_keyratios = agent._get_from_cache("gurufocus_tool", "AOS_keyratios")

print("=" * 60)
print("KEYRATIOS STRUCTURE")
print("=" * 60)
print()

if gf_keyratios and gf_keyratios.get("success"):
    data = gf_keyratios.get("data", {})

    print(f"data keys: {list(data.keys())}")
    print()

    # Check metrics section
    if "metrics" in data:
        metrics = data["metrics"]
        print("metrics section:")
        print(f"  Type: {type(metrics)}")
        if isinstance(metrics, dict):
            print(f"  Keys: {list(metrics.keys())[:20]}")
            print()

            # Check for ROIC-related fields
            print("ROIC-related fields:")
            roic_fields = [k for k in metrics.keys() if "roic" in k.lower() or "return" in k.lower()]
            for field in roic_fields:
                value = metrics.get(field)
                print(f"  {field}: {value} (type: {type(value)})")
            print()

    # Check raw_data section
    if "raw_data" in data:
        raw_data = data["raw_data"]
        print("raw_data section:")
        print(f"  Type: {type(raw_data)}")
        if isinstance(raw_data, dict):
            print(f"  Keys: {list(raw_data.keys())[:20]}")
            print()

            # Look for fields that might contain ROIC
            print("Checking for ROIC/ROE/ROA fields:")
            for key in sorted(raw_data.keys()):
                if any(term in key.lower() for term in ["roic", "roe", "roa", "return", "capital"]):
                    value = raw_data.get(key)
                    print(f"  {key}: {value}")
            print()

            # Check if there's company_data
            if "company_data" in raw_data:
                company_data = raw_data["company_data"]
                print("company_data section:")
                print(f"  Type: {type(company_data)}")
                if isinstance(company_data, dict):
                    print(f"  Keys: {list(company_data.keys())}")
                    print()

                    # Check roic field specifically
                    if "roic" in company_data:
                        roic_value = company_data["roic"]
                        print(f"  [FOUND] roic field: {roic_value}")
                        print(f"           Type: {type(roic_value)}")

                        # Check if this looks like a percentage or dollar amount
                        try:
                            numeric_value = float(roic_value) if roic_value not in [None, "", "N/A"] else None
                            if numeric_value:
                                if numeric_value > 100:
                                    print(f"           [WARNING] Value > 100 suggests dollar amount, not percentage!")
                                elif numeric_value > 1:
                                    print(f"           [INFO] Value > 1 - likely percentage in whole numbers (e.g., 15 = 15%)")
                                else:
                                    print(f"           [INFO] Value < 1 - likely decimal percentage (e.g., 0.15 = 15%)")
                        except:
                            pass
else:
    print("[FAIL] Failed to get keyratios from cache")

print()
print("=" * 60)
