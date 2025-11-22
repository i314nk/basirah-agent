"""
Phase 7.7.4 Synthesis Optimization - Test Suite

Tests the structured data integration in synthesis prompt.
"""

import sys
import json


def test_structured_data_formatting():
    """Test that structured data is formatted correctly for synthesis."""
    print("=" * 80)
    print("TEST 1: Structured Data Formatting")
    print("=" * 80)

    from src.agent.buffett_agent import WarrenBuffettAgent
    from src.agent.data_structures import AnalysisMetrics, AnalysisInsights

    # Create test agent
    agent = WarrenBuffettAgent()

    # Create test data with metrics and insights for multiple years
    structured_metrics = {
        "current_year": {
            "year": 2024,
            "metrics": {
                "roic": 0.24,
                "revenue": 50000.0,
                "operating_margin": 0.25,
                "debt_equity": 0.45,
                "free_cash_flow": 8000.0,
                "current_price": 150.0,
                "margin_of_safety": 0.20
            }
        },
        "all_years": [
            {
                "year": 2024,
                "metrics": {
                    "roic": 0.24,
                    "revenue": 50000.0,
                    "operating_margin": 0.25,
                    "debt_equity": 0.45,
                    "free_cash_flow": 8000.0,
                    "current_price": 150.0,
                    "margin_of_safety": 0.20
                }
            },
            {
                "year": 2023,
                "metrics": {
                    "roic": 0.22,
                    "revenue": 45000.0,
                    "operating_margin": 0.23,
                    "debt_equity": 0.50,
                    "free_cash_flow": 7000.0,
                    "current_price": 140.0,
                    "margin_of_safety": 0.15
                }
            },
            {
                "year": 2022,
                "metrics": {
                    "roic": 0.20,
                    "revenue": 40000.0,
                    "operating_margin": 0.22,
                    "debt_equity": 0.55,
                    "free_cash_flow": 6000.0,
                    "current_price": 130.0,
                    "margin_of_safety": 0.10
                }
            }
        ]
    }

    structured_insights = {
        "current_year": {
            "year": 2024,
            "insights": {
                "decision": "BUY",
                "conviction": "HIGH",
                "moat_rating": "STRONG",
                "risk_rating": "LOW"
            }
        },
        "all_years": [
            {
                "year": 2024,
                "insights": {
                    "decision": "BUY",
                    "conviction": "HIGH",
                    "moat_rating": "STRONG",
                    "risk_rating": "LOW"
                }
            },
            {
                "year": 2023,
                "insights": {
                    "decision": "WATCH",
                    "conviction": "MODERATE",
                    "moat_rating": "MODERATE",
                    "risk_rating": "MODERATE"
                }
            },
            {
                "year": 2022,
                "insights": {
                    "decision": "WATCH",
                    "conviction": "MODERATE",
                    "moat_rating": "MODERATE",
                    "risk_rating": "MODERATE"
                }
            }
        ]
    }

    # Test _build_structured_data_section
    section = agent._build_structured_data_section(
        ticker="TEST",
        structured_metrics=structured_metrics,
        structured_insights=structured_insights
    )

    print("\nGenerated Structured Data Section:")
    print("=" * 80)
    print(section)
    print("=" * 80)

    # Verify section content
    checks = [
        ("PHASE 7.7.4: STRUCTURED DATA REFERENCE" in section, "Header present"),
        ("QUANTITATIVE METRICS (Validated via Pydantic)" in section, "Metrics table header"),
        ("QUALITATIVE INSIGHTS (Validated via Pydantic)" in section, "Insights table header"),
        ("2024" in section, "Year 2024 present"),
        ("2023" in section, "Year 2023 present"),
        ("2022" in section, "Year 2022 present"),
        ("24.0%" in section or "24%" in section, "ROIC 24% present"),
        ("Revenue CAGR" in section, "Revenue CAGR calculated"),
        ("ROIC Trend" in section, "ROIC trend calculated"),
        ("Operating Margin Trend" in section, "Margin trend calculated"),
        ("Decision Evolution" in section or "Decision Consistency" in section, "Decision evolution tracked"),
        ("Moat" in section and ("Strengthening" in section or "Stable" in section), "Moat evolution tracked")
    ]

    passed = 0
    failed = 0

    for check, description in checks:
        if check:
            print(f"[PASS] {description}")
            passed += 1
        else:
            print(f"[FAIL] {description}")
            failed += 1

    print(f"\nChecks passed: {passed}/{len(checks)}")

    return passed == len(checks)


def test_synthesis_prompt_integration():
    """Test that structured data is integrated into synthesis prompt."""
    print("\n" + "=" * 80)
    print("TEST 2: Synthesis Prompt Integration")
    print("=" * 80)

    from src.agent.buffett_agent import WarrenBuffettAgent

    # Create test agent
    agent = WarrenBuffettAgent()

    # Create test current year and prior years data
    current_year = {
        "year": 2024,
        "full_analysis": "Test analysis for 2024...",
        "metrics": {
            "roic": 0.24,
            "revenue": 50000.0
        },
        "insights": {
            "decision": "BUY",
            "conviction": "HIGH"
        }
    }

    prior_years = [
        {
            "year": 2023,
            "summary": "Test summary for 2023...",
            "metrics": {
                "roic": 0.22,
                "revenue": 45000.0
            },
            "insights": {
                "decision": "WATCH",
                "conviction": "MODERATE"
            }
        }
    ]

    # Build structured data
    structured_metrics = {
        "all_years": [
            {"year": 2024, "metrics": {"roic": 0.24, "revenue": 50000.0}},
            {"year": 2023, "metrics": {"roic": 0.22, "revenue": 45000.0}}
        ]
    }

    structured_insights = {
        "all_years": [
            {"year": 2024, "insights": {"decision": "BUY", "conviction": "HIGH"}},
            {"year": 2023, "insights": {"decision": "WATCH", "conviction": "MODERATE"}}
        ]
    }

    # Test _get_complete_thesis_prompt with structured data
    prompt = agent._get_complete_thesis_prompt(
        ticker="TEST",
        current_year=current_year,
        prior_years=prior_years,
        structured_metrics=structured_metrics,
        structured_insights=structured_insights
    )

    print(f"\nPrompt length: {len(prompt)} characters")

    # Verify prompt contains structured data
    checks = [
        ("PHASE 7.7.4: STRUCTURED DATA REFERENCE" in prompt, "Phase 7.7.4 header"),
        ("QUANTITATIVE METRICS" in prompt, "Metrics table"),
        ("QUALITATIVE INSIGHTS" in prompt, "Insights table"),
        ("Revenue CAGR" in prompt, "CAGR calculation"),
        ("Trend Indicators" in prompt, "Trend indicators"),
        ("Use these EXACT values" in prompt, "Usage instruction"),
        ("Do NOT re-parse numbers from text" in prompt, "Anti-reparsing instruction")
    ]

    passed = 0
    failed = 0

    for check, description in checks:
        if check:
            print(f"[PASS] {description}")
            passed += 1
        else:
            print(f"[FAIL] {description}")
            failed += 1

    print(f"\nChecks passed: {passed}/{len(checks)}")

    return passed == len(checks)


def test_empty_structured_data():
    """Test that synthesis works with empty/missing structured data."""
    print("\n" + "=" * 80)
    print("TEST 3: Empty Structured Data Handling")
    print("=" * 80)

    from src.agent.buffett_agent import WarrenBuffettAgent

    # Create test agent
    agent = WarrenBuffettAgent()

    # Test with None values
    section = agent._build_structured_data_section(
        ticker="TEST",
        structured_metrics=None,
        structured_insights=None
    )

    if section == "":
        print("[PASS] Empty string returned for None inputs")
        passed = 1
    else:
        print("[FAIL] Expected empty string for None inputs")
        passed = 0

    # Test with empty dicts
    section = agent._build_structured_data_section(
        ticker="TEST",
        structured_metrics={},
        structured_insights={}
    )

    if section == "":
        print("[PASS] Empty string returned for empty dict inputs")
        passed += 1
    else:
        print("[FAIL] Expected empty string for empty dict inputs")

    print(f"\nChecks passed: {passed}/2")

    return passed == 2


def test_trend_calculations():
    """Test that trend calculations work correctly."""
    print("\n" + "=" * 80)
    print("TEST 4: Trend Calculations")
    print("=" * 80)

    from src.agent.buffett_agent import WarrenBuffettAgent

    # Create test agent
    agent = WarrenBuffettAgent()

    # Test improving trends
    structured_metrics = {
        "all_years": [
            {
                "year": 2024,
                "metrics": {
                    "roic": 0.30,  # 30% (up from 20%)
                    "revenue": 60000.0,  # $60B (up from $40B)
                    "operating_margin": 0.35  # 35% (up from 25%)
                }
            },
            {
                "year": 2020,
                "metrics": {
                    "roic": 0.20,  # 20%
                    "revenue": 40000.0,  # $40B
                    "operating_margin": 0.25  # 25%
                }
            }
        ]
    }

    section = agent._build_structured_data_section(
        ticker="TEST",
        structured_metrics=structured_metrics,
        structured_insights=None
    )

    # Verify trend calculations
    checks = [
        ("Revenue CAGR" in section, "Revenue CAGR calculated"),
        ("10.7%" in section or "10.7" in section, "CAGR value ~10.7% present"),  # (60000/40000)^(1/4) - 1 = 10.67%
        ("improving" in section, "ROIC improving trend detected"),
        ("30.0%" in section, "Final ROIC 30% present"),
        ("20.0%" in section, "Initial ROIC 20% present"),
        ("expanding" in section, "Margin expanding trend detected")
    ]

    passed = 0
    failed = 0

    print("\nTrend Indicators Section:")
    print("-" * 80)
    trend_start = section.find("**Trend Indicators:**")
    if trend_start >= 0:
        trend_end = section.find("\n\n", trend_start)
        print(section[trend_start:trend_end])
    print("-" * 80)

    for check, description in checks:
        if check:
            print(f"[PASS] {description}")
            passed += 1
        else:
            print(f"[FAIL] {description}")
            failed += 1

    print(f"\nChecks passed: {passed}/{len(checks)}")

    return passed == len(checks)


def test_pydantic_validation_in_formatting():
    """Test that Pydantic validation works during formatting."""
    print("\n" + "=" * 80)
    print("TEST 5: Pydantic Validation During Formatting")
    print("=" * 80)

    from src.agent.buffett_agent import WarrenBuffettAgent

    # Create test agent
    agent = WarrenBuffettAgent()

    # Test with valid data
    structured_metrics = {
        "all_years": [
            {
                "year": 2024,
                "metrics": {
                    "roic": 0.24,  # Valid: 24%
                    "revenue": 50000.0,
                    "operating_margin": 0.25
                }
            }
        ]
    }

    section = agent._build_structured_data_section(
        ticker="TEST",
        structured_metrics=structured_metrics,
        structured_insights=None
    )

    check1 = "24.0%" in section or "24%" in section
    if check1:
        print("[PASS] Valid ROIC (24%) formatted correctly")
    else:
        print("[FAIL] Valid ROIC not formatted")

    # Test with invalid data (should handle gracefully)
    structured_metrics_invalid = {
        "all_years": [
            {
                "year": 2024,
                "metrics": {
                    "roic": -0.5,  # Invalid: negative ROIC (should be caught by Pydantic)
                    "revenue": 50000.0
                }
            }
        ]
    }

    try:
        section = agent._build_structured_data_section(
            ticker="TEST",
            structured_metrics=structured_metrics_invalid,
            structured_insights=None
        )
        # Should not crash, but may show "--" for invalid ROIC
        print("[PASS] Invalid data handled gracefully (no crash)")
        check2 = True
    except Exception as e:
        print(f"[FAIL] Crashed on invalid data: {e}")
        check2 = False

    passed = sum([check1, check2])
    print(f"\nChecks passed: {passed}/2")

    return passed == 2


def main():
    """Run all Phase 7.7.4 tests."""
    print("\n" + "=" * 80)
    print("PHASE 7.7.4 SYNTHESIS OPTIMIZATION TEST SUITE")
    print("Testing Structured Data Integration in Synthesis")
    print("=" * 80 + "\n")

    results = []

    results.append(("Structured Data Formatting", test_structured_data_formatting()))
    results.append(("Synthesis Prompt Integration", test_synthesis_prompt_integration()))
    results.append(("Empty Data Handling", test_empty_structured_data()))
    results.append(("Trend Calculations", test_trend_calculations()))
    results.append(("Pydantic Validation", test_pydantic_validation_in_formatting()))

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
        print("\n*** All Phase 7.7.4 tests PASSED!")
        print("[OK] Synthesis optimization working correctly")
        print("[OK] Structured data integrated into synthesis prompt")
        print("[OK] Trend calculations working")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
