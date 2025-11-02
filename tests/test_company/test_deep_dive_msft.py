"""Test deep dive analysis on Microsoft (MSFT) with context management."""

import sys
import logging
from datetime import datetime
from src.agent.buffett_agent import WarrenBuffettAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def main():
    print("=" * 80)
    print("TESTING DEEP DIVE ANALYSIS: MICROSOFT (MSFT)")
    print("=" * 80)
    print()
    print("Ticker: MSFT (Microsoft Corporation)")
    print("Analysis Type: Deep Dive (multi-year with progressive summarization)")
    print()
    print("Expected cost: ~$2-5")
    print("Expected time: 3-5 minutes")
    print()
    input("Press ENTER to start the analysis (or Ctrl+C to cancel)...")

    print("Initializing Warren Buffett AI Agent...")
    agent = WarrenBuffettAgent()

    print("\nStarting deep dive analysis on MSFT...")
    print("=" * 80)
    print()

    start_time = datetime.now()

    try:
        # Run deep dive analysis
        result = agent.analyze_company("MSFT", deep_dive=True)

        duration = (datetime.now() - start_time).total_seconds()

        print()
        print("=" * 80)
        print("DEEP DIVE ANALYSIS COMPLETE - MICROSOFT")
        print("=" * 80)
        print()
        print(f"Ticker: {result['ticker']}")
        print(f"Decision: {result['decision']}")
        print(f"Conviction: {result['conviction']}")
        print()
        print(f"Intrinsic Value: ${result.get('intrinsic_value', 'N/A')}")
        print(f"Current Price: ${result.get('current_price', 'N/A')}")
        print(f"Margin of Safety: {result.get('margin_of_safety', 0) * 100:.1f}%")
        print()

        # Context management verification
        cm = result['metadata']['context_management']
        print("Context Management:")
        print(f"  Strategy: {cm.get('strategy', 'N/A')}")
        print(f"  Years Analyzed: {cm.get('years_analyzed', [])}")
        print(f"  Current Year Tokens: ~{cm.get('current_year_tokens', 0):,}")
        print(f"  Prior Years Tokens: ~{cm.get('prior_years_tokens', 0):,}")
        print(f"  Total Estimated Tokens: ~{cm.get('total_token_estimate', 0):,}")
        print()

        # Additional metadata if adaptive strategy used
        if cm.get('adaptive_used', False):
            print("  Adaptive Summarization Applied:")
            print(f"    Filing Size: {cm.get('filing_size', 0):,} characters")
            print(f"    Summary Size: {cm.get('summary_size', 0):,} characters")
            print(f"    Reduction: {cm.get('reduction_percent', 0):.1f}%")
            print()

        # Verify context limit compliance
        total_tokens = cm.get('total_token_estimate', 0)
        if total_tokens < 200000:
            print(f"  STATUS: PASS - Context within 200K limit")
        else:
            print(f"  STATUS: FAIL - Context exceeds 200K limit ({total_tokens:,} tokens)")
        print()

        print(f"Tool Calls: {result['metadata'].get('tool_calls_made', 0)}")
        print(f"Duration: {duration:.1f} seconds")
        print()

        # Show first 1000 chars of thesis
        print("-" * 80)
        print("INVESTMENT THESIS (First 1000 chars):")
        print("-" * 80)
        print(result['thesis'][:1000])
        print("...")
        print()

        # Save full result
        import json
        output_file = 'test_deep_dive_msft_result.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull result saved to: {output_file}")

        print("\nMICROSOFT TEST COMPLETE!")

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print()
        print("=" * 80)
        print("DEEP DIVE ANALYSIS FAILED - MICROSOFT")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print(f"Duration before failure: {duration:.1f} seconds")
        print()

        # Show traceback for debugging
        import traceback
        print("Traceback:")
        print(traceback.format_exc())

        sys.exit(1)

if __name__ == '__main__':
    main()
