"""
Check balance_sheet for Total Debt alternatives
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache
agent._warm_cache_for_synthesis("AOS", current_year=2024)

# Get the cached data
gf_financials = agent._get_from_cache("gurufocus_tool", "AOS_financials")

if gf_financials and gf_financials.get("success"):
    data = gf_financials.get("data", {})
    raw_data = data.get("raw_data", {})

    if "balance_sheet" in raw_data:
        balance_sheet = raw_data["balance_sheet"]

        print("Searching for debt-related fields:")
        print()

        for key in sorted(balance_sheet.keys()):
            if "debt" in key.lower() or "borrow" in key.lower():
                print(f"  [DEBT-RELATED] {key}")

        print()
        print("All balance_sheet keys:")
        for key in sorted(balance_sheet.keys()):
            print(f"  - {key}")
