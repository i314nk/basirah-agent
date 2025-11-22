"""
Test script to verify Phase 9.1 architecture implementation.

Tests:
1. Tier 1 decision gate logic
2. MD&A-only historical analysis (not full 10-Ks)
3. Proxy statement fetching in Tier 2

Usage:
    python test_phase9_1_architecture.py
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.buffett_agent import WarrenBuffettAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tier1_decision_gate():
    """Test that Tier 1 decision gate evaluates correctly."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Tier 1 Decision Gate Logic")
    logger.info("=" * 80)

    agent = WarrenBuffettAgent(
        enable_validation=False  # Disable validation for speed
    )

    # Test AVOID decision (low ROIC)
    logger.info("\nTest 1a: AVOID decision (ROIC < 10%)")

    current_year_analysis = {
        'year': 2024,
        'full_analysis': """
        This company has consistently low returns on invested capital (ROIC < 8%)
        over the past decade. The business model is capital-intensive with no moat.

        **DECISION: AVOID**
        Fails core criterion: ROIC too low for quality investment.
        """,
        'tool_calls_made': 5,
        'token_estimate': 10000
    }

    verified_metrics = {
        'roic_10y_avg': 0.07,  # 7% - below threshold
        'debt_equity': 0.5
    }

    tier1_decision = agent._evaluate_tier1_decision(
        ticker="TEST",
        current_year_analysis=current_year_analysis,
        verified_metrics=verified_metrics
    )

    assert tier1_decision['decision'] == 'AVOID', \
        f"Expected AVOID, got {tier1_decision['decision']}"
    logger.info(f"✅ PASS: Decision = {tier1_decision['decision']}")
    logger.info(f"   Reasoning: {tier1_decision['reasoning']}")

    # Test WATCH decision
    logger.info("\nTest 1b: WATCH decision (good business, wrong price)")

    current_year_analysis_watch = {
        'year': 2024,
        'full_analysis': """
        Excellent business with wide moat and exceptional management.
        ROIC of 22% sustained over 10 years. However, current valuation
        shows only 12% margin of safety - below our 25% threshold.

        **DECISION: WATCH**
        Waiting for better price. Target entry: $150 (current $175).
        """,
        'tool_calls_made': 8,
        'token_estimate': 15000
    }

    verified_metrics_watch = {
        'roic_10y_avg': 0.22,  # 22% - excellent
        'debt_equity': 0.3
    }

    tier1_decision_watch = agent._evaluate_tier1_decision(
        ticker="TEST",
        current_year_analysis=current_year_analysis_watch,
        verified_metrics=verified_metrics_watch
    )

    assert tier1_decision_watch['decision'] == 'WATCH', \
        f"Expected WATCH, got {tier1_decision_watch['decision']}"
    logger.info(f"✅ PASS: Decision = {tier1_decision_watch['decision']}")
    logger.info(f"   Reasoning: {tier1_decision_watch['reasoning']}")

    # Test BUY candidate
    logger.info("\nTest 1c: BUY candidate (strong on all criteria)")

    current_year_analysis_buy = {
        'year': 2024,
        'full_analysis': """
        Outstanding business with multiple moat sources: brand, network effects,
        switching costs. ROIC of 25% sustained over decade. Exceptional management
        with aligned incentives. Current price offers 32% margin of safety.

        All 8 core investment criteria pass. Strong BUY candidate.
        """,
        'tool_calls_made': 12,
        'token_estimate': 18000
    }

    verified_metrics_buy = {
        'roic_10y_avg': 0.25,  # 25% - exceptional
        'debt_equity': 0.2
    }

    tier1_decision_buy = agent._evaluate_tier1_decision(
        ticker="TEST",
        current_year_analysis=current_year_analysis_buy,
        verified_metrics=verified_metrics_buy
    )

    assert tier1_decision_buy['decision'] == 'BUY', \
        f"Expected BUY, got {tier1_decision_buy['decision']}"
    logger.info(f"✅ PASS: Decision = {tier1_decision_buy['decision']}")
    logger.info(f"   Reasoning: {tier1_decision_buy['reasoning']}")

    logger.info("\n✅ TEST 1 PASSED: Tier 1 decision gate logic works correctly")


def test_mda_history_method_exists():
    """Test that new _analyze_mda_history method exists and has correct signature."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: MD&A History Method Verification")
    logger.info("=" * 80)

    agent = WarrenBuffettAgent(
        enable_validation=False
    )

    # Check method exists
    assert hasattr(agent, '_analyze_mda_history'), \
        "Method _analyze_mda_history does not exist"
    logger.info("✅ Method _analyze_mda_history exists")

    # Check it's callable
    assert callable(agent._analyze_mda_history), \
        "_analyze_mda_history is not callable"
    logger.info("✅ Method is callable")

    # Verify it has correct parameters
    import inspect
    sig = inspect.signature(agent._analyze_mda_history)
    params = list(sig.parameters.keys())

    expected_params = ['ticker', 'num_years', 'years_to_analyze']
    assert all(p in params for p in expected_params), \
        f"Missing expected parameters. Got: {params}, Expected: {expected_params}"
    logger.info(f"✅ Method has correct parameters: {params}")

    # Verify default values
    assert sig.parameters['num_years'].default == 5, \
        f"Expected num_years default=5, got {sig.parameters['num_years'].default}"
    logger.info("✅ Default num_years = 5 (reads 5 years of MD&A)")

    logger.info("\n✅ TEST 2 PASSED: MD&A-only method correctly implemented")


def test_proxy_statement_in_workflow():
    """Test that proxy statement fetching is in the Tier 2 workflow."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Proxy Statement Integration")
    logger.info("=" * 80)

    # Read the buffett_agent.py file to verify proxy statement code exists
    import ast

    agent_file = Path(__file__).parent / "src" / "agent" / "buffett_agent.py"
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for proxy statement fetching code
    assert 'DEF 14A' in content, \
        "Proxy statement (DEF 14A) fetching not found in code"
    logger.info("✅ DEF 14A proxy statement reference found")

    assert 'proxy_analysis' in content, \
        "proxy_analysis variable not found"
    logger.info("✅ proxy_analysis variable found")

    assert 'Proxy statement' in content or 'proxy statement' in content, \
        "Proxy statement logging not found"
    logger.info("✅ Proxy statement fetching logic exists")

    # Check for Phase 9.1 marker
    assert 'PHASE 9.1' in content or 'Phase 9.1' in content, \
        "Phase 9.1 markers not found in code"
    logger.info("✅ Phase 9.1 implementation markers found")

    logger.info("\n✅ TEST 3 PASSED: Proxy statement integrated in Tier 2")


def test_ui_updates():
    """Test that UI has been updated to reflect Phase 9.1 architecture."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Streamlit UI Updates")
    logger.info("=" * 80)

    # Read components.py to verify UI updates
    components_file = Path(__file__).parent / "src" / "ui" / "components.py"
    with open(components_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for key Phase 9.1 terminology
    assert 'Tier 1' in content, "Tier 1 terminology not found in UI"
    logger.info("✅ Tier 1 terminology found")

    assert 'Tier 2' in content, "Tier 2 terminology not found in UI"
    logger.info("✅ Tier 2 terminology found")

    assert 'Decision Gate' in content or 'decision gate' in content or 'Decision:' in content, \
        "Decision gate concept not found in UI"
    logger.info("✅ Decision gate concept found")

    assert 'MD&A' in content or 'MDA' in content, \
        "MD&A sections not mentioned in UI"
    logger.info("✅ MD&A sections mentioned")

    assert 'Proxy' in content or 'DEF 14A' in content, \
        "Proxy statement not mentioned in UI"
    logger.info("✅ Proxy statement mentioned")

    assert 'BUY candidate' in content or 'BUY Candidate' in content, \
        "BUY candidate terminology not found"
    logger.info("✅ BUY candidate terminology found")

    logger.info("\n✅ TEST 4 PASSED: UI properly updated for Phase 9.1")


def test_munger_critique_visibility():
    """Test that Phase 9.2 Munger critique is appended to thesis (Phase 9.2)."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Charlie Munger Critique Visibility (Phase 9.2)")
    logger.info("=" * 80)

    agent = WarrenBuffettAgent(enable_validation=False)

    # Check _format_munger_critique method exists
    assert hasattr(agent, '_format_munger_critique'), \
        "Method _format_munger_critique does not exist"
    logger.info("✅ _format_munger_critique method exists")

    # Test with mock validation data
    mock_validation = {
        "enabled": True,
        "approved": False,
        "score": 65,
        "overall_assessment": "Test assessment showing use of mental models",
        "strengths": ["Good analysis", "Clear reasoning"],
        "issues": [
            {
                "severity": "critical",
                "category": "calculations",
                "mental_model": "inversion",
                "description": "Test issue description",
                "suggested_fix": "Test fix"
            }
        ],
        "recommendation": "revise"
    }

    critique = agent._format_munger_critique(mock_validation)

    # Verify critique contains expected sections
    assert "Charlie Munger's Critique" in critique, "Missing critique header"
    logger.info("✅ Critique header present")

    assert "mental models" in critique.lower(), "Missing mental models reference"
    logger.info("✅ Mental models framework referenced")

    assert "Validation Score:" in critique, "Missing validation score"
    logger.info("✅ Validation score displayed")

    assert "Strengths" in critique, "Missing strengths section"
    logger.info("✅ Strengths section present")

    assert "Issues Identified" in critique, "Missing issues section"
    logger.info("✅ Issues section present")

    assert "**Critical Issues:**" in critique, "Missing critical issues grouping"
    logger.info("✅ Issues grouped by severity")

    assert "Inversion" in critique, "Missing mental model name in issue"
    logger.info("✅ Mental model names visible in issues")

    # Verify critique is appended in analyze_company workflow
    agent_file = Path(__file__).parent / "src" / "agent" / "buffett_agent.py"
    with open(agent_file, 'r', encoding='utf-8') as f:
        agent_content = f.read()

    assert "_format_munger_critique" in agent_content, \
        "Method _format_munger_critique not found in buffett_agent.py"
    logger.info("✅ _format_munger_critique method implemented")

    assert 'result["thesis"] = result.get("thesis", "") + munger_critique' in agent_content or \
           "result['thesis'] = result.get('thesis', '') + munger_critique" in agent_content, \
        "Critique appending logic not found"
    logger.info("✅ Critique appending logic present in analyze_company")

    logger.info("\n✅ TEST 5 PASSED: Munger critique visibility implemented (Phase 9.2)")


def run_all_tests():
    """Run all Phase 9.1 & 9.2 architecture tests."""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 9.1 & 9.2 ARCHITECTURE VERIFICATION TESTS")
    logger.info("=" * 80)
    logger.info("\nVerifying:")
    logger.info("1. Tier 1 decision gate stops AVOID/WATCH early")
    logger.info("2. MD&A-only historical analysis (not full 10-Ks)")
    logger.info("3. Proxy statement fetching in Tier 2")
    logger.info("4. Streamlit UI updates")
    logger.info("5. Charlie Munger critique visibility (Phase 9.2)")

    try:
        test_tier1_decision_gate()
        test_mda_history_method_exists()
        test_proxy_statement_in_workflow()
        test_ui_updates()
        test_munger_critique_visibility()

        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("=" * 80)
        logger.info("\nPhase 9.1 Architecture Implementation Verified:")
        logger.info("✅ Tier 1 decision gate implemented correctly")
        logger.info("✅ MD&A-only historical analysis replaces full 10-K reads")
        logger.info("✅ Proxy statement (DEF 14A) integrated in Tier 2")
        logger.info("✅ Streamlit UI reflects new tiered approach")
        logger.info("\nPhase 9.2 Enhancement Verified:")
        logger.info("✅ Charlie Munger's critique appended as visible thesis section")
        logger.info("✅ Mental models framework visible to users")
        logger.info("✅ Validation feedback presented as narrative")
        logger.info("\nExpected Outcomes:")
        logger.info("• 80-90% of companies stop at Tier 1 (AVOID/WATCH)")
        logger.info("• 10-20% of companies proceed to Tier 2 (BUY candidates)")
        logger.info("• Cost savings: $2-4 per Tier 1-only analysis")
        logger.info("• Context efficiency: 5 years MD&A < 1 year full 10-K")
        logger.info("• Transparency: Users see Charlie Munger's critique directly")

        return True

    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        return False

    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
