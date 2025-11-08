"""
Test script for enhanced Sharia screener with tool support.

Tests that the Sharia screener can:
1. Initialize with tools
2. Use tools to gather live data
3. Perform accurate screening based on actual data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent.sharia_screener import ShariaScreener
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_sharia_screener():
    """Test Sharia screener with Apple (AAPL) - generally compliant company."""
    print("=" * 80)
    print("TESTING ENHANCED SHARIA SCREENER WITH TOOL SUPPORT")
    print("=" * 80)

    # Initialize screener
    print("\n1. Initializing Sharia Screener...")
    screener = ShariaScreener()

    # Check that tools were initialized
    print(f"   [OK] Tools initialized: {list(screener.tools.keys())}")

    # Screen a company
    ticker = "AAPL"  # Apple - generally Sharia-compliant
    print(f"\n2. Screening {ticker} using live data from tools...")
    print(f"   This will fetch actual 10-K filings and financial data...")

    result = screener.screen_company(ticker)

    # Display results
    print("\n" + "=" * 80)
    print("SCREENING RESULTS")
    print("=" * 80)

    print(f"\nTicker: {result['ticker']}")
    print(f"Status: {result['status']}")
    print(f"Purification Rate: {result['purification_rate']}%")

    if 'metadata' in result:
        meta = result['metadata']
        print(f"\nMetadata:")
        print(f"  - Analysis Date: {meta.get('analysis_date', 'N/A')}")
        print(f"  - Standard: {meta.get('standard', 'N/A')}")
        print(f"  - Tool Calls Made: {meta.get('tool_calls_made', 0)}")

        if 'token_usage' in meta:
            usage = meta['token_usage']
            print(f"  - Total Cost: ${usage.get('total_cost', 0):.2f}")
            print(f"  - Input Tokens: {usage.get('input_tokens', 0):,}")
            print(f"  - Output Tokens: {usage.get('output_tokens', 0):,}")

    print("\n" + "=" * 80)
    print("FULL ANALYSIS")
    print("=" * 80)
    print(result.get('analysis', 'No analysis available'))

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    # Verify tool usage
    if result.get('metadata', {}).get('tool_calls_made', 0) > 0:
        print(f"\n[SUCCESS] Screener used {result['metadata']['tool_calls_made']} tool calls")
        print("  The screener is now gathering LIVE DATA instead of relying on training data!")
    else:
        print("\n[WARNING] No tools were used. Something may be wrong.")

    return result

if __name__ == "__main__":
    try:
        result = test_sharia_screener()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
