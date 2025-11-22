"""
Check ROIC in Profitability section of GuruFocus keyratios
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("ROIC IN PROFITABILITY SECTION")
print("=" * 60)
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache
agent._warm_cache_for_synthesis("AOS", current_year=2024)

# Get the cached keyratios data
gf_keyratios = agent._get_from_cache("gurufocus_tool", "AOS_keyratios")

if gf_keyratios and gf_keyratios.get("success"):
    data = gf_keyratios.get("data", {})
    raw_data = data.get("raw_data", {})

    if "Profitability" in raw_data:
        profitability = raw_data["Profitability"]
        print("Profitability section:")
        print(f"  Type: {type(profitability)}")
        print()

        if isinstance(profitability, dict):
            print("All Profitability keys:")
            for key in sorted(profitability.keys()):
                print(f"  - {key}")
            print()

            # Check for ROIC specifically
            print("Checking ROIC-related fields:")
            for key in sorted(profitability.keys()):
                if any(term in key.lower() for term in ["roic", "return", "capital"]):
                    value = profitability.get(key)
                    print(f"  {key}:")
                    print(f"    Value: {value}")
                    print(f"    Type: {type(value)}")

                    # If it's a list (historical data), show first/last values
                    if isinstance(value, list) and len(value) > 0:
                        print(f"    Length: {len(value)}")
                        print(f"    First value: {value[0]}")
                        print(f"    Last value: {value[-1]}")
                    print()
    else:
        print("[MISSING] 'Profitability' section not found in raw_data")

    # Also check Fundamental section
    if "Fundamental" in raw_data:
        fundamental = raw_data["Fundamental"]
        print()
        print("=" * 60)
        print("FUNDAMENTAL SECTION")
        print("=" * 60)
        print()

        if isinstance(fundamental, dict):
            print("Checking for ROIC/Owner Earnings fields:")
            for key in sorted(fundamental.keys()):
                if any(term in key.lower() for term in ["roic", "owner", "earnings", "capital"]):
                    value = fundamental.get(key)
                    print(f"  {key}: {value}")
else:
    print("[FAIL] Failed to get keyratios from cache")

print()
print("=" * 60)
