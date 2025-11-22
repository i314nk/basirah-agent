"""
Check exact field names in GuruFocus nested structure
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("FIELD NAMES CHECK")
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
    print("CHECKING FIELD NAMES WE NEED")
    print("=" * 60)
    print()

    # Income statement
    if "income_statement" in raw_data:
        income_stmt = raw_data["income_statement"]
        print("income_statement fields we need:")
        fields_needed = ["Net Income", "Revenue", "Operating Income"]
        for field in fields_needed:
            exists = field in income_stmt
            print(f"  {field}: {'[OK]' if exists else '[MISSING]'}")
        print()

    # Balance sheet
    if "balance_sheet" in raw_data:
        balance_sheet = raw_data["balance_sheet"]
        print("balance_sheet fields we need:")
        fields_needed = [
            "Total Assets",
            "Total Liabilities",
            "Cash and Cash Equivalents",
            "Total Debt",
            "Total Stockholders Equity"
        ]
        for field in fields_needed:
            exists = field in balance_sheet
            print(f"  {field}: {'[OK]' if exists else '[MISSING]'}")
        print()

    # Cashflow statement
    if "cashflow_statement" in raw_data:
        cashflow_stmt = raw_data["cashflow_statement"]
        print("cashflow_statement fields we need:")

        # Check common variations
        variations = {
            "Depreciation & Amortization": [
                "Depreciation & Amortization",
                "Depreciation Amortization & Depletion",
                "Cash Flow Depreciation, Depletion and Amortization",
                "Depreciation, Depletion and Amortization"
            ],
            "Capital Expenditure": [
                "Capital Expenditure",
                "Purchase Of Property, Plant, Equipment",
                "Capital Spending"
            ],
            "Free Cash Flow": [
                "Free Cash Flow",
                "Free Cash Flow Per Share",
                "Levered Free Cash Flow"
            ]
        }

        for concept, field_variations in variations.items():
            print(f"\n  {concept}:")
            found = False
            for field in field_variations:
                if field in cashflow_stmt:
                    print(f"    [OK] Found as: '{field}'")
                    found = True
                    break
            if not found:
                print(f"    [MISSING] None of these found:")
                for field in field_variations:
                    print(f"      - {field}")

        print()
        print("  All cashflow_statement keys:")
        for key in sorted(cashflow_stmt.keys()):
            print(f"    - {key}")

else:
    print("[FAIL] Failed to get GuruFocus financials from cache")

print()
print("=" * 60)
