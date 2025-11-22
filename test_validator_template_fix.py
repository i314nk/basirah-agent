"""
Test: Validator Template Placeholder Fix

Verifies that the validator receives actual analysis content, not template placeholders.
This test reproduces the bug reported in user's validator logs.
"""

import sys
import json


def test_validator_prompt_has_actual_content():
    """Test that validator prompt contains actual analysis data, not placeholders."""
    print("=" * 80)
    print("TEST: Validator Receives Actual Content (Not Template Placeholders)")
    print("=" * 80)

    from src.agent.prompts import get_validator_prompt

    # Create realistic test analysis
    test_analysis = {
        "ticker": "AAPL",
        "decision": "BUY",
        "analysis_type": "deep_dive",
        "conviction": "HIGH",
        "intrinsic_value": 250.0,
        "current_price": 180.0,
        "margin_of_safety": 0.28,
        "roic": 0.45,
        "revenue": 394000.0,
        "operating_margin": 0.30,
        "debt_equity": 0.25,
        "thesis": "Apple has a wide moat from ecosystem lock-in...",
        "metadata": {
            "analysis_type": "deep_dive",
            "tool_cache": {}
        }
    }

    # Generate validator prompt
    prompt = get_validator_prompt(test_analysis, iteration=0)

    print(f"\nValidator prompt generated: {len(prompt):,} characters\n")

    # Critical checks: Ensure NO template placeholders exist
    errors = []
    warnings = []

    if "{ticker}" in prompt:
        errors.append("[FAIL] CRITICAL: {ticker} placeholder found in prompt")
    else:
        print("[PASS] No {ticker} placeholder")

    if "{analysis_type}" in prompt:
        errors.append("[FAIL] CRITICAL: {analysis_type} placeholder found in prompt")
    else:
        print("[PASS] No {analysis_type} placeholder")

    if "{decision}" in prompt:
        errors.append("[FAIL] CRITICAL: {decision} placeholder found in prompt")
    else:
        print("[PASS] No {decision} placeholder")

    if "{analysis_json}" in prompt:
        errors.append("[FAIL] CRITICAL: {analysis_json} placeholder found in prompt")
    else:
        print("[PASS] No {analysis_json} placeholder")

    # Verify actual values are present
    if "Ticker: AAPL" not in prompt:
        errors.append("[FAIL] CRITICAL: Ticker value not formatted in prompt")
    else:
        print("[PASS] Ticker value present: 'Ticker: AAPL'")

    if "Decision: BUY" not in prompt:
        errors.append("[FAIL] CRITICAL: Decision value not formatted in prompt")
    else:
        print("[PASS] Decision value present: 'Decision: BUY'")

    if "Analysis Type: deep_dive" not in prompt:
        errors.append("[FAIL] CRITICAL: Analysis Type not formatted in prompt")
    else:
        print("[PASS] Analysis Type present: 'Analysis Type: deep_dive'")

    # Verify analysis JSON is actually embedded
    if '"ticker": "AAPL"' not in prompt:
        errors.append("[FAIL] CRITICAL: Analysis JSON not embedded in prompt")
    else:
        print("[PASS] Analysis JSON embedded (found ticker in JSON)")

    if '"decision": "BUY"' not in prompt:
        warnings.append("[WARN] Warning: Decision not found in JSON (might be formatted differently)")
    else:
        print("[PASS] Decision found in JSON")

    # Print results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    if errors:
        print("\nCRITICAL ERRORS:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  {warning}")

    if not errors:
        print("\n[OK] ALL CHECKS PASSED!")
        print("[OK] Validator receives actual analysis content (not template placeholders)")
        print("\nBug Fix Verified:")
        print("  - Line 255: Added 'f' prefix to format string")
        print("  - Line 497: Added 'f' prefix to format string")
        print("  - Placeholders {ticker}, {analysis_type}, {decision}, {analysis_json} now replaced")
        return True
    else:
        print(f"\n[FAIL] TEST FAILED: {len(errors)} critical error(s)")
        return False


def test_validator_prompt_with_structured_validation():
    """Test that structured validation results are included correctly."""
    print("\n" + "=" * 80)
    print("TEST: Structured Validation Integration")
    print("=" * 80)

    from src.agent.prompts import get_validator_prompt

    test_analysis = {
        "ticker": "MSFT",
        "decision": "WATCH",
        "analysis_type": "deep_dive",
        "metadata": {}
    }

    # Include structured validation results
    structured_validation = {
        "total_errors": 2,
        "total_warnings": 3,
        "quantitative": {
            "errors": [
                "ROIC 547% exceeds maximum allowed 500%",
                "Operating margin 120% exceeds gross margin 100%"
            ],
            "warnings": [
                "Revenue CAGR -5% suggests declining business"
            ]
        },
        "decision_consistency": {
            "errors": [],
            "warnings": [
                "Decision BUY conflicts with low ROIC 8%"
            ]
        },
        "completeness": {
            "errors": [],
            "warnings": [
                "Missing field: moat_sources"
            ]
        }
    }

    prompt = get_validator_prompt(test_analysis, iteration=0, structured_validation=structured_validation)

    print(f"\nValidator prompt with structured validation: {len(prompt):,} characters\n")

    # Verify structured validation is included
    checks = [
        ("AUTOMATED QUANTITATIVE VALIDATION RESULTS" in prompt, "Validation header present"),
        ("CRITICAL ERRORS FOUND: 2" in prompt, "Error count shown"),
        ("WARNINGS FOUND: 3" in prompt, "Warning count shown"),
        ("ROIC 547%" in prompt, "Specific error included"),
        ("Decision BUY conflicts" in prompt, "Warning included")
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

    print(f"\nChecks: {passed}/{len(checks)} passed")

    return passed == len(checks)


def main():
    """Run all validator template fix tests."""
    print("\n" + "=" * 80)
    print("VALIDATOR TEMPLATE PLACEHOLDER BUG FIX - TEST SUITE")
    print("=" * 80)
    print("\nThis test verifies the fix for the critical bug where the validator")
    print("was receiving template placeholders like {analysis_json} instead of")
    print("actual analysis content.\n")

    results = []

    results.append(("Validator Prompt Formatting", test_validator_prompt_has_actual_content()))
    results.append(("Structured Validation Integration", test_validator_prompt_with_structured_validation()))

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
        print("\n*** All validator template fix tests PASSED!")
        print("[OK] Validator receives actual analysis content")
        print("[OK] Template placeholders correctly replaced")
        print("\nCRITICAL BUG FIXED:")
        print("  Before: Validator received '{analysis_json}' literal text")
        print("  After:  Validator receives actual JSON analysis data")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
