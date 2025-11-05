"""
Test script for Phase 6C.1 Storage & Search functionality.
Tests AnalysisStorage and AnalysisSearchEngine.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage import AnalysisStorage, AnalysisSearchEngine


def print_section(title):
    """Print section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def create_mock_deep_dive_result():
    """Create mock deep dive analysis result."""
    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "decision": "BUY",
        "conviction": "HIGH",
        "intrinsic_value": 185.50,
        "current_price": 150.25,
        "margin_of_safety": 19.0,
        "roic": 48.5,
        "thesis": "Apple is a high-quality business with excellent fundamentals. Strong brand, loyal customer base, and exceptional capital efficiency make it a Warren Buffett-style investment.",
        "metadata": {
            "analysis_type": "deep_dive",
            "years_analyzed": 3,
            "analysis_duration_seconds": 245,
            "token_usage": {
                "input_tokens": 25000,
                "output_tokens": 3500,
                "total_cost": 4.50
            }
        }
    }


def create_mock_quick_screen_result():
    """Create mock quick screen analysis result."""
    return {
        "ticker": "MSFT",
        "company_name": "Microsoft Corporation",
        "decision": "INVESTIGATE",
        "thesis": "Microsoft shows strong fundamentals with growing cloud business. Recommendation: INVESTIGATE for potential deep dive analysis.",
        "metadata": {
            "analysis_type": "quick",
            "analysis_duration_seconds": 75,
            "token_usage": {
                "input_tokens": 8000,
                "output_tokens": 1200,
                "total_cost": 1.25
            }
        }
    }


def create_mock_sharia_result():
    """Create mock Sharia compliance analysis result."""
    return {
        "ticker": "TSLA",
        "company_name": "Tesla Inc.",
        "status": "COMPLIANT",
        "purification_rate": 0.15,
        "analysis": "Tesla meets AAOIFI standards for Sharia compliance. The company operates in permissible industries (electric vehicles and clean energy) with minimal interest income.",
        "metadata": {
            "analysis_type": "sharia",
            "analysis_duration_seconds": 95,
            "token_usage": {
                "input_tokens": 12000,
                "output_tokens": 2000,
                "total_cost": 2.10
            }
        }
    }


def test_storage_initialization():
    """Test storage initialization."""
    print_section("Test 1: Storage Initialization")

    try:
        storage = AnalysisStorage()
        print("[OK] AnalysisStorage initialized")

        # Check directories exist
        if storage.storage_root.exists():
            print(f"[OK] Storage root exists: {storage.storage_root}")
        else:
            print("[FAIL] Storage root does not exist")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        return False


def test_save_analyses():
    """Test saving analyses."""
    print_section("Test 2: Saving Analyses")

    try:
        storage = AnalysisStorage()

        # Save deep dive
        print("\n1. Saving Deep Dive analysis...")
        deep_dive = create_mock_deep_dive_result()
        result1 = storage.save_analysis(deep_dive)

        if result1['success']:
            print(f"[OK] Deep dive saved: {result1['analysis_id']}")
            print(f"     Database ID: {result1['database_id']}")
            print(f"     File path: {result1['relative_path']}")
        else:
            print(f"[FAIL] Deep dive save failed: {result1.get('error')}")
            return False

        # Save quick screen
        print("\n2. Saving Quick Screen analysis...")
        quick_screen = create_mock_quick_screen_result()
        result2 = storage.save_analysis(quick_screen)

        if result2['success']:
            print(f"[OK] Quick screen saved: {result2['analysis_id']}")
        else:
            print(f"[FAIL] Quick screen save failed: {result2.get('error')}")
            return False

        # Save Sharia
        print("\n3. Saving Sharia analysis...")
        sharia = create_mock_sharia_result()
        result3 = storage.save_analysis(sharia)

        if result3['success']:
            print(f"[OK] Sharia analysis saved: {result3['analysis_id']}")
        else:
            print(f"[FAIL] Sharia save failed: {result3.get('error')}")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Save analyses failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_analysis():
    """Test loading analysis."""
    print_section("Test 3: Loading Analysis")

    try:
        storage = AnalysisStorage()
        search = AnalysisSearchEngine()

        # Get most recent analysis
        recent = search.get_recent(days=1, limit=1)

        if not recent:
            print("[SKIP] No analyses found to load")
            return True

        analysis_id = recent[0]['analysis_id']
        print(f"\nLoading analysis: {analysis_id}")

        loaded = storage.load_analysis(analysis_id)

        if loaded:
            print(f"[OK] Analysis loaded successfully")
            print(f"     Ticker: {loaded.get('ticker')}")
            print(f"     Decision: {loaded.get('decision', loaded.get('status'))}")
            return True
        else:
            print("[FAIL] Failed to load analysis")
            return False
    except Exception as e:
        print(f"[FAIL] Load analysis failed: {e}")
        return False


def test_search_functionality():
    """Test search functionality."""
    print_section("Test 4: Search Functionality")

    try:
        search = AnalysisSearchEngine()

        # Test 1: Get recent
        print("\n1. Testing get_recent()...")
        recent = search.get_recent(days=7, limit=10)
        print(f"[OK] Found {len(recent)} recent analyses")

        # Test 2: Search by ticker
        print("\n2. Testing search by ticker...")
        aapl_results = search.get_by_ticker("AAPL", limit=5)
        print(f"[OK] Found {len(aapl_results)} AAPL analyses")

        # Test 3: Search by analysis type
        print("\n3. Testing search by analysis type...")
        deep_dives = search.search(analysis_types=["deep_dive"], limit=10)
        print(f"[OK] Found {len(deep_dives)} deep dive analyses")

        # Test 4: Search by decision
        print("\n4. Testing search by decision...")
        buy_results = search.search(decisions=["buy"], limit=10)
        print(f"[OK] Found {len(buy_results)} BUY decisions")

        # Test 5: Quick search
        print("\n5. Testing quick_search()...")
        quick_results = search.quick_search("AAPL")
        print(f"[OK] Quick search found {len(quick_results)} results")

        return True
    except Exception as e:
        print(f"[FAIL] Search functionality failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test statistics functionality."""
    print_section("Test 5: Statistics")

    try:
        search = AnalysisSearchEngine()

        stats = search.get_statistics()

        if stats:
            print("[OK] Statistics retrieved successfully:\n")
            print(f"     Total analyses: {stats.get('total_analyses', 0)}")
            print(f"     Unique companies: {stats.get('unique_companies', 0)}")
            print(f"     Total cost: ${stats.get('total_cost', 0):.2f}")
            print(f"     Avg cost: ${stats.get('avg_cost', 0):.2f}")
            print(f"     Total time: {stats.get('total_time_hours', 0):.1f} hours")
            print(f"     Quick screens: {stats.get('quick_screens', 0)}")
            print(f"     Deep dives: {stats.get('deep_dives', 0)}")
            print(f"     Sharia screens: {stats.get('sharia_screens', 0)}")
            print(f"     BUY decisions: {stats.get('buy_count', 0)}")
            return True
        else:
            print("[WARN] No statistics available (no analyses yet)")
            return True
    except Exception as e:
        print(f"[FAIL] Statistics failed: {e}")
        return False


def test_storage_stats():
    """Test storage statistics."""
    print_section("Test 6: Storage Statistics")

    try:
        storage = AnalysisStorage()

        stats = storage.get_storage_stats()

        if stats:
            print("[OK] Storage statistics retrieved:\n")
            print(f"     File count: {stats.get('file_count', 0)}")
            print(f"     Total size: {stats.get('total_size_mb', 0):.2f} MB")
            print(f"     Database records: {stats.get('database_records', 0)}")
            print(f"     Storage root: {stats.get('storage_root')}")
            return True
        else:
            print("[WARN] Storage stats not available")
            return True
    except Exception as e:
        print(f"[FAIL] Storage stats failed: {e}")
        return False


def test_companies_and_tags():
    """Test companies and tags functionality."""
    print_section("Test 7: Companies & Tags")

    try:
        search = AnalysisSearchEngine()

        # Test companies
        print("\n1. Getting companies...")
        companies = search.get_companies()
        print(f"[OK] Found {len(companies)} companies")

        if companies:
            print("\nTop 3 companies:")
            for i, company in enumerate(companies[:3], 1):
                print(f"   {i}. {company['ticker']} - {company['company_name']}")
                print(f"      Analyses: {company['total_analyses']}")

        # Test tags
        print("\n2. Getting tags...")
        tags = search.get_tags()
        print(f"[OK] Found {len(tags)} tags")

        if tags:
            print("\nAvailable tags:")
            for tag in tags[:5]:
                print(f"   - {tag['name']} (used {tag['usage_count']} times)")

        return True
    except Exception as e:
        print(f"[FAIL] Companies/tags test failed: {e}")
        return False


def print_summary(results):
    """Print test summary."""
    print_section("Test Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"\n[RESULTS] Results: {passed}/{total} tests passed")

    if failed > 0:
        print(f"\n[FAIL] Failed tests:")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")

    if passed == total:
        print("\n[OK] All tests passed! Storage & Search system is ready.")
        print("\n[NEXT] Next steps:")
        print("   1. Ready for Stage 3 (History Browser UI)")
        print("   2. Ready to integrate into analysis flows")
        print("   3. View saved analyses: ls basirah_analyses/")
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")


def main():
    """Run all tests."""
    print("\n" + "Storage & Search System Test".center(60))
    print("Phase 6C.1 - Stage 2 Verification".center(60))

    results = {}

    # Run tests
    results['Storage Initialization'] = test_storage_initialization()
    results['Save Analyses'] = test_save_analyses()
    results['Load Analysis'] = test_load_analysis()
    results['Search Functionality'] = test_search_functionality()
    results['Statistics'] = test_statistics()
    results['Storage Stats'] = test_storage_stats()
    results['Companies & Tags'] = test_companies_and_tags()

    print_summary(results)


if __name__ == "__main__":
    main()
