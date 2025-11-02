"""
Quick Screen Example - Warren Buffett AI Agent

This example demonstrates using the agent to quickly screen a company
without doing a full deep-dive analysis.

Useful for:
- Screening a watchlist
- Initial filtering before deep analysis
- Checking if a company meets basic criteria

Run:
    python examples/quick_screen.py
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
    Quick screen example: Screen multiple companies rapidly.
    """

    print("=" * 80)
    print("Warren Buffett AI Agent - Quick Screen Example")
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

    # Companies to screen
    watchlist = [
        "AAPL",  # Apple - tech
        "KO",    # Coca-Cola - consumer staples
        "JNJ",   # Johnson & Johnson - healthcare
        "BRK.B", # Berkshire Hathaway - diversified
        "WMT"    # Walmart - retail
    ]

    print(f"Quick screening {len(watchlist)} companies from watchlist...")
    print("This will check basic financial metrics without full analysis")
    print()

    # Quick screen each company
    results = agent.batch_analyze(
        tickers=watchlist,
        deep_dive=False  # Quick screen only
    )

    # Display summary
    print("\n" + "=" * 80)
    print("SCREENING RESULTS")
    print("=" * 80)
    print()

    buys = []
    watches = []
    avoids = []

    for result in results:
        decision = result['decision']

        if decision == "BUY":
            buys.append(result)
        elif decision == "WATCH":
            watches.append(result)
        elif decision == "AVOID":
            avoids.append(result)

        print(f"{result['ticker']:6} → {decision:6} (Conviction: {result.get('conviction', 'N/A')})")

    print()
    print("Summary:")
    print(f"  BUY candidates: {len(buys)}")
    print(f"  WATCH list: {len(watches)}")
    print(f"  AVOID: {len(avoids)}")
    print()

    if buys:
        print("✓ Recommended for deep-dive analysis:")
        for result in buys:
            print(f"    - {result['ticker']}")
    else:
        print("No strong BUY candidates found in this screen.")

    print()


if __name__ == "__main__":
    main()
