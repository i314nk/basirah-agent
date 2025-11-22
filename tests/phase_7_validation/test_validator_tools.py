"""
Test validator tool filtering - verify it gets provider-native web search.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.agent.buffett_agent import WarrenBuffettAgent


def test_validator_tools():
    """Test that validator gets correct tools for each provider."""
    print("\n" + "=" * 70)
    print("Testing Validator Tool Access")
    print("=" * 70)

    # Test with Kimi
    print("\n--- Kimi K2 Thinking ---")
    agent_kimi = WarrenBuffettAgent(model_key="kimi-k2-thinking")

    all_tools_kimi = agent_kimi._get_tool_definitions()
    print(f"All tools: {len(all_tools_kimi)}")
    for tool in all_tools_kimi:
        tool_type = tool.get("type", "unknown")
        if tool_type == "builtin_function":
            tool_name = tool.get("function", {}).get("name", "unknown")
            print(f"  - {tool_name} (type: {tool_type})")
        else:
            tool_name = tool.get("name", "unknown")
            print(f"  - {tool_name} (type: {tool_type})")

    validator_tools_kimi = agent_kimi._get_validator_tool_definitions()
    print(f"\nValidator tools: {len(validator_tools_kimi)}")
    for tool in validator_tools_kimi:
        tool_type = tool.get("type", "unknown")
        if tool_type == "builtin_function":
            tool_name = tool.get("function", {}).get("name", "unknown")
            print(f"  - {tool_name} (type: {tool_type})")
        else:
            tool_name = tool.get("name", "unknown")
            print(f"  - {tool_name} (type: {tool_type})")

    # Check if web_search is included
    has_web_search = False
    for tool in validator_tools_kimi:
        if tool.get("type") == "builtin_function":
            if tool.get("function", {}).get("name") == "$web_search":
                has_web_search = True
                break
        elif "web_search" in tool.get("name", "").lower():
            has_web_search = True
            break

    if has_web_search:
        print("\n[OK] Kimi validator has web search access")
    else:
        print("\n[FAIL] Kimi validator MISSING web search access!")
        return 1

    print("\n" + "=" * 70)
    print("[SUCCESS] Validator has correct tool access")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(test_validator_tools())
