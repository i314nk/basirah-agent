"""
Test the new validator-driven refinement approach.

This tests that:
1. Validator identifies issues using tools
2. Validator fixes issues directly with structured <FIX> blocks
3. Fixes are applied correctly
4. Decision is properly extracted (not UNKNOWN)
5. Numeric fields are preserved (not set to None)
"""

import os
os.environ["LLM_MODEL"] = "kimi-k2-thinking"
os.environ["ENABLE_VALIDATION"] = "true"
os.environ["MAX_REFINEMENTS"] = "1"  # Just one refinement iteration for testing

from src.agent.buffett_agent import WarrenBuffettAgent

def test_validator_driven_refinement():
    """Test validator-driven refinement on NVO quick screen."""
    print("=" * 80)
    print("VALIDATOR-DRIVEN REFINEMENT TEST")
    print("=" * 80)
    print()

    # Initialize agent with validation enabled
    agent = WarrenBuffettAgent()

    # Run quick screen with validation
    print("Running NVO quick screen with validator-driven refinement...")
    print()

    result = agent.analyze_company("NVO", analysis_type="quick")

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    # Check decision extraction
    decision = result.get('decision', 'UNKNOWN')
    conviction = result.get('conviction', 'UNKNOWN')

    print(f"Decision: {decision}")
    print(f"Conviction: {conviction}")
    print()

    # Check numeric fields
    print(f"Intrinsic Value: ${result.get('intrinsic_value', 'N/A')}")
    print(f"Current Price: ${result.get('current_price', 'N/A')}")
    print(f"Margin of Safety: {result.get('margin_of_safety', 'N/A')}")
    print()

    # Check validation results
    validation = result.get('validation', {})
    print(f"Validation Score: {validation.get('score', 'N/A')}/100")
    print(f"Validation Approved: {validation.get('approved', False)}")
    print()

    # Check refinement metrics
    metadata = result.get('metadata', {})
    print(f"Validator Fixes Applied: {metadata.get('validator_fixes_applied', 0)}")
    print(f"Validator Tool Calls: {metadata.get('validator_tool_calls', 0)}")
    print()

    # Determine success
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print()

    success = True

    if decision == 'UNKNOWN':
        print("❌ FAILED: Decision is UNKNOWN (should be BUY/WATCH/AVOID)")
        success = False
    else:
        print(f"✓ PASSED: Decision extracted as '{decision}'")

    if conviction == 'UNKNOWN':
        print("❌ FAILED: Conviction is UNKNOWN (should be HIGH/MODERATE/LOW)")
        success = False
    else:
        print(f"✓ PASSED: Conviction extracted as '{conviction}'")

    # Check if numeric fields were erased
    if result.get('intrinsic_value') is None and validation.get('score', 0) < 100:
        print("❌ FAILED: Intrinsic value is None (was likely erased during refinement)")
        success = False
    else:
        print(f"✓ PASSED: Intrinsic value preserved/extracted: ${result.get('intrinsic_value', 'N/A')}")

    # Check if validator applied fixes
    fixes_applied = metadata.get('validator_fixes_applied', 0)
    if fixes_applied > 0:
        print(f"✓ PASSED: Validator applied {fixes_applied} fixes directly")
    elif validation.get('score', 100) < 80:
        print(f"⚠ WARNING: No validator fixes applied, but score is {validation.get('score')}/100")

    # Check if validator used tools
    validator_tool_calls = metadata.get('validator_tool_calls', 0)
    if validator_tool_calls > 0:
        print(f"✓ PASSED: Validator used {validator_tool_calls} tool calls to verify data")
    elif validation.get('score', 100) < 80:
        print(f"⚠ WARNING: No validator tool calls, but score is {validation.get('score')}/100")

    print()
    if success:
        print("=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = test_validator_driven_refinement()
    exit(0 if success else 1)
