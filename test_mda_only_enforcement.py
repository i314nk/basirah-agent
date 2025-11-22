"""
Test to verify MD&A-only enforcement in Phase 9.1.

This test verifies that _analyze_mda_history() fetches ONLY MD&A sections,
not full 10-Ks, for prior years.

Usage:
    python test_mda_only_enforcement.py
"""

import sys
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.buffett_agent import WarrenBuffettAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_mda_only_enforcement():
    """Test that _analyze_mda_history enforces MD&A-only fetching."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: MD&A-Only Enforcement in Phase 9.1")
    logger.info("=" * 80)

    agent = WarrenBuffettAgent(enable_validation=False)

    # Mock SEC filing tool to verify section parameter
    sec_calls = []

    def mock_sec_execute(**kwargs):
        """Track all SEC filing tool calls."""
        sec_calls.append(kwargs)
        # Return mock successful MD&A response
        return {
            "success": True,
            "data": {
                "content": "Mock MD&A content for testing...",
                "content_length": 100,
                "section": kwargs.get("section", "unknown")
            }
        }

    # Mock _run_analysis_loop to avoid actual LLM calls
    def mock_analysis_loop(ticker, prompt):
        """Return mock analysis result."""
        return {
            'thesis': f'=== {ticker} MD&A ANALYSIS ===\nMock analysis\n=== END MD&A SUMMARY ===',
            'metadata': {'tool_calls': 0}
        }

    # Patch the methods
    agent.tools["sec_filing"].execute = mock_sec_execute
    agent._run_analysis_loop = mock_analysis_loop
    agent._report_progress = lambda **kwargs: None  # No-op progress reporting

    # Test _analyze_mda_history
    logger.info("\n✅ Testing _analyze_mda_history with 3 years...")
    summaries, missing = agent._analyze_mda_history(
        ticker="TEST",
        num_years=3,
        years_to_analyze=4
    )

    logger.info(f"\n📊 Results:")
    logger.info(f"   Summaries generated: {len(summaries)}")
    logger.info(f"   Missing years: {len(missing)}")
    logger.info(f"   SEC tool calls made: {len(sec_calls)}")

    # Verify all SEC calls used section='mda'
    logger.info(f"\n🔍 Verifying all SEC calls used section='mda'...")
    for i, call in enumerate(sec_calls, 1):
        section = call.get('section', 'MISSING')
        year = call.get('year', 'UNKNOWN')
        logger.info(f"   Call {i}: year={year}, section={section}")

        assert section == "mda", \
            f"❌ FAILED: Call {i} used section='{section}' instead of 'mda'"

    logger.info(f"\n✅ ALL SEC CALLS USED section='mda'")

    # Verify no full 10-K fetches
    full_fetches = [c for c in sec_calls if c.get('section') in ['full', None]]
    assert len(full_fetches) == 0, \
        f"❌ FAILED: Found {len(full_fetches)} full 10-K fetches"

    logger.info(f"✅ NO full 10-K fetches detected")

    # Verify all calls were for 10-K filing type
    for call in sec_calls:
        assert call.get('filing_type') == '10-K', \
            f"❌ FAILED: Unexpected filing type: {call.get('filing_type')}"

    logger.info(f"✅ All calls used filing_type='10-K'")

    logger.info("\n" + "=" * 80)
    logger.info("✅ TEST PASSED: MD&A-Only Enforcement Verified")
    logger.info("=" * 80)
    logger.info("\nKey Findings:")
    logger.info(f"• All {len(sec_calls)} SEC tool calls used section='mda'")
    logger.info(f"• Zero full 10-K fetches detected")
    logger.info(f"• {len(summaries)} MD&A summaries generated")
    logger.info("\nConclusion: Phase 9.1 now ENFORCES MD&A-only fetching.")
    logger.info("LLM cannot ignore instructions and fetch full 10-Ks.")


if __name__ == "__main__":
    try:
        test_mda_only_enforcement()
        sys.exit(0)
    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        sys.exit(1)
