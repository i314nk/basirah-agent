"""
Test to investigate incomplete analysis issue (Issue #2)
Check if synthesis stage generates all 10 sections
"""
import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 80)
print("INCOMPLETE ANALYSIS INVESTIGATION (Issue #2)")
print("=" * 80)
print()

# Initialize agent with validation disabled for faster testing
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)

# Run a simple analysis
print("Running analysis for AOS (A. O. Smith Corporation)...")
print("This will take a few minutes...")
print()

result = agent.analyze("AOS")

print("=" * 80)
print("ANALYSIS STRUCTURE CHECK")
print("=" * 80)
print()

# Check if analysis succeeded
if result and result.get("final_recommendation"):
    final_rec = result["final_recommendation"]

    # Check what keys are in final_recommendation
    print("Final recommendation keys:")
    for key in final_rec.keys():
        print(f"  - {key}")
    print()

    # Get the full analysis text
    full_analysis = final_rec.get("full_analysis", "")

    print(f"Full analysis length: {len(full_analysis)} characters")
    print(f"Full analysis word count: {len(full_analysis.split())} words")
    print()

    # Check for expected sections
    expected_sections = [
        "Business Overview",
        "Economic Moat",
        "Competitive Advantages",
        "Management Quality",
        "Financial Health",
        "Valuation",
        "Risks",
        "Investment Decision",
        "Margin of Safety",
        "Long-term Prospects"
    ]

    print("Checking for expected sections:")
    sections_found = []
    sections_missing = []

    for section in expected_sections:
        if section.lower() in full_analysis.lower():
            sections_found.append(section)
            print(f"  ✓ {section} - FOUND")
        else:
            sections_missing.append(section)
            print(f"  ✗ {section} - MISSING")
    print()

    print(f"Sections found: {len(sections_found)}/{len(expected_sections)}")
    print()

    # Check if analysis ends abruptly
    last_200_chars = full_analysis[-200:] if len(full_analysis) > 200 else full_analysis
    print("Last 200 characters of analysis:")
    print("-" * 80)
    print(last_200_chars)
    print("-" * 80)
    print()

    # Check for truncation markers
    if full_analysis.endswith("...") or full_analysis.endswith("[TRUNCATED]"):
        print("[WARNING] Analysis appears to be truncated")
    else:
        print("[OK] Analysis does not appear to be truncated")
    print()

    # Validation
    if len(sections_missing) == 0:
        print("=" * 80)
        print("[SUCCESS] All sections present - no incomplete analysis issue")
        print("=" * 80)
    else:
        print("=" * 80)
        print(f"[ISSUE CONFIRMED] Missing {len(sections_missing)} sections")
        print("Missing sections:")
        for section in sections_missing:
            print(f"  - {section}")
        print()
        print("This confirms Issue #2: Incomplete analysis")
        print("=" * 80)

    # Show first 500 characters to see what IS generated
    print()
    print("First 500 characters of analysis:")
    print("-" * 80)
    print(full_analysis[:500])
    print("-" * 80)

else:
    print("[FAIL] Analysis did not complete successfully")
    print(f"Result keys: {list(result.keys()) if result else 'None'}")

print()
print("=" * 80)
