"""
Quick metadata tracking test - verifies tool_calls is captured correctly.
"""

import logging
from src.agent.buffett_agent import WarrenBuffettAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_quick():
    """Quick test of metadata tracking."""
    print("\n" + "="*80)
    print("QUICK METADATA TEST")
    print("="*80)

    agent = WarrenBuffettAgent(
        model_key="kimi-k2-thinking",
        enable_validation=False  # Disable validation to test faster
    )

    print("\nRunning NVO quick screen...")
    result = agent.analyze_company("NVO", deep_dive=False, years_to_analyze=1)

    # Check metadata
    metadata = result.get("metadata", {})
    tool_calls = metadata.get("tool_calls_made", 0)

    print("\n" + "-"*80)
    print(f"Tool calls tracked: {tool_calls}")
    print("-"*80)

    if tool_calls == 0:
        print("FAILED: Still showing 0 tool calls")
        print("   Metadata bug not fixed")
        return False
    else:
        print(f"PASSED: {tool_calls} tool calls tracked correctly")
        return True

if __name__ == "__main__":
    success = test_quick()
    exit(0 if success else 1)
