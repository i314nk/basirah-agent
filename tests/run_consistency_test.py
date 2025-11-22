"""
Comprehensive consistency test for basīrah.

Tests 10 diverse companies, 5 runs each to verify <1% variance.
This test is CRITICAL before Phase 8 batch processing.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.buffett_agent import WarrenBuffettAgent
from src.validation import ConsistencyTester

def main():
    """Run comprehensive consistency test."""

    print("\n" + "="*80)
    print("BASĪRAH CONSISTENCY TEST - Phase 7.5 Quality Control")
    print("="*80)
    print("\nThis test verifies that analyses produce deterministic results.")
    print("Testing 10 diverse companies, 5 runs each.")
    print("Using 5-year deep dive analysis (cost-optimized).")
    print("\nEstimated time: ~90 minutes")
    print("Estimated cost: ~$150 (essential investment for quality assurance)")
    print("\n" + "="*80 + "\n")

    # Initialize
    print("Initializing Warren Buffett Agent...")
    agent = WarrenBuffettAgent()

    print("Initializing Consistency Tester (1% variance threshold)...")
    tester = ConsistencyTester(variance_threshold=0.01)  # 1% max variance

    # Test tickers (diverse set across sectors)
    TEST_TICKERS = [
        "FDS",   # Known problem case - Financial data services
        "AAPL",  # Large cap tech
        "MSFT",  # Large cap tech #2
        "JPM",   # Financial
        "COST",  # Retail
        "V",     # Payments
        "JNJ",   # Healthcare
        "XOM",   # Energy
        "DIS",   # Media
        "PG"     # Consumer staples
    ]

    print(f"\nTest tickers ({len(TEST_TICKERS)}):")
    for ticker in TEST_TICKERS:
        print(f"  - {ticker}")
    print()

    # Confirm with user
    response = input("Proceed with test? This will cost ~$150 (y/n): ")
    if response.lower() != 'y':
        print("\nTest cancelled by user.")
        return

    print("\n" + "="*80)
    print("STARTING CONSISTENCY TEST")
    print("="*80 + "\n")

    try:
        # Run comprehensive test
        result = tester.test_multiple_tickers(
            analyze_func=agent.analyze_company,
            tickers=TEST_TICKERS,
            runs_per_ticker=5,
            deep_dive=True,
            years_to_analyze=5  # Cost-optimized: 5 years instead of 8
        )

        # Test passed!
        print("\n" + "="*80)
        print("✅ SUCCESS! ALL TESTS PASSED")
        print("="*80)
        print(f"\nAll {len(TEST_TICKERS)} tickers passed consistency test with <1% variance")
        print("\nbasīrah is ready for Phase 8 batch processing!")
        print("The validation layer successfully catches non-deterministic behavior.")
        print("\n" + "="*80 + "\n")

        # Save results
        results_file = project_root / "tests" / "consistency_test_results.json"
        import json
        with open(results_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            serializable_result = {
                "tickers_tested": result["tickers_tested"],
                "all_passed": result["all_passed"],
                "failures": result["failures"],
                "test_date": str(result.get("test_date", "unknown"))
            }
            json.dump(serializable_result, f, indent=2)

        print(f"Results saved to: {results_file}\n")

        return 0  # Success

    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {e}\n")
        print("DO NOT proceed to Phase 8 until this is fixed!")
        print("The validation layer detected non-deterministic behavior.")
        print("\n" + "="*80 + "\n")

        return 1  # Failure


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
