"""
Test 20-F automatic fallback for foreign companies.

This tests that when requesting a 10-K for a foreign company like TSM,
the tool automatically falls back to 20-F.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.tools.sec_filing_tool import SECFilingTool
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_20f_fallback():
    """Test that requesting 10-K for TSM automatically falls back to 20-F."""
    print("=" * 80)
    print("TESTING 20-F AUTOMATIC FALLBACK")
    print("=" * 80)

    print("\n1. Testing TSM (Taiwan Semiconductor) - Foreign company that files 20-F")
    print("   Requesting 10-K (should auto-fall back to 20-F)...")

    tool = SECFilingTool()

    result = tool.execute(
        ticker="TSM",
        filing_type="10-K",  # Requesting 10-K
        section="business"
    )

    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)

    if result['success']:
        print("\n[SUCCESS] Tool successfully retrieved filing!")
        data = result.get('data', '')
        if isinstance(data, str):
            print(f"\nData preview (first 500 chars):")
            print(data[:500])
            print("\n...")

        # Check if it mentions 20-F in the data
        if '20-F' in str(result):
            print("\n[CONFIRMED] Tool automatically fell back to 20-F for foreign company TSM")
        else:
            print("\n[INFO] Filing retrieved successfully")

    else:
        print(f"\n[FAILED] {result.get('error', 'Unknown error')}")
        print("\nExpected: Tool should automatically try 20-F when 10-K not found")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    return result

if __name__ == "__main__":
    try:
        result = test_20f_fallback()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
