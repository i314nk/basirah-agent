"""
Single-ticker consistency test for basīrah.

Quick verification test before running the full 10-ticker suite.
Tests 1 company, 3 runs to verify <1% variance.

This is a SMOKE TEST - run this first to catch obvious issues.
Cost: ~$9 | Duration: ~10 minutes
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.buffett_agent import WarrenBuffettAgent
from src.validation import ConsistencyTester

def main():
    """Run single-ticker consistency test."""

    print("\n" + "="*80)
    print("BASĪRAH SINGLE-TICKER CONSISTENCY TEST - Phase 7.5 Smoke Test")
    print("="*80)
    print("\nThis is a QUICK smoke test before running the full 10-ticker suite.")
    print("Tests 1 company (FDS), 3 runs.")
    print("Using 5-year deep dive analysis (cost-optimized).")
    print("\nEstimated time: ~10 minutes")
    print("Estimated cost: ~$9 (3 runs × $3 per analysis)")
    print("\n" + "="*80 + "\n")

    # Test ticker (FDS - the known problem case from bug discovery)
    TEST_TICKER = "FDS"  # FactSet Research Systems - known to have had issues

    print(f"Test ticker: {TEST_TICKER} (FactSet Research Systems)")
    print("\nWhy FDS?")
    print("  - This was the ticker where the 20% variance bug was discovered")
    print("  - If FDS passes, other tickers should also pass")
    print("  - Good smoke test before committing to full $150 test suite")
    print()

    # Initialize
    print("Initializing Warren Buffett Agent...")
    agent = WarrenBuffettAgent()

    print("Initializing Consistency Tester (1% variance threshold)...")
    tester = ConsistencyTester(variance_threshold=0.01)  # 1% max variance

    # Confirm with user
    response = input("Proceed with smoke test? This will cost ~$9 (y/n): ")
    if response.lower() != 'y':
        print("\nTest cancelled by user.")
        return

    print("\n" + "="*80)
    print("STARTING SINGLE-TICKER CONSISTENCY TEST")
    print("="*80 + "\n")

    try:
        # Run smoke test (3 runs for quick validation)
        result = tester.test_analysis_consistency(
            analyze_func=agent.analyze_company,
            ticker=TEST_TICKER,
            runs=3,  # Quick smoke test - 3 runs instead of 5
            deep_dive=True,
            years_to_analyze=5  # Cost-optimized: 5 years
        )

        # Test passed!
        print("\n" + "="*80)
        print("✅ SUCCESS! SMOKE TEST PASSED")
        print("="*80)
        print(f"\n{TEST_TICKER} passed consistency test with <1% variance")
        print("\nVariance breakdown:")
        for metric, variance in result['variances'].items():
            status = "✅" if variance <= 0.01 else "❌"
            print(f"  {status} {metric}: {variance*100:.3f}% variance")

        print("\n" + "-"*80)
        print("RECOMMENDATION: Proceed with full 10-ticker test")
        print("-"*80)
        print("\nThe smoke test passed, indicating the validation layer is working.")
        print("You can now run the full consistency test with confidence:")
        print("\n  python tests/run_consistency_test.py")
        print("\nFull test specs:")
        print("  - 10 diverse tickers across sectors")
        print("  - 5 runs per ticker (50 total analyses)")
        print("  - Cost: ~$150")
        print("  - Duration: ~90 minutes")
        print("\n" + "="*80 + "\n")

        # Save results
        results_file = project_root / "tests" / "single_consistency_test_results.json"
        import json
        from datetime import datetime

        with open(results_file, 'w') as f:
            serializable_result = {
                "ticker": TEST_TICKER,
                "runs": result["runs"],
                "variances": {k: float(v) for k, v in result["variances"].items()},
                "pass": result["pass"],
                "test_date": datetime.now().isoformat()
            }
            json.dump(serializable_result, f, indent=2)

        print(f"Results saved to: {results_file}\n")

        return 0  # Success

    except Exception as e:
        print("\n" + "="*80)
        print("❌ SMOKE TEST FAILED")
        print("="*80)
        print(f"\nError: {e}\n")
        print("DO NOT proceed with full 10-ticker test until this is fixed!")
        print("\nPossible causes:")
        print("  1. Non-deterministic behavior in ReAct loop")
        print("  2. API data changed between runs (GuruFocus updates)")
        print("  3. Calculator tool not being used consistently")
        print("  4. Validation layer not catching skipped calculations")
        print("\nNext steps:")
        print("  1. Review the error message above")
        print("  2. Check logs for validation errors")
        print("  3. Fix the underlying issue")
        print("  4. Re-run this smoke test")
        print("  5. Only proceed to full test after smoke test passes")
        print("\n" + "="*80 + "\n")

        return 1  # Failure


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
