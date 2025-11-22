"""
Quick integration test for Pydantic & Validator implementation.
Tests if all components work together.
"""

import sys

def test_imports():
    """Test that all modules import correctly."""
    print("=" * 80)
    print("TEST: Module Imports")
    print("=" * 80)

    try:
        from src.agent.data_structures import AnalysisMetrics, AnalysisInsights
        print("[OK] data_structures imports")

        from src.agent.data_extractor import merge_metrics
        print("[OK] data_extractor imports")

        from src.agent.validator_checks import run_all_validations
        print("[OK] validator_checks imports")

        from src.agent.prompts import get_validator_prompt
        print("[OK] prompts imports")

        from src.agent.buffett_agent import WarrenBuffettAgent
        print("[OK] buffett_agent imports")

        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_basic():
    """Test basic Pydantic functionality."""
    print("\n" + "=" * 80)
    print("TEST: Pydantic Basic Functionality")
    print("=" * 80)

    try:
        from src.agent.data_structures import AnalysisMetrics, AnalysisInsights

        # Create metrics
        metrics = AnalysisMetrics(
            roic=0.24,
            revenue=50000.0,
            debt_equity=0.45
        )
        print(f"[OK] Created metrics: ROIC={metrics.roic}, Revenue={metrics.revenue}")

        # Test model_dump
        data = metrics.model_dump(exclude_none=True)
        print(f"[OK] model_dump() works: {len(data)} fields exported")

        # Create insights
        insights = AnalysisInsights(
            decision="BUY",
            conviction="HIGH",
            moat_rating="STRONG"
        )
        print(f"[OK] Created insights: {insights.decision} with {insights.conviction} conviction")

        return True
    except Exception as e:
        print(f"[FAIL] Pydantic error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validator_checks():
    """Test validator_checks module."""
    print("\n" + "=" * 80)
    print("TEST: Validator Checks")
    print("=" * 80)

    try:
        from src.agent.validator_checks import run_all_validations

        # Create mock analysis result
        analysis_result = {
            "thesis": "Test analysis",
            "decision": "BUY",
            "conviction": "HIGH",
            "metadata": {
                "structured_metrics": {
                    "current_year": {
                        "year": 2024,
                        "metrics": {
                            "roic": 0.24,
                            "revenue": 50000.0,
                            "operating_margin": 0.25,
                            "debt_equity": 0.45
                        }
                    },
                    "all_years": []
                },
                "structured_insights": {
                    "current_year": {
                        "year": 2024,
                        "insights": {
                            "decision": "BUY",
                            "conviction": "HIGH",
                            "moat_rating": "STRONG",
                            "risk_rating": "LOW"
                        }
                    }
                }
            }
        }

        # Run validation
        validation = run_all_validations(analysis_result)

        print(f"[OK] Validation ran successfully")
        print(f"     Errors: {validation['total_errors']}")
        print(f"     Warnings: {validation['total_warnings']}")
        print(f"     Passed: {validation['overall_passed']}")

        return True
    except Exception as e:
        print(f"[FAIL] Validator checks error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_merge_metrics():
    """Test merge_metrics with Pydantic."""
    print("\n" + "=" * 80)
    print("TEST: Merge Metrics (Pydantic)")
    print("=" * 80)

    try:
        from src.agent.data_extractor import merge_metrics
        from src.agent.data_structures import AnalysisMetrics

        m1 = AnalysisMetrics(roic=0.24, revenue=50000.0)
        m2 = AnalysisMetrics(debt_equity=0.45, operating_margin=0.25)

        merged = merge_metrics(m1, m2)

        print(f"[OK] Merged metrics:")
        print(f"     ROIC: {merged.roic}")
        print(f"     Revenue: {merged.revenue}")
        print(f"     D/E: {merged.debt_equity}")
        print(f"     Op Margin: {merged.operating_margin}")

        return True
    except Exception as e:
        print(f"[FAIL] Merge metrics error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validator_prompt():
    """Test validator prompt generation."""
    print("\n" + "=" * 80)
    print("TEST: Validator Prompt Generation")
    print("=" * 80)

    try:
        from src.agent.prompts import get_validator_prompt

        analysis = {
            "thesis": "Test thesis",
            "decision": "BUY",
            "conviction": "HIGH"
        }

        # Test without structured validation
        prompt1 = get_validator_prompt(analysis, 0)
        print(f"[OK] Generated prompt without validation: {len(prompt1)} chars")

        # Test with structured validation
        structured_validation = {
            "total_errors": 0,
            "total_warnings": 2,
            "quantitative": {"errors": [], "warnings": ["Test warning"]},
            "decision_consistency": {"errors": [], "warnings": []},
            "completeness": {"errors": [], "warnings": []},
            "trends": {"errors": [], "warnings": []}
        }

        prompt2 = get_validator_prompt(analysis, 0, structured_validation)
        print(f"[OK] Generated prompt with validation: {len(prompt2)} chars")

        if len(prompt2) > len(prompt1):
            print(f"[OK] Structured validation added to prompt (+{len(prompt2) - len(prompt1)} chars)")

        return True
    except Exception as e:
        print(f"[FAIL] Validator prompt error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUITE")
    print("Testing Pydantic & Validator Implementation Integration")
    print("=" * 80 + "\n")

    results = []

    results.append(("Module Imports", test_imports()))
    results.append(("Pydantic Basic", test_pydantic_basic()))
    results.append(("Validator Checks", test_validator_checks()))
    results.append(("Merge Metrics", test_merge_metrics()))
    results.append(("Validator Prompt", test_validator_prompt()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All integration tests PASSED!")
        print("Phase 7.7 implementation is working correctly.")
        return True
    else:
        print(f"\n[FAILURE] {total - passed} test(s) FAILED")
        print("There may be an issue with the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
