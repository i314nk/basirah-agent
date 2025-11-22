"""
Test Multi-Year Historical Metrics Extraction

Validates that the BUGFIX for identical metrics across years is working.
Tests that each year has different metric values extracted from historical arrays.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 80)
print("MULTI-YEAR HISTORICAL METRICS EXTRACTION TEST")
print("=" * 80)
print()

# Initialize agent
print("Step 1: Initialize agent...")
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)
print("[OK] Agent initialized")
print()

# Run 3-year analysis
print("Step 2: Run 3-year deep dive analysis (AOS)...")
print("   This will take ~3-5 minutes...")
print()

result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=3)

print()
print("=" * 80)
print("MULTI-YEAR METRICS VALIDATION")
print("=" * 80)
print()

# Check structured_metrics exists
has_metrics = "structured_metrics" in result['metadata']
print(f"[OK] structured_metrics in metadata: {has_metrics}")

if not has_metrics:
    print("[FAIL] structured_metrics not found in metadata")
    sys.exit(1)

metrics = result['metadata']['structured_metrics']

# Get all years
all_years = metrics.get('all_years', [])
print(f"[OK] Years analyzed: {len(all_years)}")
print()

# Extract revenue for each year to check for duplicates
print("=" * 80)
print("HISTORICAL METRICS CHECK (Revenue)")
print("=" * 80)
print()

revenues = {}
for year_data in all_years:
    year = year_data.get('year')
    year_metrics = year_data.get('metrics', {})
    revenue = year_metrics.get('revenue')
    revenues[year] = revenue
    print(f"Year {year}: Revenue = ${revenue:.1f}M" if revenue else f"Year {year}: Revenue = None")

print()

# Check for duplicates
unique_revenues = set([v for v in revenues.values() if v is not None])
print(f"Unique revenue values: {len(unique_revenues)}")
print(f"Total years with revenue: {len([v for v in revenues.values() if v is not None])}")
print()

# Validation
if len(unique_revenues) == 0:
    print("[FAIL] No revenue data extracted for any year")
    sys.exit(1)
elif len(unique_revenues) == 1:
    print("[FAIL] All years show IDENTICAL revenue - historical extraction NOT working!")
    print(f"       All years have: ${list(unique_revenues)[0]:.1f}M")
    sys.exit(1)
elif len(unique_revenues) >= 2:
    print("[SUCCESS] Historical metrics extraction is WORKING!")
    print(f"          Found {len(unique_revenues)} different revenue values across {len(revenues)} years")

print()

# Check other metrics
print("=" * 80)
print("OTHER METRICS CHECK")
print("=" * 80)
print()

for year_data in all_years:
    year = year_data.get('year')
    year_metrics = year_data.get('metrics', {})

    print(f"\n{year}:")
    print(f"  Revenue: ${year_metrics.get('revenue', 'N/A'):.1f}M" if year_metrics.get('revenue') else f"  Revenue: N/A")
    print(f"  Net Income: ${year_metrics.get('net_income', 'N/A'):.1f}M" if year_metrics.get('net_income') else f"  Net Income: N/A")
    print(f"  Operating Income: ${year_metrics.get('operating_income', 'N/A'):.1f}M" if year_metrics.get('operating_income') else f"  Operating Income: N/A")
    print(f"  Free Cash Flow: ${year_metrics.get('free_cash_flow', 'N/A'):.1f}M" if year_metrics.get('free_cash_flow') else f"  Free Cash Flow: N/A")
    print(f"  ROIC: {year_metrics.get('roic', 'N/A')}" if year_metrics.get('roic') else f"  ROIC: N/A")
    print(f"  ROE: {year_metrics.get('roe', 'N/A')}" if year_metrics.get('roe') else f"  ROE: N/A")
    print(f"  Owner Earnings: ${year_metrics.get('owner_earnings', 'N/A'):.1f}M" if year_metrics.get('owner_earnings') else f"  Owner Earnings: N/A")

print()
print("=" * 80)
print("ROIC FIELD VALIDATION")
print("=" * 80)
print()

# Check if ROIC is a percentage or dollar amount (ISSUE #4)
current_year_metrics = all_years[0].get('metrics', {})
roic = current_year_metrics.get('roic')

if roic:
    print(f"Current year ROIC: {roic}")

    # ROIC should be a percentage (0-100), not millions
    if roic > 1000:
        print("[FAIL] ROIC appears to be a dollar amount (> 1000), not a percentage!")
        print(f"       This is likely Issue #4: ROIC field mapping error")
    elif roic > 100:
        print("[WARN] ROIC > 100% - unusual but possible for high-return businesses")
    else:
        print("[OK] ROIC is in percentage range (0-100%)")
else:
    print("[INFO] ROIC not available for current year")

print()
print("=" * 80)
print("JSON REMOVAL CHECK")
print("=" * 80)
print()

# Check if JSON block leaked into thesis
thesis = result.get('thesis', '')
if '<INSIGHTS>' in thesis:
    print("[FAIL] JSON block is still present in thesis!")
    print("       Issue #1 (JSON leaking) NOT fixed properly")
else:
    print("[OK] No JSON block found in thesis - properly removed")

print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print()

print(f"Years analyzed: {len(all_years)}")
print(f"Unique revenue values: {len(unique_revenues)}")
print(f"Historical extraction: {'✅ WORKING' if len(unique_revenues) >= 2 else '❌ BROKEN'}")
print(f"JSON removal: {'✅ WORKING' if '<INSIGHTS>' not in thesis else '❌ BROKEN'}")
print(f"ROIC field: {'✅ OK' if roic and roic < 1000 else '⚠️ ISSUE' if roic and roic > 1000 else 'ℹ️ N/A'}")

print()
print("=" * 80)
