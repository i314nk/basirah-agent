"""
Test section name extraction for standardized refinement merging.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.agent.buffett_agent import WarrenBuffettAgent


def test_section_extraction():
    """Test extracting section names from investment thesis."""
    print("\n" + "=" * 70)
    print("Testing Section Name Extraction")
    print("=" * 70)

    # Sample thesis with various section formats
    sample_thesis = """
## Business Overview

Novo Nordisk A/S is a global pharmaceutical company...

**Economic Moat**

The company has a wide economic moat based on:
- Patent protection
- Brand strength

## Financial Analysis

Revenue has grown consistently...

**Current Leadership:**
- CEO: Lars Jørgensen
- CFO: Karsten Munk Knudsen

## Management Quality

Management has demonstrated...

**Valuation:**

Using DCF analysis...
"""

    # Create agent instance (just to access the method)
    agent = WarrenBuffettAgent(model_key="kimi-k2-thinking")

    # Extract section names
    section_names = agent._extract_section_names(sample_thesis)

    print(f"\nExtracted {len(section_names)} section names:")
    for i, name in enumerate(section_names, 1):
        print(f"  {i}. {name}")

    # Verify expected sections are found
    expected = [
        "Business Overview",
        "Economic Moat",
        "Financial Analysis",
        "Current Leadership",
        "Management Quality",
        "Valuation"
    ]

    print("\nVerification:")
    success = True
    for expected_name in expected:
        if expected_name in section_names:
            print(f"  [OK] Found: {expected_name}")
        else:
            print(f"  [FAIL] Missing: {expected_name}")
            success = False

    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] Section extraction working correctly!")
        return 0
    else:
        print("[FAILED] Some sections were not extracted")
        return 1


if __name__ == "__main__":
    sys.exit(test_section_extraction())
