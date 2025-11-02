"""
Outside Circle of Competence Example - Warren Buffett AI Agent

This example demonstrates the agent saying "I'll pass" when analyzing
a company outside Warren Buffett's circle of competence.

Warren Buffett is famously selective and comfortable admitting when
he doesn't understand a business. This example shows that behavior.

Run:
    python examples/outside_competence.py
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
    Circle of competence example: Analyze a biotech company.

    Warren Buffett typically avoids biotech because:
    - Complex drug development processes
    - Unpredictable regulatory outcomes
    - Difficult to forecast cash flows
    - Outside his expertise
    """

    print("=" * 80)
    print("Warren Buffett AI Agent - Circle of Competence Example")
    print("=" * 80)
    print()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        return

    # Initialize agent
    agent = WarrenBuffettAgent()
    print("✓ Agent initialized")
    print()

    # Analyze a biotech company
    ticker = "MRNA"  # Moderna (biotech)
    print(f"Analyzing {ticker} (Moderna - Biotechnology)")
    print()
    print("Moderna develops mRNA vaccines and therapeutics.")
    print("This is typically outside Warren Buffett's circle of competence.")
    print()
    print("Let's see if the agent recognizes this and passes...")
    print()

    # Perform analysis
    result = agent.analyze_company(ticker, deep_dive=True)

    # Display results
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print(f"Company: {result['ticker']}")
    print(f"Decision: {result['decision']}")
    print(f"Conviction: {result.get('conviction', 'N/A')}")
    print()

    print("Investment Thesis:")
    print("-" * 80)
    print(result['thesis'])
    print()

    # Analysis
    if result['decision'] == "AVOID":
        print("✓ As expected, Warren Buffett passed on this opportunity.")
        print("  The agent correctly identified this as outside the circle of competence.")
        print()
        print("Key takeaways:")
        print("  1. Warren Buffett doesn't invest in everything")
        print("  2. He's comfortable saying 'I don't understand this'")
        print("  3. Staying within your circle of competence is critical")
        print("  4. It's better to pass than to invest in something you don't understand")
    else:
        print(f"Note: Agent decided {result['decision']}")
        print("Review the reasoning in the thesis above.")

    print()


if __name__ == "__main__":
    main()
