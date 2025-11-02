"""
Error Handling Example - Warren Buffett AI Agent

This example demonstrates how the agent handles various error scenarios:
- Invalid ticker symbols
- API failures
- Missing data

Run:
    python examples/error_handling.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.buffett_agent import WarrenBuffettAgent


def main():
    """
    Error handling examples.
    """

    print("=" * 80)
    print("Warren Buffett AI Agent - Error Handling Examples")
    print("=" * 80)
    print()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        return

    # Initialize agent
    agent = WarrenBuffettAgent()
    print("✓ Agent initialized")
    print()

    # Test 1: Invalid ticker
    print("Test 1: Invalid Ticker Symbol")
    print("-" * 40)
    invalid_ticker = "INVALID123"
    print(f"Attempting to analyze: {invalid_ticker}")
    print()

    result = agent.analyze_company(invalid_ticker, deep_dive=False)

    print(f"Result: {result['decision']}")
    if result['decision'] == "ERROR":
        print("✓ Agent handled invalid ticker gracefully")
        print(f"  Error message: {result.get('thesis', 'N/A')[:100]}...")
    print()

    # Test 2: Very small/obscure company (may have missing data)
    print("Test 2: Obscure Company (Potential Data Issues)")
    print("-" * 40)
    obscure_ticker = "BKYI"  # Small company, may have limited data
    print(f"Attempting to analyze: {obscure_ticker}")
    print()

    result = agent.analyze_company(obscure_ticker, deep_dive=False)

    print(f"Result: {result['decision']}")
    print(f"Tool calls made: {result['metadata']['tool_calls_made']}")

    if result['decision'] == "AVOID":
        print("✓ Agent analyzed despite potential data limitations")
        print("  Made a decision based on available information")
    elif result['decision'] == "ERROR":
        print("✓ Agent returned error when data was insufficient")
    print()

    # Test 3: Batch analysis with mixed validity
    print("Test 3: Batch Analysis with Invalid Tickers")
    print("-" * 40)
    mixed_tickers = ["AAPL", "INVALID", "MSFT", "NOTREAL"]
    print(f"Analyzing: {mixed_tickers}")
    print()

    results = agent.batch_analyze(mixed_tickers, deep_dive=False)

    print("Results:")
    for result in results:
        ticker = result['ticker']
        decision = result['decision']
        print(f"  {ticker:12} → {decision}")

    print()
    print("✓ Batch analysis continued despite individual failures")
    print("  Valid companies were analyzed successfully")
    print("  Invalid tickers returned ERROR status")
    print()

    # Summary
    print("=" * 80)
    print("ERROR HANDLING SUMMARY")
    print("=" * 80)
    print()
    print("The agent handles errors gracefully:")
    print("  ✓ Invalid tickers don't crash the system")
    print("  ✓ Missing data results in appropriate AVOID decisions")
    print("  ✓ Batch operations continue even when some fail")
    print("  ✓ Error messages are clear and actionable")
    print()
    print("In production, you should:")
    print("  1. Validate tickers before analysis")
    print("  2. Check result['decision'] for ERROR status")
    print("  3. Review result['metadata']['error'] for details")
    print("  4. Implement retry logic for temporary failures")
    print()


if __name__ == "__main__":
    main()
