"""
Test Pydantic validation for Bug #12 scenario and other edge cases.

This test verifies that Pydantic catches invalid data assignments immediately.
"""

from src.agent.data_structures import AnalysisMetrics, AnalysisInsights


def test_bug12_roic_validation():
    """Test that Pydantic catches Bug #12 scenario (ROIC = $547.6M)."""
    print("=" * 80)
    print("TEST 1: Bug #12 Scenario - Assigning owner_earnings to ROIC")
    print("=" * 80)

    metrics = AnalysisMetrics()

    # Attempt Bug #12: Assign owner_earnings value to ROIC
    try:
        metrics.roic = 547600000.0  # $547.6M (should be 0.24 for 24%)
        print("[FAIL] Pydantic didn't catch invalid ROIC!")
        print(f"   ROIC value: {metrics.roic}")
        return False
    except Exception as e:  # Catch both ValueError and ValidationError
        print("[PASS] Pydantic caught invalid ROIC!")
        print(f"   Error: {e}")
        return True


def test_negative_roic():
    """Test that negative ROIC is rejected."""
    print("\n" + "=" * 80)
    print("TEST 2: Negative ROIC")
    print("=" * 80)

    try:
        metrics = AnalysisMetrics(roic=-0.15)
        print("[FAIL] Pydantic allowed negative ROIC!")
        return False
    except Exception as e:
        print("[PASS] Pydantic rejected negative ROIC!")
        print(f"   Error: {e}")
        return True


def test_margin_consistency():
    """Test that operating margin > gross margin is rejected."""
    print("\n" + "=" * 80)
    print("TEST 3: Margin Consistency (Operating > Gross)")
    print("=" * 80)

    try:
        metrics = AnalysisMetrics(
            gross_margin=0.30,      # 30% gross margin
            operating_margin=0.35   # 35% operating margin (IMPOSSIBLE!)
        )
        print("[FAIL] Pydantic allowed operating_margin > gross_margin!")
        return False
    except Exception as e:
        print("[PASS] Pydantic caught margin inconsistency!")
        print(f"   Error: {e}")
        return True


def test_valid_metrics():
    """Test that valid metrics are accepted."""
    print("\n" + "=" * 80)
    print("TEST 4: Valid Metrics (Should Pass)")
    print("=" * 80)

    try:
        metrics = AnalysisMetrics(
            roic=0.24,              # 24% ROIC
            debt_equity=0.45,       # 0.45 D/E
            gross_margin=0.40,      # 40% gross margin
            operating_margin=0.25,  # 25% operating margin
            net_margin=0.18,        # 18% net margin
            revenue=50000.0,        # $50B revenue
            current_price=150.0,    # $150/share
            margin_of_safety=0.25   # 25% MoS
        )
        print("[PASS] Valid metrics accepted!")
        print(f"   ROIC: {metrics.roic:.1%}")
        print(f"   D/E: {metrics.debt_equity:.2f}")
        print(f"   Margins: Gross={metrics.gross_margin:.1%}, Operating={metrics.operating_margin:.1%}, Net={metrics.net_margin:.1%}")
        return True
    except Exception as e:
        print("[FAIL] Valid metrics rejected!")
        print(f"   Error: {e}")
        return False


def test_insights_validation():
    """Test that AnalysisInsights enforces Literal values."""
    print("\n" + "=" * 80)
    print("TEST 5: Insights Validation (Literal Values)")
    print("=" * 80)

    # Test valid values
    try:
        insights = AnalysisInsights(
            decision="BUY",
            conviction="HIGH",
            moat_rating="STRONG",
            risk_rating="MODERATE"
        )
        print("[PASS] Valid insights accepted!")
        print(f"   Decision: {insights.decision}, Conviction: {insights.conviction}")
        print(f"   Moat: {insights.moat_rating}, Risk: {insights.risk_rating}")
    except Exception as e:
        print(f"[FAIL] Valid insights rejected: {e}")
        return False

    # Test invalid values
    try:
        insights = AnalysisInsights(
            decision="MAYBE",  # Invalid - only BUY/WATCH/AVOID allowed
            conviction="HIGH"
        )
        print("[FAIL] Pydantic allowed invalid decision 'MAYBE'!")
        return False
    except Exception as e:
        print("[PASS] Pydantic rejected invalid decision!")
        print(f"   Error: {e}")
        return True


def test_model_dump():
    """Test that model_dump() replaces to_dict()."""
    print("\n" + "=" * 80)
    print("TEST 6: model_dump() API (Replaces to_dict())")
    print("=" * 80)

    metrics = AnalysisMetrics(
        roic=0.24,
        revenue=50000.0,
        debt_equity=None  # None values
    )

    # Test model_dump(exclude_none=True)
    data = metrics.model_dump(exclude_none=True)

    if "roic" in data and "revenue" in data and "debt_equity" not in data:
        print("[PASS] model_dump(exclude_none=True) works correctly!")
        print(f"   Included: roic={data['roic']}, revenue={data['revenue']}")
        print(f"   Excluded: debt_equity (None)")
        return True
    else:
        print("[FAIL] model_dump() didn't work as expected!")
        print(f"   Data: {data}")
        return False


def main():
    """Run all Pydantic validation tests."""
    print("\n" + "=" * 80)
    print("PYDANTIC VALIDATION TEST SUITE")
    print("Testing Phase 7.7 Pydantic Integration")
    print("=" * 80 + "\n")

    results = []

    results.append(("Bug #12 ROIC Validation", test_bug12_roic_validation()))
    results.append(("Negative ROIC Rejection", test_negative_roic()))
    results.append(("Margin Consistency", test_margin_consistency()))
    results.append(("Valid Metrics Acceptance", test_valid_metrics()))
    results.append(("Insights Literal Validation", test_insights_validation()))
    results.append(("model_dump() API", test_model_dump()))

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
        print("\n*** All Pydantic validation tests PASSED!")
        print("[OK] Bug #12 would be caught immediately")
        print("[OK] Data quality guaranteed by Pydantic")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
