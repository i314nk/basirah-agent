"""
Test Phase 7.7 Phase 3.2: JSON-Based Insights Extraction

Validates that the LLM provides structured insights in JSON format,
and that our extraction logic correctly parses them.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 80)
print("PHASE 7.7 PHASE 3.2: JSON INSIGHTS EXTRACTION TEST")
print("=" * 80)
print()

# Initialize agent
print("Step 1: Initialize agent...")
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)
print("[OK] Agent initialized")
print()

# Run analysis (1 year for speed)
print("Step 2: Run quick analysis (1 year)...")
print("   This will take ~90 seconds...")
print()

result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=1)

print()
print("=" * 80)
print("PHASE 3.2 VALIDATION")
print("=" * 80)
print()

# Check structured_insights exists
has_insights = "structured_insights" in result['metadata']
print(f"[OK] structured_insights in metadata: {has_insights}")

if not has_insights:
    print("[FAIL] structured_insights not found in metadata")
    sys.exit(1)

insights = result['metadata']['structured_insights']
current = insights['current_year']
current_insights = current['insights']

# Count insights extracted
def count_insights(insights_dict):
    """Count non-empty insights."""
    return len([v for v in insights_dict.values() if v])

current_count = count_insights(current_insights)

print()
print("=" * 80)
print("EXTRACTION RESULTS")
print("=" * 80)
print()

print(f"Current year ({current['year']}): {current_count} insights extracted")
print()

# Show what was extracted
if current_count > 0:
    print("Extracted insights:")
    for key, value in current_insights.items():
        if value:
            # Truncate long values for display
            display_value = value
            if isinstance(value, str) and len(value) > 100:
                display_value = value[:97] + "..."
            elif isinstance(value, list):
                display_value = f"{len(value)} items: {value}"
            print(f"  - {key}: {display_value}")
print()

print("=" * 80)
print("PHASE 3.2 vs PHASE 3.1 COMPARISON")
print("=" * 80)
print()

# Phase 3.1 baseline: 4 insights
phase_3_1_baseline = 4
phase_3_2_target = 8  # Target: 8+ insights with JSON extraction

print(f"Phase 3.1 baseline (text parsing): {phase_3_1_baseline} insights")
print(f"Phase 3.2 actual (JSON extraction): {current_count} insights")
print(f"Phase 3.2 target: {phase_3_2_target}+ insights")
print()

improvement = current_count - phase_3_1_baseline
improvement_pct = (improvement / phase_3_1_baseline * 100) if phase_3_1_baseline > 0 else 0

print(f"Improvement: +{improvement} insights ({improvement_pct:+.0f}%)")
print()

print("=" * 80)
print("SUCCESS CRITERIA (Phase 3.2)")
print("=" * 80)
print()

success = current_count >= phase_3_2_target
meets_baseline = current_count >= phase_3_1_baseline

if success:
    print(f"[SUCCESS] Phase 3.2 working! Extracted {current_count}/{phase_3_2_target}+ insights")
    print()
    print("JSON extraction is functioning as expected.")
    print()
    print("Next steps:")
    print("1. Test with more companies to validate consistency")
    print("2. Measure extraction accuracy across diverse sectors")
    print("3. Refine prompts if needed based on failure modes")
elif meets_baseline:
    print(f"[PARTIAL SUCCESS] Extracted {current_count} insights (target: {phase_3_2_target}+)")
    print()
    print(f"Better than Phase 3.1 baseline ({phase_3_1_baseline}), but below target.")
    print()
    if current_count >= 6:
        print("This is acceptable. JSON extraction is working.")
        print("Prompt refinement may improve further.")
    else:
        print("Possible issues:")
        print("- LLM may not be following JSON format instructions")
        print("- Check if <INSIGHTS> block is present in analysis text")
        print("- May need to refine prompt clarity")
else:
    print(f"[NEEDS IMPROVEMENT] Extracted {current_count} insights (baseline: {phase_3_1_baseline})")
    print()
    print("JSON extraction may not be working. Falling back to text parsing.")
    print()
    print("Debugging steps:")
    print("1. Check if LLM provided <INSIGHTS> JSON block in output")
    print("2. Review extraction logs for JSON parsing errors")
    print("3. Verify prompt instructions are clear")

print()
print("=" * 80)
print()
