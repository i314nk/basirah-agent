"""
Quick test to verify historical metrics extraction fix
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 60)
print("HISTORICAL METRICS EXTRACTION - QUICK TEST")
print("=" * 60)
print()

# Initialize agent
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)
print("[OK] Agent initialized")
print()

# Warm cache
print("Warming cache for AOS...")
agent._warm_cache_for_synthesis("AOS", current_year=2024)
print()

print("=" * 60)
print("TESTING HISTORICAL YEAR DETECTION")
print("=" * 60)
print()

# Test extracting metrics for different years
test_years = [2024, 2023, 2022]
results = {}

for year in test_years:
    print(f"Extracting metrics for year {year}:")
    metrics_dict = agent._extract_metrics_from_cache("AOS", year)

    if metrics_dict:
        revenue = metrics_dict.get('revenue')
        net_income = metrics_dict.get('net_income')
        results[year] = revenue
        print(f"  Revenue: ${revenue:.1f}M" if revenue else "  Revenue: N/A")
        print(f"  Net Income: ${net_income:.1f}M" if net_income else "  Net Income: N/A")
    else:
        results[year] = None
        print(f"  No metrics extracted")
    print()

print("=" * 60)
print("VALIDATION")
print("=" * 60)
print()

# Check for unique values
unique_revenues = set([v for v in results.values() if v is not None])
print(f"Unique revenue values found: {len(unique_revenues)}")
print(f"Total years analyzed: {len(results)}")
print()

if len(unique_revenues) >= 2:
    print("[SUCCESS] Historical metrics extraction is WORKING!")
    print(f"Found {len(unique_revenues)} different revenue values across {len(results)} years")
    print()
    print("Each year is extracting different historical data as expected.")
elif len(unique_revenues) == 1:
    print("[FAIL] All years show IDENTICAL revenue")
    print(f"All years have: ${list(unique_revenues)[0]:.1f}M")
    print()
    print("Historical extraction is NOT working - all years using current year data.")
else:
    print("[FAIL] No revenue data extracted for any year")
    print()
    print("Metrics extraction failed completely.")
print()
