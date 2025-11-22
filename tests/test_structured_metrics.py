"""
Test Phase 7.7 Phase 2: Structured Metrics Extraction

This test verifies that structured metrics are properly extracted from tool outputs
and included in the final analysis result.

Expected behavior:
1. Stage 1 (current year): Extracts metrics from GuruFocus + Calculator cache
2. Stage 2 (prior years): Extracts metrics for each prior year
3. Final result: Includes all metrics in metadata["structured_metrics"]
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.buffett_agent import WarrenBuffettAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_structured_metrics_extraction():
    """Test Phase 7.7 Phase 2 structured metrics extraction."""
    print("=" * 80)
    print("PHASE 7.7 PHASE 2: STRUCTURED METRICS EXTRACTION TEST")
    print("=" * 80)
    print()

    # Initialize agent
    print("Step 1: Initialize agent...")
    agent = WarrenBuffettAgent(
        model_key="kimi-k2-thinking",
        enable_validation=False  # Disable validation for faster testing
    )
    print("[PASS] Agent initialized")
    print()

    # Run a deep dive analysis (5 years)
    print("Step 2: Run deep dive analysis with metrics extraction (5 years)...")
    print("   This will take 3-5 minutes...")
    print()

    result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=5)

    print()
    print("Step 3: Verify analysis completed...")
    assert result['decision'] != "ERROR", f"Analysis failed: {result.get('thesis', 'Unknown error')}"
    print(f"[PASS] Analysis completed: {result['decision']}")
    print()

    # Check that structured_metrics exists in metadata
    print("Step 4: Verify structured_metrics in metadata...")
    assert 'metadata' in result, "Result should have metadata"
    assert 'structured_metrics' in result['metadata'], "Metadata should have structured_metrics"

    structured_metrics = result['metadata']['structured_metrics']
    print("[PASS] structured_metrics found in metadata")
    print()

    # Verify current_year metrics
    print("Step 5: Verify current year metrics...")
    assert 'current_year' in structured_metrics, "Should have current_year metrics"
    current_year = structured_metrics['current_year']

    assert 'year' in current_year, "Current year should have 'year' field"
    assert 'metrics' in current_year, "Current year should have 'metrics' field"

    print(f"[PASS] Current year: {current_year['year']}")
    print(f"[PASS] Current year has metrics: {bool(current_year['metrics'])}")

    # Show sample metrics if available
    if current_year['metrics']:
        sample_keys = list(current_year['metrics'].keys())[:5]
        print(f"   Sample metrics: {sample_keys}")
    print()

    # Verify prior_years metrics
    print("Step 6: Verify prior years metrics...")
    assert 'prior_years' in structured_metrics, "Should have prior_years metrics"
    prior_years = structured_metrics['prior_years']

    assert isinstance(prior_years, list), "prior_years should be a list"
    assert len(prior_years) > 0, "Should have at least 1 prior year"

    print(f"[PASS] Prior years analyzed: {len(prior_years)}")

    for i, year_data in enumerate(prior_years):
        assert 'year' in year_data, f"Prior year {i} should have 'year' field"
        assert 'metrics' in year_data, f"Prior year {i} should have 'metrics' field"
        print(f"   Year {year_data['year']}: {bool(year_data['metrics'])} metrics")
    print()

    # Verify all_years aggregation
    print("Step 7: Verify all_years aggregation...")
    assert 'all_years' in structured_metrics, "Should have all_years aggregation"
    all_years = structured_metrics['all_years']

    assert isinstance(all_years, list), "all_years should be a list"
    expected_count = 1 + len(prior_years)  # current year + prior years
    assert len(all_years) == expected_count, f"all_years should have {expected_count} entries"

    print(f"[PASS] all_years has {len(all_years)} entries (current + prior)")
    print(f"   Years: {[y['year'] for y in all_years]}")
    print()

    # Verify cache statistics (Phase 1 still working)
    print("Step 8: Verify tool caching still working (Phase 1)...")
    cache_stats = result['metadata']['cache_stats']

    print(f"   Cache Hits: {cache_stats['cache_hits']}")
    print(f"   Cache Misses: {cache_stats['cache_misses']}")
    print(f"   Hit Rate: {cache_stats['hit_rate_percent']}%")

    assert cache_stats['cache_hits'] > 0, "Should have cache hits from Phase 1"
    print("[PASS] Tool caching still working alongside metrics extraction")
    print()

    # Check metrics quality (if GuruFocus data was fetched)
    print("Step 9: Check metrics data quality...")
    metrics_found = 0
    non_null_metrics = 0

    for year_data in all_years:
        if year_data['metrics']:
            metrics_found += 1
            # Count how many non-null metric fields exist
            non_null = sum(1 for v in year_data['metrics'].values() if v is not None)
            non_null_metrics += non_null
            print(f"   Year {year_data['year']}: {non_null} non-null metrics extracted")

    print(f"[PASS] {metrics_found}/{len(all_years)} years have metrics extracted")
    print(f"[PASS] Total non-null metrics across all years: {non_null_metrics}")
    print()

    # Summary
    print("=" * 80)
    print("PHASE 7.7 PHASE 2: STRUCTURED METRICS EXTRACTION TEST PASSED")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  [OK] structured_metrics in metadata: YES")
    print(f"  [OK] Current year metrics: {bool(current_year['metrics'])}")
    print(f"  [OK] Prior years with metrics: {metrics_found}/{len(prior_years)}")
    print(f"  [OK] all_years aggregation: {len(all_years)} years")
    print(f"  [OK] Tool caching working: {cache_stats['hit_rate_percent']}% hit rate")
    print(f"  [OK] Total non-null metrics: {non_null_metrics}")
    print()

    # Expected benefits
    print("Achieved Benefits:")
    print(f"  - Structured metrics available for all {len(all_years)} years")
    print(f"  - Instant access to quantitative data (no text parsing needed)")
    print(f"  - Programmatic trend analysis enabled")
    print(f"  - {non_null_metrics} quantitative metrics extracted from tool outputs")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_structured_metrics_extraction()
        if success:
            print("[SUCCESS] All tests passed!")
            sys.exit(0)
    except AssertionError as e:
        print(f"[FAILED] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
