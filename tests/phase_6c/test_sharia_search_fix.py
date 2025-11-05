"""
Test that Sharia analyses appear in search results.
Verifies fix for missing Sharia decisions in History page filters.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.storage import AnalysisSearchEngine


def test_sharia_in_search():
    """Verify Sharia analyses are found in search results."""
    print("\nTesting Sharia Analysis Search Fix")
    print("=" * 60)

    search = AnalysisSearchEngine()

    # Test 1: Search with all decision types (should find TSLA)
    print("\n1. Testing search with all decision types...")
    all_decisions = ["buy", "watch", "avoid", "investigate", "pass",
                     "compliant", "doubtful", "non_compliant"]

    results = search.search(
        decisions=all_decisions,
        sort_by="date",
        limit=100
    )

    print(f"   Found {len(results)} total analyses")

    # Find TSLA
    tsla = [r for r in results if r['ticker'] == 'TSLA']
    if tsla:
        print(f"   [OK] TSLA found in results!")
        print(f"        Type: {tsla[0]['analysis_type']}")
        print(f"        Decision: {tsla[0]['decision']}")
    else:
        print(f"   [FAIL] TSLA not found in results")
        return False

    # Test 2: Search with only Sharia decisions
    print("\n2. Testing search with only Sharia decisions...")
    sharia_decisions = ["compliant", "doubtful", "non_compliant"]

    results = search.search(
        decisions=sharia_decisions,
        sort_by="date",
        limit=100
    )

    print(f"   Found {len(results)} Sharia analyses")

    tsla = [r for r in results if r['ticker'] == 'TSLA']
    if tsla:
        print(f"   [OK] TSLA found with Sharia filter!")
    else:
        print(f"   [FAIL] TSLA not found with Sharia filter")
        return False

    # Test 3: Search excluding Sharia decisions (old bug)
    print("\n3. Testing search WITHOUT Sharia decisions (old behavior)...")
    non_sharia_decisions = ["buy", "watch", "avoid", "investigate", "pass"]

    results = search.search(
        decisions=non_sharia_decisions,
        sort_by="date",
        limit=100
    )

    print(f"   Found {len(results)} non-Sharia analyses")

    tsla = [r for r in results if r['ticker'] == 'TSLA']
    if not tsla:
        print(f"   [OK] TSLA correctly excluded when Sharia decisions not in filter")
    else:
        print(f"   [FAIL] TSLA found even though Sharia decisions excluded")
        return False

    # Test 4: Quick search should still work
    print("\n4. Testing quick search...")
    results = search.quick_search("TSLA")

    if results:
        print(f"   [OK] Quick search finds TSLA ({len(results)} result(s))")
    else:
        print(f"   [FAIL] Quick search doesn't find TSLA")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All Sharia search tests passed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_sharia_in_search()
        if not success:
            print("\n[FAIL] Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
