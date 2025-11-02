"""
Compare Competitors Example - Warren Buffett AI Agent

This example demonstrates comparing multiple competitors side-by-side
to choose the best investment opportunity.

The agent will analyze each company and then provide a comparative
analysis in Warren Buffett's voice.

Run:
    python examples/compare_competitors.py
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
    Compare competitors example: Tech giants comparison.
    """

    print("=" * 80)
    print("Warren Buffett AI Agent - Compare Competitors Example")
    print("=" * 80)
    print()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        return

    # Initialize agent
    agent = WarrenBuffettAgent()
    print("✓ Agent initialized")
    print()

    # Competitors to compare
    competitors = [
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "GOOGL"  # Alphabet (Google)
    ]

    print(f"Comparing {len(competitors)} tech giants:")
    for ticker in competitors:
        print(f"  - {ticker}")
    print()
    print("This will:")
    print("  1. Analyze each company individually (deep dive)")
    print("  2. Compare their moats, management, financials, and valuations")
    print("  3. Recommend which (if any) to invest in")
    print()
    print("This will take 10-20 minutes for complete analysis...")
    print()

    # Perform comparison
    result = agent.compare_companies(competitors)

    # Display individual analyses
    print("\n" + "=" * 80)
    print("INDIVIDUAL ANALYSES")
    print("=" * 80)
    print()

    for company in result['companies']:
        print(f"\n{company['ticker']}:")
        print(f"  Decision: {company['decision']}")
        print(f"  Conviction: {company.get('conviction', 'N/A')}")
        if company.get('intrinsic_value'):
            print(f"  Intrinsic Value: ${company['intrinsic_value']:.2f}")
        if company.get('margin_of_safety'):
            print(f"  Margin of Safety: {company['margin_of_safety']*100:.1f}%")

    # Display comparative analysis
    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS (Warren Buffett)")
    print("=" * 80)
    print()
    print(result['comparison'])
    print()

    # Display recommendation
    print("\n" + "=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)
    print()

    if result['recommendation'] == "NONE":
        print("Warren Buffett recommends: NONE")
        print("None of these companies meet the criteria at current valuations.")
    elif result['recommendation'] == "UNCLEAR":
        print("Recommendation: UNCLEAR (review full analysis)")
    else:
        print(f"Warren Buffett recommends: {result['recommendation']}")
        print(f"This is the best investment opportunity among the compared companies.")

    print()


if __name__ == "__main__":
    main()
