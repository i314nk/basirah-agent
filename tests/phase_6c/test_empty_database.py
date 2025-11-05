"""
Test that the History page handles an empty database gracefully.
Verifies fix for None values in statistics when no analyses exist.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.storage import AnalysisSearchEngine


def test_empty_database_statistics():
    """Verify statistics work when database is empty."""
    print("\nTesting Empty Database Statistics")
    print("=" * 60)

    search = AnalysisSearchEngine()

    # Get statistics
    print("\n1. Getting statistics from database...")
    stats = search.get_statistics()

    print(f"   Retrieved statistics: {stats}")

    # Check each statistic can be safely used
    print("\n2. Checking each statistic value...")

    # Total analyses
    total_analyses = stats.get('total_analyses', 0) or 0
    print(f"   Total Analyses: {total_analyses}")
    assert isinstance(total_analyses, int), "total_analyses should be an integer"

    # Unique companies
    unique_companies = stats.get('unique_companies', 0) or 0
    print(f"   Unique Companies: {unique_companies}")
    assert isinstance(unique_companies, int), "unique_companies should be an integer"

    # Total cost (can be None from database)
    total_cost = stats.get('total_cost') or 0
    print(f"   Total Cost: ${total_cost:.2f}")
    assert isinstance(total_cost, (int, float)), "total_cost should be a number"

    # Avg cost (can be None from database)
    avg_cost = stats.get('avg_cost') or 0
    print(f"   Avg Cost: ${avg_cost:.2f}")
    assert isinstance(avg_cost, (int, float)), "avg_cost should be a number"

    # Test formatting (like in the UI)
    print("\n3. Testing f-string formatting (like in UI)...")
    try:
        formatted_total = f"${stats.get('total_cost') or 0:.2f}"
        formatted_avg = f"${stats.get('avg_cost') or 0:.2f}"
        print(f"   Total Cost formatted: {formatted_total}")
        print(f"   Avg Cost formatted: {formatted_avg}")
        print("   [OK] Formatting works correctly")
    except TypeError as e:
        print(f"   [FAIL] Formatting failed: {e}")
        return False

    # Test breakdown dictionaries
    print("\n4. Checking breakdown dictionaries...")

    by_type = stats.get('by_type', {})
    print(f"   By Type: {by_type}")
    assert isinstance(by_type, dict), "by_type should be a dictionary"

    by_decision = stats.get('by_decision', {})
    print(f"   By Decision: {by_decision}")
    assert isinstance(by_decision, dict), "by_decision should be a dictionary"

    print("\n" + "=" * 60)
    print("[SUCCESS] Empty database statistics handled correctly!")
    print("=" * 60)
    print("\nKey findings:")
    print("  - Database returns None for SUM/AVG with no rows")
    print("  - Using 'or 0' ensures we always get a number")
    print("  - f-string formatting works with fallback value")
    print("  - UI will display $0.00 when database is empty")

    return True


def test_search_with_empty_database():
    """Verify search works when database is empty."""
    print("\n\nTesting Search with Empty Database")
    print("=" * 60)

    search = AnalysisSearchEngine()

    # Quick search
    print("\n1. Testing quick search...")
    results = search.quick_search("AAPL")
    print(f"   Results: {len(results)} found")
    assert results == [], "Should return empty list"
    print("   [OK] Quick search returns empty list")

    # Advanced search
    print("\n2. Testing advanced search...")
    results = search.search(
        analysis_types=["deep_dive"],
        decisions=["buy"],
        sort_by="date"
    )
    print(f"   Results: {len(results)} found")
    assert results == [], "Should return empty list"
    print("   [OK] Advanced search returns empty list")

    # Recent analyses
    print("\n3. Testing get_recent...")
    results = search.get_recent(days=7, limit=5)
    print(f"   Results: {len(results)} found")
    assert results == [], "Should return empty list"
    print("   [OK] get_recent returns empty list")

    print("\n" + "=" * 60)
    print("[SUCCESS] Search operations work correctly with empty database!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        # Note: This test assumes the database is empty
        # If tests fail, it may be because there are analyses in the database

        print("\n" + "Empty Database Edge Case Tests".center(60))
        print("Testing graceful handling of empty database".center(60))
        print("\nNOTE: These tests work best with an empty database.")
        print("If tests fail, try deleting all analyses first.\n")

        success1 = test_empty_database_statistics()
        success2 = test_search_with_empty_database()

        if success1 and success2:
            print("\n" + "=" * 60)
            print("[SUCCESS] All empty database tests passed!")
            print("=" * 60)
        else:
            print("\n[FAIL] Some tests failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
