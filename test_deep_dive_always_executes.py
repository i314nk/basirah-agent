"""
Test to verify Deep Dive ALWAYS executes all 3 stages regardless of decision.

This test verifies the fix for the issue where Deep Dive was stopping after
Stage 1 (current year) when the decision was AVOID or WATCH.

Expected behavior:
- Stage 1: Current year analysis → extracts decision (could be BUY/WATCH/AVOID)
- Stage 2: Prior years MD&A + Proxy → ALWAYS executes
- Stage 3: Multi-year synthesis → ALWAYS executes

Usage:
    python test_deep_dive_always_executes.py
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_deep_dive_always_executes():
    """Test that Deep Dive executes all 3 stages regardless of Stage 1 decision."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Deep Dive Always Executes All 3 Stages")
    logger.info("=" * 80)

    agent = WarrenBuffettAgent(enable_validation=False)

    # Track which methods were called
    stages_executed = {
        "stage1_current_year": False,
        "stage2_mda_history": False,
        "stage3_synthesis": False
    }

    # Mock _analyze_current_year (Stage 1)
    original_analyze_current_year = agent._analyze_current_year
    def mock_current_year(*args, **kwargs):
        stages_executed["stage1_current_year"] = True
        logger.info("✅ Stage 1 executed: _analyze_current_year()")
        # Return mock result with WATCH decision (should NOT stop Deep Dive)
        return {
            'thesis': '=== CURRENT YEAR ANALYSIS ===\nMock analysis\n**DECISION: WATCH**',
            'decision': 'WATCH',
            'year': 2024,
            'token_estimate': 1000,
            'metadata': {'tool_calls': 0},
            'metrics': {},
            'insights': {}
        }
    agent._analyze_current_year = mock_current_year

    # Mock _analyze_mda_history (Stage 2)
    original_analyze_mda_history = agent._analyze_mda_history
    def mock_mda_history(*args, **kwargs):
        stages_executed["stage2_mda_history"] = True
        logger.info("✅ Stage 2 executed: _analyze_mda_history()")
        # Return mock summaries
        return ([
            {'year': 2023, 'summary': 'Mock 2023', 'token_estimate': 500, 'metrics': {}, 'insights': {}},
            {'year': 2022, 'summary': 'Mock 2022', 'token_estimate': 500, 'metrics': {}, 'insights': {}},
        ], [])  # summaries, missing_years
    agent._analyze_mda_history = mock_mda_history

    # Mock _synthesize_multi_year_analysis (Stage 3)
    original_synthesize = agent._synthesize_multi_year_analysis
    def mock_synthesis(*args, **kwargs):
        stages_executed["stage3_synthesis"] = True
        logger.info("✅ Stage 3 executed: _synthesize_multi_year_analysis()")
        # Return mock final thesis
        return {
            'thesis': '=== MULTI-YEAR SYNTHESIS ===\nMock synthesis\n**DECISION: WATCH**',
            'decision': 'WATCH',
            'ticker': 'TEST',
            'metadata': {'tool_calls': 0}
        }
    agent._synthesize_multi_year_analysis = mock_synthesis

    # Mock SEC filing tool and other tools
    agent.tools["sec_filing"].execute = Mock(return_value={
        "success": False,
        "error": "Mock - proxy not needed for test"
    })
    agent.tools["gurufocus"].execute = Mock(return_value={
        "success": True,
        "data": {"metrics": {}}
    })
    agent._report_progress = lambda **kwargs: None  # No-op progress reporting
    agent._warm_cache_for_synthesis = lambda *args, **kwargs: None  # No-op
    agent._fetch_verified_metrics = lambda *args: {}  # Return empty metrics

    # Execute Deep Dive with 3 years (Stage 1 should return WATCH decision)
    logger.info("\n📊 Executing Deep Dive with deep_dive=True, years_to_analyze=3...")
    logger.info("   Stage 1 will return decision='WATCH' (this should NOT stop Deep Dive)\n")

    result = agent.analyze_company(
        ticker="TEST",
        deep_dive=True,
        years_to_analyze=3
    )

    # Verify all 3 stages were executed
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION RESULTS")
    logger.info("=" * 80)

    all_passed = True

    if stages_executed["stage1_current_year"]:
        logger.info("✅ Stage 1 (Current Year): EXECUTED")
    else:
        logger.error("❌ Stage 1 (Current Year): NOT EXECUTED")
        all_passed = False

    if stages_executed["stage2_mda_history"]:
        logger.info("✅ Stage 2 (MD&A History): EXECUTED")
    else:
        logger.error("❌ Stage 2 (MD&A History): NOT EXECUTED - DEEP DIVE STOPPED EARLY!")
        all_passed = False

    if stages_executed["stage3_synthesis"]:
        logger.info("✅ Stage 3 (Multi-Year Synthesis): EXECUTED")
    else:
        logger.error("❌ Stage 3 (Multi-Year Synthesis): NOT EXECUTED - DEEP DIVE STOPPED EARLY!")
        all_passed = False

    logger.info("\n" + "=" * 80)
    if all_passed:
        logger.info("✅ TEST PASSED: Deep Dive executed all 3 stages despite WATCH decision")
        logger.info("=" * 80)
        logger.info("\nKey Findings:")
        logger.info("• Stage 1 returned decision='WATCH'")
        logger.info("• Stage 2 (MD&A History) still executed ✅")
        logger.info("• Stage 3 (Multi-Year Synthesis) still executed ✅")
        logger.info("\nConclusion: Deep Dive now ALWAYS executes all stages.")
        logger.info("The Tier 1 decision gate has been successfully removed.")
        return True
    else:
        logger.error("❌ TEST FAILED: Deep Dive did not execute all stages")
        logger.info("=" * 80)
        logger.error("\nThe Tier 1 decision gate is still blocking Deep Dive!")
        logger.error("Deep Dive should ALWAYS execute all 3 stages regardless of decision.")
        return False


if __name__ == "__main__":
    try:
        success = test_deep_dive_always_executes()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ TEST ERROR: {e}", exc_info=True)
        sys.exit(1)
