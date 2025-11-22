"""
Check the actual structure of period_data from GuruFocus API
"""
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("PERIOD_DATA STRUCTURE CHECK")
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
    raw_data = data.get("raw_data", {})

    print("=" * 60)
    print("RAW DATA STRUCTURE")
    print("=" * 60)
    print(f"raw_data keys: {list(raw_data.keys())}")
    print()

    # Check income_statement
    if "income_statement" in raw_data:
        income_statement = raw_data["income_statement"]
        print("income_statement:")
        print(f"  Type: {type(income_statement)}")
        print(f"  Keys: {list(income_statement.keys())[:15] if isinstance(income_statement, dict) else 'Not a dict'}")
        print()

        if isinstance(income_statement, dict):
            # Check if Revenue exists
            if "Revenue" in income_statement:
                revenue = income_statement["Revenue"]
                print("  Revenue field:")
                print(f"    Type: {type(revenue)}")
                print(f"    Length: {len(revenue) if isinstance(revenue, list) else 'N/A'}")
                if isinstance(revenue, list) and len(revenue) > 0:
                    print(f"    First 3: {revenue[:3]}")
                    print(f"    Last 3: {revenue[-3:]}")
            else:
                print("  Revenue: NOT FOUND")

    # Check balance_sheet
    if "balance_sheet" in raw_data:
        balance_sheet = raw_data["balance_sheet"]
        print()
        print("balance_sheet:")
        print(f"  Type: {type(balance_sheet)}")
        print(f"  Keys: {list(balance_sheet.keys())[:15] if isinstance(balance_sheet, dict) else 'Not a dict'}")

    # Check cashflow_statement
    if "cashflow_statement" in raw_data:
        cashflow_statement = raw_data["cashflow_statement"]
        print()
        print("cashflow_statement:")
        print(f"  Type: {type(cashflow_statement)}")
        print(f"  Keys: {list(cashflow_statement.keys())[:15] if isinstance(cashflow_statement, dict) else 'Not a dict'}")

else:
    print("[FAIL] Failed to get GuruFocus financials from cache")

print()
print("=" * 60)
