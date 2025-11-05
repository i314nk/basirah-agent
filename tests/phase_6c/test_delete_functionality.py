"""
Test script for delete functionality in Phase 6C.1.
Verifies that delete_analysis works correctly.
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


def create_test_analysis():
    """Create a test analysis for deletion."""
    return {
        "ticker": "DELTEST",
        "company_name": "Delete Test Company",
        "decision": "BUY",
        "conviction": "LOW",
        "intrinsic_value": 100.0,
        "current_price": 80.0,
        "margin_of_safety": 20.0,
        "roic": 15.0,
        "thesis": "This is a test analysis that will be deleted.",
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


def test_delete_functionality():
    """Test the complete delete workflow."""
    print_section("Testing Delete Functionality")

    try:
        storage = AnalysisStorage()
        search = AnalysisSearchEngine()

        # Step 1: Create and save a test analysis
        print("\n1. Creating test analysis...")
        test_analysis = create_test_analysis()
        save_result = storage.save_analysis(test_analysis)

        if not save_result['success']:
            print("[FAIL] Failed to create test analysis")
            return False

        analysis_id = save_result['analysis_id']
        file_path = Path(save_result['file_path'])

        print(f"[OK] Test analysis created: {analysis_id}")
        print(f"     File path: {file_path}")

        # Step 2: Verify it exists in database
        print("\n2. Verifying analysis exists in database...")
        results = search.quick_search("DELTEST")

        if not results:
            print("[FAIL] Analysis not found in database")
            return False

        print(f"[OK] Analysis found in database (ID: {results[0]['id']})")

        # Step 3: Verify file exists
        print("\n3. Verifying file exists...")
        if not file_path.exists():
            print("[FAIL] Analysis file does not exist")
            return False

        print(f"[OK] File exists: {file_path}")

        # Step 4: Delete the analysis
        print("\n4. Deleting analysis...")
        delete_success = storage.delete_analysis(analysis_id)

        if not delete_success:
            print("[FAIL] Delete operation returned False")
            return False

        print(f"[OK] Delete operation successful")

        # Step 5: Verify it's gone from database
        print("\n5. Verifying removal from database...")
        results_after = search.quick_search("DELTEST")

        if results_after:
            print("[FAIL] Analysis still exists in database")
            return False

        print("[OK] Analysis removed from database")

        # Step 6: Verify file is deleted
        print("\n6. Verifying file deletion...")
        if file_path.exists():
            print("[FAIL] File still exists after deletion")
            return False

        print("[OK] File successfully deleted")

        # Step 7: Verify load_analysis returns None
        print("\n7. Verifying load_analysis returns None...")
        loaded = storage.load_analysis(analysis_id)

        if loaded is not None:
            print("[FAIL] load_analysis should return None for deleted analysis")
            return False

        print("[OK] load_analysis correctly returns None")

        print("\n" + "="*60)
        print("[SUCCESS] All delete functionality tests passed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Delete functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cascade_delete():
    """Test that cascade delete works (deleting company analyses)."""
    print_section("Testing Cascade Behavior")

    try:
        storage = AnalysisStorage()
        search = AnalysisSearchEngine()

        print("\n1. Creating multiple analyses for same ticker...")

        # Create 2 analyses for the same test company
        for i in range(2):
            test_analysis = create_test_analysis()
            test_analysis['ticker'] = f"CASTEST"
            test_analysis['decision'] = "BUY" if i == 0 else "WATCH"
            save_result = storage.save_analysis(test_analysis)

            if save_result['success']:
                print(f"[OK] Created analysis {i+1}: {save_result['analysis_id']}")
            else:
                print(f"[FAIL] Failed to create analysis {i+1}")
                return False

        # Verify both exist
        print("\n2. Verifying both analyses exist...")
        results = search.quick_search("CASTEST")

        if len(results) != 2:
            print(f"[FAIL] Expected 2 analyses, found {len(results)}")
            return False

        print(f"[OK] Found 2 analyses for CASTEST")

        # Delete first one
        print("\n3. Deleting first analysis...")
        first_id = results[0]['analysis_id']
        storage.delete_analysis(first_id)
        print(f"[OK] Deleted: {first_id}")

        # Verify only one remains
        print("\n4. Verifying one analysis remains...")
        results_after = search.quick_search("CASTEST")

        if len(results_after) != 1:
            print(f"[FAIL] Expected 1 analysis, found {len(results_after)}")
            return False

        print(f"[OK] One analysis remains")

        # Clean up - delete remaining
        print("\n5. Cleaning up remaining analysis...")
        storage.delete_analysis(results_after[0]['analysis_id'])
        print("[OK] Cleanup complete")

        print("\n" + "="*60)
        print("[SUCCESS] Cascade delete behavior correct!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Cascade test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all delete functionality tests."""
    print("\n" + "Delete Functionality Test".center(60))
    print("Phase 6C.1 - Delete Feature Verification".center(60))

    results = {}

    # Run tests
    results['Delete Functionality'] = test_delete_functionality()
    results['Cascade Delete'] = test_cascade_delete()

    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print(f"\n[RESULTS] {passed}/{total} test groups passed")

    if passed == total:
        print("\n[SUCCESS] All delete functionality tests passed!")
        print("\nDelete feature is ready to use in History Browser UI.")
        print("\nFeatures verified:")
        print("  - Delete analysis from database")
        print("  - Delete analysis file from disk")
        print("  - Proper cascade behavior")
        print("  - load_analysis returns None after delete")
    else:
        print("\n[FAIL] Some tests failed. Please review errors above.")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")


if __name__ == "__main__":
    main()
