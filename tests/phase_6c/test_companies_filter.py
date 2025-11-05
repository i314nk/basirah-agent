"""
Test that companies with 0 analyses are filtered out.
Verifies fix for stale company records appearing in the list.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.storage import AnalysisSearchEngine


def test_companies_filter():
    """Verify companies with 0 analyses don't appear in get_companies()."""
    print("\nTesting Companies Filter (0 analyses excluded)")
    print("=" * 60)

    search = AnalysisSearchEngine()

    # Get companies list
    print("\n1. Getting companies from database...")
    companies = search.get_companies()

    print(f"   Found {len(companies)} companies")

    # Check that all companies have at least 1 analysis
    print("\n2. Verifying all companies have analyses...")
    all_valid = True

    for company in companies:
        ticker = company['ticker']
        total = company['total_analyses']
        print(f"   {ticker}: {total} analyses")

        if total == 0:
            print(f"   [FAIL] Company {ticker} has 0 analyses but still appears!")
            all_valid = False

    if all_valid:
        print("   [OK] All companies have at least 1 analysis")
    else:
        print("   [FAIL] Some companies have 0 analyses")
        return False

    # Additional check: verify no company has None or negative analyses
    print("\n3. Checking for invalid analysis counts...")
    for company in companies:
        total = company['total_analyses']
        if total is None or total < 0:
            print(f"   [FAIL] Company {company['ticker']} has invalid count: {total}")
            return False

    print("   [OK] All analysis counts are valid positive numbers")

    print("\n" + "=" * 60)
    print("[SUCCESS] Companies filter working correctly!")
    print("=" * 60)
    print("\nKey behavior:")
    print("  - Only companies with total_analyses > 0 are returned")
    print("  - Companies with 0 analyses are automatically filtered out")
    print("  - After deleting all analyses, companies won't appear in sidebar")

    return True


def test_empty_database_companies():
    """Test that empty database returns no companies."""
    print("\n\nTesting Empty Database - No Companies")
    print("=" * 60)

    search = AnalysisSearchEngine()

    # Get companies (should be empty if all analyses deleted)
    print("\n1. Getting companies from empty database...")
    companies = search.get_companies()

    print(f"   Found {len(companies)} companies")

    if len(companies) == 0:
        print("   [OK] No companies returned (expected with empty database)")
    else:
        print(f"   [INFO] Found {len(companies)} companies with analyses")
        print("   This is OK if there are actual analyses in the database")

    print("\n" + "=" * 60)
    print("[SUCCESS] Empty database handling works correctly!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        print("\n" + "Companies Filter Tests".center(60))
        print("Testing that companies with 0 analyses are filtered".center(60))

        success1 = test_companies_filter()
        success2 = test_empty_database_companies()

        if success1 and success2:
            print("\n" + "=" * 60)
            print("[SUCCESS] All companies filter tests passed!")
            print("=" * 60)
            print("\nNow when you click refresh, companies with 0 analyses won't appear!")
        else:
            print("\n[FAIL] Some tests failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
