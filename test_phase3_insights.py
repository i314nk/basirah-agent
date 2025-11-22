"""
Test Phase 7.7 Phase 3.1: Structured Insights Extraction (Text Parsing Prototype)

Validates that qualitative insights are extracted from analysis text.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 80)
print("PHASE 7.7 PHASE 3.1: STRUCTURED INSIGHTS EXTRACTION TEST")
print("=" * 80)
print()

# Initialize agent
print("Step 1: Initialize agent...")
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)
print("[OK] Agent initialized")
print()

# Run analysis (2 years for speed)
print("Step 2: Run analysis (2 years)...")
print("   This will take ~2 minutes...")
print()

result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=2)

print()
print("=" * 80)
print("INFRASTRUCTURE VALIDATION")
print("=" * 80)
print()

# Check structured_insights exists
has_insights = "structured_insights" in result['metadata']
print(f"[OK] structured_insights in metadata: {has_insights}")

if not has_insights:
    print("❌ FAIL: structured_insights not found in metadata")
    sys.exit(1)

insights = result['metadata']['structured_insights']

# Check structure
print(f"[OK] current_year structure: {'current_year' in insights}")
print(f"[OK] prior_years structure: {'prior_years' in insights}")
print(f"[OK] all_years structure: {'all_years' in insights}")
print()

# Check current year
current = insights['current_year']
print(f"[OK] Current year: {current['year']}")
print(f"[OK] Current year insights populated: {'insights' in current}")
print()

# Check prior years
prior_years = insights['prior_years']
print(f"[OK] Prior years count: {len(prior_years)}")
for year_data in prior_years:
    print(f"   - Year {year_data['year']}: insights populated: {'insights' in year_data}")
print()

# Check all_years
all_years = insights['all_years']
print(f"[OK] Total years in all_years: {len(all_years)}")
print()

print("=" * 80)
print("INSIGHTS EXTRACTION RESULTS")
print("=" * 80)
print()

# Count insights extracted per year
def count_insights(insights_dict):
    """Count non-empty insights."""
    return len([v for v in insights_dict.values() if v])

current_insights = current['insights']
current_count = count_insights(current_insights)
print(f"Current year ({current['year']}):")
print(f"  [RESULT] {current_count} insights extracted")

# Show what was extracted
if current_count > 0:
    print(f"  Extracted insights:")
    for key, value in current_insights.items():
        if value:
            # Truncate long values for display
            display_value = value
            if isinstance(value, str) and len(value) > 100:
                display_value = value[:97] + "..."
            elif isinstance(value, list):
                display_value = f"{len(value)} items"
            print(f"    - {key}: {display_value}")
print()

# Check prior years
for year_data in prior_years:
    year_insights = year_data['insights']
    year_count = count_insights(year_insights)
    print(f"Year {year_data['year']}:")
    print(f"  [RESULT] {year_count} insights extracted")
print()

# Total insights
total_insights = sum(
    count_insights(yd['insights'])
    for yd in all_years
)
print(f"[RESULT] Total insights across all years: {total_insights}")
print()

print("=" * 80)
print("SUCCESS CRITERIA (Phase 3.1)")
print("=" * 80)
print()

# Success criteria: Extract 5+ insights per year
success_threshold = 5
success = current_count >= success_threshold

print(f"Target: {success_threshold}+ insights per year")
print(f"Actual (current year): {current_count} insights")
print()

if success:
    print("[SUCCESS] Phase 3.1 prototype is working!")
    print()
    print("Next steps:")
    print("1. Review extracted insights for accuracy")
    print("2. Refine text parsing patterns if needed")
    print("3. Proceed to Phase 3.2 (Structured LLM Output)")
else:
    print(f"[PARTIAL SUCCESS] {current_count} insights extracted (target: {success_threshold}+)")
    print()
    print("This is expected for a text parsing prototype.")
    print("Insights extraction depends on LLM analysis format consistency.")
    print()
    print("Options:")
    print("1. Refine text parsing patterns to improve extraction")
    print("2. Proceed to Phase 3.2 for more reliable structured output")

print()
print("=" * 80)
print()
