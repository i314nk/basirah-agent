"""
Quick test to verify metrics extraction fix.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 80)
print("METRICS EXTRACTION FIX VERIFICATION")
print("=" * 80)
print()

print("Step 1: Initialize agent...")
agent = WarrenBuffettAgent(
    model_key="kimi-k2-thinking",
    enable_validation=False
)
print("[OK] Agent initialized")
print()

print("Step 2: Run analysis (2 years for speed)...")
print("   This will take ~2 minutes...")
print()

result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=2)

print()
print("Step 3: Check metrics extraction...")
if 'structured_metrics' in result['metadata']:
    structured_metrics = result['metadata']['structured_metrics']

    # Check current year
    current_metrics = structured_metrics['current_year']['metrics']
    current_non_null = sum(1 for v in current_metrics.values() if v is not None)

    print(f"[RESULT] Current year (2024): {current_non_null} non-null metrics")

    # Check prior years
    total_non_null = current_non_null
    for prior_year in structured_metrics['prior_years']:
        metrics = prior_year['metrics']
        non_null = sum(1 for v in metrics.values() if v is not None)
        total_non_null += non_null
        print(f"[RESULT] Year {prior_year['year']}: {non_null} non-null metrics")

    print()
    print(f"[RESULT] Total non-null metrics across all years: {total_non_null}")
    print()

    if total_non_null > 0:
        print("=" * 80)
        print("SUCCESS! Metrics extraction is now working!")
        print("=" * 80)
        print()
        print("Sample metrics from current year:")
        for key, value in list(current_metrics.items())[:10]:
            if value is not None:
                print(f"  {key}: {value}")
    else:
        print("=" * 80)
        print("WARNING: Still 0 metrics extracted")
        print("=" * 80)
else:
    print("[ERROR] structured_metrics not found in metadata")

print()
print("Test complete!")
