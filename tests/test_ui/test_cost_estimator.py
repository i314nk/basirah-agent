"""
Quick test of the CostEstimator functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.ui.cost_estimator import CostEstimator
from src.agent.buffett_agent import WarrenBuffettAgent
from src.agent.sharia_screener import ShariaScreener

# Load environment variables
load_dotenv()

def test_quick_screen_estimate():
    """Test Quick Screen cost estimation"""
    print("\n" + "="*60)
    print("Testing Quick Screen Cost Estimation")
    print("="*60)

    estimator = CostEstimator()
    agent = WarrenBuffettAgent()

    ticker = "AAPL"
    print(f"\nEstimating cost for Quick Screen: {ticker}")

    result = estimator.estimate_quick_screen_cost(ticker, agent)

    if result['success']:
        print(f"SUCCESS!")
        print(f"   Input Tokens: {result['input_tokens']:,}")
        print(f"   Estimated Output Tokens: {result['estimated_output_tokens']:,}")
        print(f"   Total Cost: ${result['total_estimated_cost']:.2f}")
        print(f"   Range: ${result['min_cost']:.2f} - ${result['max_cost']:.2f}")
        print(f"   Confidence: {result['confidence']}")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        print(f"   Fallback estimate: ${result['total_estimated_cost']:.2f}")

def test_deep_dive_estimate():
    """Test Deep Dive cost estimation"""
    print("\n" + "="*60)
    print("Testing Deep Dive Cost Estimation")
    print("="*60)

    estimator = CostEstimator()
    agent = WarrenBuffettAgent()

    ticker = "AAPL"
    years = 3
    print(f"\nEstimating cost for Deep Dive: {ticker} ({years} years)")

    result = estimator.estimate_deep_dive_cost(ticker, years, agent)

    if result['success']:
        print(f"SUCCESS!")
        print(f"   Input Tokens: {result['input_tokens']:,}")
        print(f"   Estimated Output Tokens: {result['estimated_output_tokens']:,}")
        print(f"   Total Cost: ${result['total_estimated_cost']:.2f}")
        print(f"   Range: ${result['min_cost']:.2f} - ${result['max_cost']:.2f}")
        print(f"   Confidence: {result['confidence']}")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        print(f"   Fallback estimate: ${result['total_estimated_cost']:.2f}")

def test_sharia_screen_estimate():
    """Test Sharia Screen cost estimation"""
    print("\n" + "="*60)
    print("Testing Sharia Screen Cost Estimation")
    print("="*60)

    estimator = CostEstimator()
    screener = ShariaScreener()

    ticker = "AAPL"
    print(f"\nEstimating cost for Sharia Screen: {ticker}")

    result = estimator.estimate_sharia_screen_cost(ticker, screener)

    if result['success']:
        print(f"SUCCESS!")
        print(f"   Input Tokens: {result['input_tokens']:,}")
        print(f"   Estimated Output Tokens: {result['estimated_output_tokens']:,}")
        print(f"   Total Cost: ${result['total_estimated_cost']:.2f}")
        print(f"   Range: ${result['min_cost']:.2f} - ${result['max_cost']:.2f}")
        print(f"   Confidence: {result['confidence']}")
    else:
        print(f"FAILED: {result.get('error', 'Unknown error')}")
        print(f"   Fallback estimate: ${result['total_estimated_cost']:.2f}")

if __name__ == "__main__":
    print("\nTesting Cost Estimator")
    print("This will use the Anthropic token counting API to estimate costs")

    try:
        # Test all three analysis types
        test_quick_screen_estimate()
        test_deep_dive_estimate()
        test_sharia_screen_estimate()

        print("\n" + "="*60)
        print("All tests complete!")
        print("="*60)

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
