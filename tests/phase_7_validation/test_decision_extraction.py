"""
Test decision extraction from analysis output.
Tests that decision is properly extracted from thesis and not set to UNKNOWN.
"""

import os
os.environ["LLM_MODEL"] = "kimi-k2-thinking"
os.environ["ENABLE_VALIDATION"] = "false"  # Disable validation for quick test

from src.agent.buffett_agent import WarrenBuffettAgent

def test_decision_extraction():
    """Test that decision is extracted correctly from analysis."""
    print("=" * 80)
    print("DECISION EXTRACTION TEST")
    print("=" * 80)
    print()

    # Initialize agent
    agent = WarrenBuffettAgent()

    # Run quick screen (no validation)
    print("Running NVO quick screen...")
    result = agent.analyze_company("NVO", analysis_type="quick")

    print()
    print("-" * 80)
    print(f"Decision: {result.get('decision', 'N/A')}")
    print(f"Conviction: {result.get('conviction', 'N/A')}")
    print(f"Intrinsic Value: ${result.get('intrinsic_value', 'N/A')}")
    print(f"Current Price: ${result.get('current_price', 'N/A')}")
    print(f"Margin of Safety: {result.get('margin_of_safety', 'N/A')}")
    print("-" * 80)
    print()

    # Check if decision is UNKNOWN
    decision = result.get('decision', 'UNKNOWN')
    if decision == 'UNKNOWN':
        print("FAILED: Decision is UNKNOWN")
        print()
        print("Thesis preview (first 500 chars):")
        print(result.get('thesis', '')[:500])
        print()
        print("Thesis ending (last 500 chars):")
        print(result.get('thesis', '')[-500:])
        return False
    else:
        print(f"PASSED: Decision successfully extracted as '{decision}'")
        return True

if __name__ == "__main__":
    success = test_decision_extraction()
    exit(0 if success else 1)
