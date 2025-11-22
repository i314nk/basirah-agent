"""
Test Kimi tool conversion - verify builtin_function pass-through.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.llm.providers.kimi import KimiProvider


def test_tool_conversion():
    """Test that builtin_function tools pass through unchanged."""
    print("\n" + "=" * 70)
    print("Testing Kimi Tool Conversion")
    print("=" * 70)

    # Create provider instance
    provider = KimiProvider("kimi-k2-thinking")

    # Test tools (mixed standard and builtin)
    test_tools = [
        # Standard tool (Claude format)
        {
            "name": "calculator_tool",
            "description": "Perform calculations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                }
            }
        },
        # Kimi builtin function
        {
            "type": "builtin_function",
            "function": {
                "name": "$web_search"
            }
        },
        # Another standard tool
        {
            "name": "gurufocus_tool",
            "description": "Get financial data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"}
                }
            }
        }
    ]

    print(f"\nInput: {len(test_tools)} tools")
    print("  - calculator_tool (standard)")
    print("  - $web_search (builtin_function)")
    print("  - gurufocus_tool (standard)")

    # Convert tools
    converted = provider._convert_tools_to_openai_format(test_tools)

    print(f"\nOutput: {len(converted)} tools")

    # Verify results
    success = True

    # Tool 1: calculator_tool (should be converted to function)
    if converted[0]["type"] != "function":
        print(f"[FAIL] Tool 1 type: expected 'function', got '{converted[0]['type']}'")
        success = False
    elif converted[0]["function"]["name"] != "calculator_tool":
        print(f"[FAIL] Tool 1 name: expected 'calculator_tool', got '{converted[0]['function']['name']}'")
        success = False
    else:
        print("[OK] Tool 1: calculator_tool converted to function")

    # Tool 2: $web_search (should be passed through as builtin_function)
    if converted[1]["type"] != "builtin_function":
        print(f"[FAIL] Tool 2 type: expected 'builtin_function', got '{converted[1]['type']}'")
        success = False
    elif converted[1]["function"]["name"] != "$web_search":
        print(f"[FAIL] Tool 2 name: expected '$web_search', got '{converted[1]['function']['name']}'")
        success = False
    else:
        print("[OK] Tool 2: $web_search passed through as builtin_function")

    # Tool 3: gurufocus_tool (should be converted to function)
    if converted[2]["type"] != "function":
        print(f"[FAIL] Tool 3 type: expected 'function', got '{converted[2]['type']}'")
        success = False
    elif converted[2]["function"]["name"] != "gurufocus_tool":
        print(f"[FAIL] Tool 3 name: expected 'gurufocus_tool', got '{converted[2]['function']['name']}'")
        success = False
    else:
        print("[OK] Tool 3: gurufocus_tool converted to function")

    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] All tool conversions correct!")
        print("=" * 70)
        return 0
    else:
        print("[FAILED] Tool conversion has issues")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(test_tool_conversion())
