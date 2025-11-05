"""
Test script for delete company functionality in Phase 6C.1.
Verifies that delete_company works correctly and cascade deletes all analyses.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.storage import AnalysisStorage, AnalysisSearchEngine


def print_section(title):
    """Print section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def create_test_analyses(storage, ticker, count):
    """Create multiple test analyses for a company."""
    analyses = []

    for i in range(count):
        test_analysis = {
            "ticker": ticker,
            "company_name": f"{ticker} Test Company",
            "decision": ["BUY", "WATCH", "AVOID"][i % 3],
            "conviction": "LOW",
            "intrinsic_value": 100.0 + (i * 10),
            "current_price": 80.0,
            "margin_of_safety": 20.0,
            "roic": 15.0 + i,
            "thesis": f"This is test analysis {i+1} for {ticker}.",
            "metadata": {
                "analysis_type": "deep_dive",
                "years_analyzed": 3,
                "analysis_duration_seconds": 60,
                "token_usage": {
                    "input_tokens": 5000,
                    "output_tokens": 500,
                    "total_cost": 0.75
                }
            }
        }

        result = storage.save_analysis(test_analysis)
        if result['success']:
            analyses.append(result['analysis_id'])

    return analyses


def test_delete_company_with_analyses():
    """Test deleting a company and all its analyses."""
    print_section("Testing Delete Company with Multiple Analyses")

    try:
        storage = AnalysisStorage()
        search = AnalysisSearchEngine()

        # Step 1: Create test company with 3 analyses
        print("\n1. Creating test company with 3 analyses...")
        ticker = "DELCO"
        analyses = create_test_analyses(storage, ticker, 3)

        if len(analyses) != 3:
            print(f"[FAIL] Failed to create test analyses (got {len(analyses)}, expected 3)")
            return False

        print(f"[OK] Created 3 analyses for {ticker}")
        for aid in analyses:
            print(f"     - {aid}")

        # Step 2: Verify company exists in database
        print("\n2. Verifying company exists in database...")
        companies = search.get_companies()
        company_found = any(c['ticker'] == ticker for c in companies)

        if not company_found:
            print(f"[FAIL] Company {ticker} not found in database")
            return False

        print(f"[OK] Company {ticker} found in database")

        # Step 3: Verify analyses exist
        print("\n3. Verifying analyses exist...")
        results = search.quick_search(ticker)

        if len(results) != 3:
            print(f"[FAIL] Expected 3 analyses, found {len(results)}")
            return False

        print(f"[OK] Found 3 analyses for {ticker}")

        # Step 4: Delete the company
        print(f"\n4. Deleting company {ticker}...")
        delete_result = storage.delete_company(ticker)

        if not delete_result['success']:
            print(f"[FAIL] Delete operation failed: {delete_result['message']}")
            return False

        print(f"[OK] Delete successful: {delete_result['message']}")
        print(f"     Deleted {delete_result['deleted_count']} analyses")

        # Step 5: Verify company is gone
        print("\n5. Verifying company removed from database...")
        companies_after = search.get_companies()
        company_still_exists = any(c['ticker'] == ticker for c in companies_after)

        if company_still_exists:
            print(f"[FAIL] Company {ticker} still exists in database")
            return False

        print(f"[OK] Company {ticker} removed from database")

        # Step 6: Verify analyses are gone
        print("\n6. Verifying analyses removed...")
        results_after = search.quick_search(ticker)

        if results_after:
            print(f"[FAIL] Found {len(results_after)} analyses still in database")
            return False

        print(f"[OK] All analyses removed from database")

        # Step 7: Verify files are deleted
        print("\n7. Verifying files deleted...")
        storage_root = Path("basirah_analyses")
        remaining_files = list(storage_root.rglob(f"{ticker}_*.json"))

        if remaining_files:
            print(f"[FAIL] Found {len(remaining_files)} files still on disk")
            return False

        print(f"[OK] All files deleted from disk")

        print("\n" + "="*60)
        print("[SUCCESS] Delete company test passed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_delete_company_not_found():
    """Test deleting a company that doesn't exist."""
    print_section("Testing Delete Non-Existent Company")

    try:
        storage = AnalysisStorage()

        print("\n1. Attempting to delete non-existent company...")
        result = storage.delete_company("NOTEXIST")

        if result['success']:
            print(f"[FAIL] Delete should fail for non-existent company")
            return False

        print(f"[OK] Delete correctly failed: {result['message']}")
        print(f"     Deleted count: {result['deleted_count']}")

        print("\n" + "="*60)
        print("[SUCCESS] Non-existent company test passed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_delete_company_cascade():
    """Test that cascade delete works properly."""
    print_section("Testing Cascade Delete Behavior")

    try:
        storage = AnalysisStorage()
        search = AnalysisSearchEngine()

        # Create two companies
        print("\n1. Creating two companies with analyses...")

        ticker1 = "CASC1"
        ticker2 = "CASC2"

        analyses1 = create_test_analyses(storage, ticker1, 2)
        analyses2 = create_test_analyses(storage, ticker2, 2)

        print(f"[OK] Created {len(analyses1)} analyses for {ticker1}")
        print(f"[OK] Created {len(analyses2)} analyses for {ticker2}")

        # Verify both exist
        print("\n2. Verifying both companies exist...")
        companies = search.get_companies()
        tickers = [c['ticker'] for c in companies]

        if ticker1 not in tickers or ticker2 not in tickers:
            print(f"[FAIL] Not all companies found")
            return False

        print(f"[OK] Both companies found in database")

        # Delete first company
        print(f"\n3. Deleting {ticker1}...")
        result = storage.delete_company(ticker1)

        if not result['success']:
            print(f"[FAIL] Delete failed: {result['message']}")
            return False

        print(f"[OK] Deleted {ticker1}")

        # Verify only second company remains
        print("\n4. Verifying only second company remains...")
        companies_after = search.get_companies()
        tickers_after = [c['ticker'] for c in companies_after]

        if ticker1 in tickers_after:
            print(f"[FAIL] {ticker1} still exists")
            return False

        if ticker2 not in tickers_after:
            print(f"[FAIL] {ticker2} was incorrectly deleted")
            return False

        print(f"[OK] Only {ticker2} remains")

        # Cleanup - delete second company
        print(f"\n5. Cleaning up {ticker2}...")
        storage.delete_company(ticker2)
        print(f"[OK] Cleanup complete")

        print("\n" + "="*60)
        print("[SUCCESS] Cascade delete test passed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all delete company tests."""
    print("\n" + "Delete Company Functionality Test".center(60))
    print("Phase 6C.1 - Company Delete Feature Verification".center(60))

    results = {}

    # Run tests
    results['Delete Company with Analyses'] = test_delete_company_with_analyses()
    results['Delete Non-Existent Company'] = test_delete_company_not_found()
    results['Cascade Delete'] = test_delete_company_cascade()

    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print(f"\n[RESULTS] {passed}/{total} test groups passed")

    if passed == total:
        print("\n[SUCCESS] All delete company tests passed!")
        print("\nDelete company feature is ready to use!")
        print("\nFeatures verified:")
        print("  - Delete company from database")
        print("  - Cascade delete all company analyses")
        print("  - Delete all analysis files from disk")
        print("  - Proper error handling for non-existent companies")
        print("  - Cascade behavior preserves other companies")
    else:
        print("\n[FAIL] Some tests failed. Please review errors above.")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")


if __name__ == "__main__":
    main()
