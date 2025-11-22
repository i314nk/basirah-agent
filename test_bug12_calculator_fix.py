"""
Quick test to verify Bug #12 fix: Calculator results correctly matched by type

This tests that owner_earnings and ROIC don't get the same value.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("BUG #12 FIX VERIFICATION TEST")
print("=" * 60)
print()
print("Testing that calculator results are correctly matched by type")
print("Expected: ROIC != owner_earnings")
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Warm cache
print("Warming cache for AOS...")
agent._warm_cache_for_synthesis("AOS", current_year=2024)
print()

# Get metrics from cache
print("=" * 60)
print("EXTRACTING METRICS")
print("=" * 60)
print()

metrics_dict = agent._extract_metrics_from_cache("AOS", 2024)

if metrics_dict:
    roic = metrics_dict.get('roic')
    owner_earnings = metrics_dict.get('owner_earnings')

    print(f"ROIC: {roic}")
    if roic is not None:
        if isinstance(roic, (int, float)):
            if roic < 1:  # Decimal format
                print(f"  Format: Decimal (percentage)")
                print(f"  Value: {roic * 100:.2f}%")
            else:  # Dollar amount (BUG)
                print(f"  Format: Dollar amount (BUG!)")
                print(f"  Value: ${roic:,.0f}")
    print()

    print(f"Owner Earnings: {owner_earnings}")
    if owner_earnings is not None:
        if isinstance(owner_earnings, (int, float)):
            print(f"  Value: ${owner_earnings:,.0f}")
    print()

    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)
    print()

    # Bug #12: Calculator assigned owner_earnings value to ROIC
    # After fix: ROIC should be percentage (0.05-0.50), owner_earnings should be $ amount (millions)
    if roic is not None and owner_earnings is not None:
        if roic == owner_earnings:
            print("[FAIL] Bug #12 NOT FIXED: ROIC == owner_earnings")
            print(f"  Both have value: {roic}")
        elif roic > 1000 and owner_earnings > 1000:
            print("[FAIL] Bug #12 NOT FIXED: ROIC is dollar amount like owner_earnings")
            print(f"  ROIC: ${roic:,.0f}")
            print(f"  Owner Earnings: ${owner_earnings:,.0f}")
        elif 0.05 <= roic <= 0.50 and owner_earnings > 100:
            print("[SUCCESS] Bug #12 FIXED!")
            print(f"  ROIC: {roic * 100:.2f}% (percentage format)")
            print(f"  Owner Earnings: ${owner_earnings:,.0f} (dollar amount)")
        else:
            print(f"[WARN] Unexpected values")
            print(f"  ROIC: {roic}")
            print(f"  Owner Earnings: {owner_earnings}")
    elif roic is None:
        print("[INFO] ROIC is None - calculator may not have calculated ROIC")
    else:
        print("[INFO] Owner Earnings is None - calculator may not have calculated it")
else:
    print("[FAIL] Failed to extract metrics from cache")

print()
print("=" * 60)
