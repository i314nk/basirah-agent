"""
Test validator enhancements for Phase 7.7 structured data validation.

This test verifies that validator_checks.py correctly validates:
- Quantitative claims
- Decision consistency
- Completeness
- Trend claims
"""

from src.agent.validator_checks import (
    validate_quantitative_claims,
    validate_decision_consistency,
    validate_completeness,
    validate_trend_claims,
    run_all_validations
)


def test_quantitative_validation():
    """Test quantitative claims validation."""
    print("=" * 80)
    print("TEST 1: Quantitative Validation")
    print("=" * 80)

    # Test case: Unrealistic ROIC (Bug #12 scenario)
    structured_metrics = {
        "current_year": {
            "year": 2024,
            "metrics": {
                "roic": 5.476,  # 547.6% (unrealistic!)
                "gross_margin": 0.30,
                "operating_margin": 0.35,  # Operating > Gross (impossible!)
                "net_margin": 0.25,
                "free_cash_flow": 1000.0,
                "owner_earnings": 500.0,  # 100% difference
                "debt_equity": -0.5,  # Negative (impossible!)
                "current_price": 150.0,
                "dcf_intrinsic_value": 200.0
            }
        }
    }

    result = validate_quantitative_claims(structured_metrics)

    print(f"\nPassed: {result['passed']}")
    print(f"Errors: {len(result['errors'])}")
    for error in result['errors']:
        print(f"  - {error}")
    print(f"Warnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")

    # Should catch 3 errors: unrealistic ROIC, margin inconsistency, negative debt
    expected_errors = ["ROIC is", "Operating margin", "Debt/Equity"]
    found_errors = 0
    for expected in expected_errors:
        if any(expected in err for err in result['errors']):
            found_errors += 1

    if found_errors >= 2:  # At least 2 of the 3 errors caught
        print("\n[PASS] Quantitative validation caught major errors!")
        return True
    else:
        print("\n[FAIL] Quantitative validation missed errors!")
        return False


def test_decision_consistency_buy():
    """Test BUY decision consistency validation."""
    print("\n" + "=" * 80)
    print("TEST 2: BUY Decision Consistency")
    print("=" * 80)

    # Test case: BUY decision with weak fundamentals
    structured_metrics = {
        "current_year": {
            "year": 2024,
            "metrics": {
                "roic": 0.08,  # 8% (Buffett requires >15%)
                "margin_of_safety": 0.05,  # 5% (Buffett requires >20%)
                "debt_equity": 1.5
            }
        }
    }

    structured_insights = {
        "current_year": {
            "year": 2024,
            "insights": {
                "moat_rating": "WEAK",  # Buffett requires STRONG+
                "risk_rating": "HIGH"  # High risk for BUY
            }
        }
    }

    result = validate_decision_consistency(
        decision="BUY",
        conviction="MODERATE",  # Not HIGH
        structured_metrics=structured_metrics,
        structured_insights=structured_insights
    )

    print(f"\nPassed: {result['passed']}")
    print(f"Warnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")

    # Should catch 5 warnings: weak moat, low ROIC, low MoS, HIGH risk, MODERATE conviction
    expected_warnings = ["moat", "ROIC", "Margin of Safety", "risk rating", "conviction"]
    found_warnings = 0
    for expected in expected_warnings:
        if any(expected in warn for warn in result['warnings']):
            found_warnings += 1

    if found_warnings >= 3:  # At least 3 of the 5 warnings
        print("\n[PASS] Decision consistency validation caught BUY issues!")
        return True
    else:
        print("\n[FAIL] Decision consistency validation missed BUY issues!")
        return False


def test_decision_consistency_avoid():
    """Test AVOID decision consistency validation."""
    print("\n" + "=" * 80)
    print("TEST 3: AVOID Decision Consistency")
    print("=" * 80)

    # Test case: AVOID decision without clear reason (SHOULD warn)
    structured_metrics = {
        "current_year": {
            "year": 2024,
            "metrics": {
                "roic": 0.25,  # 25% (good!)
                "debt_equity": 0.3  # Low debt (good!)
            }
        }
    }

    structured_insights = {
        "current_year": {
            "year": 2024,
            "insights": {
                "moat_rating": "STRONG",  # Good moat
                "risk_rating": "LOW"
            }
        }
    }

    result = validate_decision_consistency(
        decision="AVOID",
        conviction="HIGH",
        structured_metrics=structured_metrics,
        structured_insights=structured_insights
    )

    print(f"\nPassed: {result['passed']}")
    print(f"Warnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")

    # Should warn about AVOID decision without clear red flags
    if any("AVOID decision" in warn for warn in result['warnings']):
        print("\n[PASS] Decision consistency caught questionable AVOID!")
        return True
    else:
        print("\n[FAIL] Decision consistency missed questionable AVOID!")
        return False


def test_completeness_validation():
    """Test completeness validation."""
    print("\n" + "=" * 80)
    print("TEST 4: Completeness Validation")
    print("=" * 80)

    # Test case: Missing required fields
    structured_metrics = {
        "current_year": {
            "year": 2024,
            "metrics": {
                "revenue": 50000.0,
                # Missing: roic, operating_margin, debt_equity
            }
        }
    }

    structured_insights = {
        "current_year": {
            "year": 2024,
            "insights": {
                "decision": "BUY",
                "conviction": "HIGH"
                # Missing: moat_rating, risk_rating
            }
        }
    }

    result = validate_completeness(structured_metrics, structured_insights)

    print(f"\nPassed: {result['passed']}")
    print(f"Warnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")

    # Should warn about missing metrics and insights
    metrics_missing = any("missing" in warn.lower() and "metrics" in warn.lower() for warn in result['warnings'])
    insights_missing = any("missing" in warn.lower() and "insights" in warn.lower() for warn in result['warnings'])

    if metrics_missing and insights_missing:
        print("\n[PASS] Completeness validation caught missing fields!")
        return True
    else:
        print("\n[FAIL] Completeness validation missed missing fields!")
        return False


def test_trend_validation():
    """Test trend claims validation."""
    print("\n" + "=" * 80)
    print("TEST 5: Trend Validation")
    print("=" * 80)

    # Test case: Claims "rapid revenue growth" but actual CAGR is 3%
    thesis = """
    This company shows rapid revenue growth with expanding margins.
    The business model is scalable and management is executing well.
    """

    structured_metrics = {
        "all_years": [
            {"year": 2024, "metrics": {"revenue": 10300.0, "operating_margin": 0.20}},
            {"year": 2023, "metrics": {"revenue": 10000.0, "operating_margin": 0.21}},
            {"year": 2022, "metrics": {"revenue": 9700.0, "operating_margin": 0.22}},
            {"year": 2021, "metrics": {"revenue": 9400.0, "operating_margin": 0.23}},
            {"year": 2020, "metrics": {"revenue": 9100.0, "operating_margin": 0.24}},
        ]
    }
    # Revenue CAGR: ~3.2% (NOT rapid!)
    # Operating margin: DECLINING from 24% to 20% (NOT expanding!)

    result = validate_trend_claims(thesis, structured_metrics)

    print(f"\nPassed: {result['passed']}")
    print(f"Warnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")

    # Should catch 2 warnings: revenue claim unsupported, margin claim unsupported
    revenue_warning = any("rapid revenue growth" in warn.lower() for warn in result['warnings'])
    margin_warning = any("margin" in warn.lower() for warn in result['warnings'])

    if revenue_warning and margin_warning:
        print("\n[PASS] Trend validation caught unsupported claims!")
        return True
    else:
        print("\n[FAIL] Trend validation missed unsupported claims!")
        return False


def test_run_all_validations():
    """Test the orchestrator function."""
    print("\n" + "=" * 80)
    print("TEST 6: run_all_validations() Orchestrator")
    print("=" * 80)

    # Test case: Comprehensive analysis with multiple issues
    analysis_result = {
        "thesis": "This company shows rapid revenue growth with expanding margins.",
        "decision": "BUY",
        "conviction": "MODERATE",
        "metadata": {
            "structured_metrics": {
                "current_year": {
                    "year": 2024,
                    "metrics": {
                        "roic": 0.10,  # 10% (too low for BUY)
                        "revenue": 50000.0,
                        "operating_margin": 0.25,
                        "gross_margin": 0.40,
                        "margin_of_safety": 0.05,  # 5% (too low for BUY)
                        "debt_equity": 0.8
                    }
                },
                "all_years": [
                    {"year": 2024, "metrics": {"revenue": 10300.0, "operating_margin": 0.20}},
                    {"year": 2023, "metrics": {"revenue": 10000.0, "operating_margin": 0.21}},
                    {"year": 2022, "metrics": {"revenue": 9700.0, "operating_margin": 0.22}},
                    {"year": 2021, "metrics": {"revenue": 9400.0, "operating_margin": 0.23}},
                    {"year": 2020, "metrics": {"revenue": 9100.0, "operating_margin": 0.24}},
                ]
            },
            "structured_insights": {
                "current_year": {
                    "year": 2024,
                    "insights": {
                        "moat_rating": "MODERATE",  # Not STRONG for BUY
                        "risk_rating": "MODERATE",
                        "decision": "BUY",
                        "conviction": "MODERATE"
                    }
                }
            }
        }
    }

    result = run_all_validations(analysis_result)

    print(f"\nOverall Passed: {result['overall_passed']}")
    print(f"Total Errors: {result['total_errors']}")
    print(f"Total Warnings: {result['total_warnings']}")

    print("\nBreakdown:")
    for check_name in ["quantitative", "decision_consistency", "completeness", "trends"]:
        check_result = result.get(check_name, {})
        errors = len(check_result.get("errors", []))
        warnings = len(check_result.get("warnings", []))
        print(f"  {check_name}: {errors} errors, {warnings} warnings")

    # Should have multiple warnings (BUY with weak fundamentals, unsupported trend claims)
    if result['total_warnings'] >= 3:
        print("\n[PASS] run_all_validations() caught multiple issues!")
        return True
    else:
        print("\n[FAIL] run_all_validations() missed issues!")
        return False


def main():
    """Run all validator enhancement tests."""
    print("\n" + "=" * 80)
    print("VALIDATOR ENHANCEMENT TEST SUITE")
    print("Testing Phase 7.7 Validator Enhancements")
    print("=" * 80 + "\n")

    results = []

    results.append(("Quantitative Validation", test_quantitative_validation()))
    results.append(("BUY Decision Consistency", test_decision_consistency_buy()))
    results.append(("AVOID Decision Consistency", test_decision_consistency_avoid()))
    results.append(("Completeness Validation", test_completeness_validation()))
    results.append(("Trend Validation", test_trend_validation()))
    results.append(("run_all_validations()", test_run_all_validations()))

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
        print("\n*** All validator enhancement tests PASSED!")
        print("[OK] Quantitative checks working")
        print("[OK] Decision consistency enforced")
        print("[OK] Completeness validated")
        print("[OK] Trend claims verified")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
