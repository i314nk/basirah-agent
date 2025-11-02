"""
Basic Usage Example - Warren Buffett AI Agent

This example demonstrates the simplest way to use the Warren Buffett AI Agent
to analyze a company.

Prerequisites:
- Set ANTHROPIC_API_KEY environment variable
- Set GURUFOCUS_API_KEY environment variable
- Set BRAVE_API_KEY environment variable

Run:
    python examples/basic_analysis.py
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
    Basic example: Analyze Apple (AAPL) using Warren Buffett AI.
    """

    print("=" * 80)
    print("Warren Buffett AI Agent - Basic Analysis Example")
    print("=" * 80)
    print()

    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key:")
        print("  export ANTHROPIC_API_KEY='your_key_here'  # Linux/Mac")
        print("  set ANTHROPIC_API_KEY=your_key_here       # Windows")
        return

    # Initialize agent
    print("Initializing Warren Buffett AI Agent...")
    agent = WarrenBuffettAgent()
    print("✓ Agent initialized with 4 tools ready")
    print()

    # Analyze a company
    ticker = "AAPL"  # Apple Inc.
    print(f"Analyzing {ticker}...")
    print("This will take 2-5 minutes as the agent:")
    print("  1. Screens financial metrics")
    print("  2. Reads complete 10-K annual reports")
    print("  3. Assesses competitive advantages")
    print("  4. Evaluates management quality")
    print("  5. Calculates intrinsic value")
    print("  6. Makes investment decision")
    print()

    # Perform analysis
    result = agent.analyze_company(
        ticker=ticker,
        deep_dive=True  # Full Buffett-style analysis
    )

    # Display results
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print(f"Company: {result['ticker']}")
    print(f"Decision: {result['decision']}")
    print(f"Conviction: {result['conviction']}")
    print()

    if result.get('intrinsic_value'):
        print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
    if result.get('current_price'):
        print(f"Current Price: ${result['current_price']:.2f}")
    if result.get('margin_of_safety'):
        print(f"Margin of Safety: {result['margin_of_safety']*100:.1f}%")

    print()
    print("Full Investment Thesis:")
    print("-" * 80)
    print(result['thesis'][:1000] + "..." if len(result['thesis']) > 1000 else result['thesis'])
    print()

    # Metadata
    print("Analysis Metadata:")
    print(f"  - Tool calls made: {result['metadata']['tool_calls_made']}")
    print(f"  - Duration: {result['metadata']['analysis_duration_seconds']:.1f} seconds")
    print()


if __name__ == "__main__":
    main()
