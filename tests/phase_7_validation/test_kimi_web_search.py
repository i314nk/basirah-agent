"""
Test Kimi official $web_search builtin function.

This tests whether the Kimi API accepts the official $web_search builtin function
as documented at: https://platform.moonshot.ai/docs/guide/use-web-search
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_kimi_web_search():
    """Test Kimi $web_search with official format from documentation."""
    print("\n" + "=" * 70)
    print("Testing Kimi Official $web_search Builtin Function")
    print("=" * 70)

    # Get API key
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("[ERROR] KIMI_API_KEY not found in environment")
        return False

    # Create client
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1",
    )

    # Define tools exactly as shown in official documentation
    tools = [
        {
            "type": "builtin_function",  # Official Kimi builtin function type
            "function": {
                "name": "$web_search"  # Official name with $ prefix
            }
        }
    ]

    print("\nTool definition:")
    print(json.dumps(tools, indent=2))

    print("\nSending request to Kimi API...")
    print("Model: kimi-k2-thinking")
    print("Message: 'Search for Novo Nordisk CEO change 2025'")

    try:
        # Make API call
        completion = client.chat.completions.create(
            model="kimi-k2-thinking",
            messages=[
                {
                    "role": "system",
                    "content": "You are Kimi, an AI assistant. You can search the web when needed."
                },
                {
                    "role": "user",
                    "content": "Search for Novo Nordisk CEO change 2025"
                }
            ],
            temperature=0.6,
            tools=tools,
        )

        print("\n[SUCCESS] API call succeeded!")
        print(f"Finish reason: {completion.choices[0].finish_reason}")
        print(f"Message: {completion.choices[0].message.model_dump_json(indent=2)[:500]}...")

        return True

    except Exception as e:
        print(f"\n[FAILED] API call failed!")
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")

        # Check if it's the function name validation error
        if "function name is invalid" in str(e).lower():
            print("\n[ANALYSIS] This is the function name validation error.")
            print("The API is rejecting the $ prefix in function names.")
            print("This contradicts the official documentation.")
        else:
            print(f"\n[ANALYSIS] Different error than expected.")

        return False


if __name__ == "__main__":
    print("\nKimi $web_search Builtin Function Test")
    print("Reference: https://platform.moonshot.ai/docs/guide/use-web-search")

    success = test_kimi_web_search()

    if success:
        print("\n" + "=" * 70)
        print("[RESULT] Kimi $web_search is working!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("[RESULT] Kimi $web_search test failed")
        print("=" * 70)
        sys.exit(1)
