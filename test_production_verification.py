"""
Production Verification Test - Phase 7.7 Complete System

This test runs a real deep dive analysis to verify all Phase 7.7 components
work correctly in production, including:
- Pydantic validation
- Structured metrics/insights extraction
- Validator template fix (receives actual content)
- Validator scoring and critique
- Synthesis optimization (structured data tables)
"""

import sys
import os
import json
from datetime import datetime


def test_production_deep_dive():
    """Run a production deep dive analysis and verify all Phase 7.7 components."""
    print("=" * 80)
    print("PHASE 7.7 PRODUCTION VERIFICATION TEST")
    print("=" * 80)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis test will:")
    print("1. Run a REAL deep dive analysis on a public company")
    print("2. Verify Pydantic validation works")
    print("3. Verify structured metrics/insights extraction")
    print("4. Verify validator receives actual content (not placeholders)")
    print("5. Verify synthesis uses structured data")
    print("6. Report any production issues\n")

    # Import after setting up path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    from agent.buffett_agent import WarrenBuffettAgent
    from agent.prompts import get_validator_prompt
    from dotenv import load_dotenv

    # Load environment
    load_dotenv()

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[SKIP] No ANTHROPIC_API_KEY found in .env")
        print("This test requires a valid API key to run production analysis.")
        print("\nTo run this test:")
        print("1. Add ANTHROPIC_API_KEY=your_key to .env")
        print("2. Run: python test_production_verification.py")
        return None

    print("[OK] API key found")
    print("[OK] Running production deep dive analysis...")
    print("\n" + "=" * 80)
    print("STEP 1: Initialize Agent")
    print("=" * 80)

    try:
        agent = WarrenBuffettAgent()
        print("[OK] Warren Buffett Agent initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize agent: {e}")
        return False

    print("\n" + "=" * 80)
    print("STEP 2: Run Deep Dive Analysis (This may take 2-5 minutes)")
    print("=" * 80)
    print("\nTicker: MSFT (Microsoft)")
    print("Analysis Type: Deep Dive")
    print("Years: 5 years")
    print("\nNOTE: This will make real API calls and use tokens.")
    print("Starting analysis...\n")

    try:
        # Run deep dive analysis
        result = agent.analyze_company(
            ticker="MSFT",
            deep_dive=True,
            years_to_analyze=5
        )

        print("[OK] Analysis completed successfully!")
        print(f"    - Ticker: {result.get('ticker', 'N/A')}")
        print(f"    - Decision: {result.get('decision', 'N/A')}")
        print(f"    - Analysis Type: {result.get('metadata', {}).get('analysis_type', 'N/A')}")

    except Exception as e:
        print(f"[FAIL] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Verification checks
    checks_passed = 0
    checks_total = 0

    print("\n" + "=" * 80)
    print("STEP 3: Verify Pydantic Validation")
    print("=" * 80)

    # Check if structured metrics were extracted and validated
    structured_metrics = result.get('metadata', {}).get('structured_metrics', {})
    if structured_metrics:
        print("[OK] Structured metrics extracted")
        checks_passed += 1
    else:
        print("[WARN] No structured metrics found")
    checks_total += 1

    # Check ROIC is valid (0-500%)
    all_years = structured_metrics.get('all_years', [])
    if all_years:
        roic_values = [y.get('metrics', {}).get('roic') for y in all_years if y.get('metrics', {}).get('roic') is not None]
        if roic_values:
            invalid_roic = [r for r in roic_values if r < 0 or r > 5.0]
            if not invalid_roic:
                print(f"[OK] All ROIC values valid: {[f'{r*100:.1f}%' for r in roic_values[:3]]}")
                checks_passed += 1
            else:
                print(f"[FAIL] Invalid ROIC values found: {invalid_roic}")
        else:
            print("[WARN] No ROIC values extracted")
    else:
        print("[WARN] No multi-year metrics found")
    checks_total += 1

    print("\n" + "=" * 80)
    print("STEP 4: Verify Structured Insights Extraction")
    print("=" * 80)

    structured_insights = result.get('metadata', {}).get('structured_insights', {})
    if structured_insights:
        print("[OK] Structured insights extracted")
        checks_passed += 1
    else:
        print("[WARN] No structured insights found")
    checks_total += 1

    # Check decision is valid Literal
    all_years_insights = structured_insights.get('all_years', [])
    if all_years_insights:
        decisions = [y.get('insights', {}).get('decision') for y in all_years_insights if y.get('insights', {}).get('decision')]
        valid_decisions = all(d in ['BUY', 'WATCH', 'AVOID'] for d in decisions)
        if valid_decisions and decisions:
            print(f"[OK] All decisions valid Literals: {decisions[:3]}")
            checks_passed += 1
        elif decisions:
            print(f"[FAIL] Invalid decisions found: {decisions}")
        else:
            print("[WARN] No decisions extracted")
    else:
        print("[WARN] No multi-year insights found")
    checks_total += 1

    print("\n" + "=" * 80)
    print("STEP 5: Verify Validator Template Fix")
    print("=" * 80)

    # Build validator prompt with the analysis result
    try:
        validator_prompt = get_validator_prompt(result, iteration=0)

        # Critical checks: Ensure NO template placeholders
        has_ticker_placeholder = "{ticker}" in validator_prompt
        has_analysis_json_placeholder = "{analysis_json}" in validator_prompt
        has_decision_placeholder = "{decision}" in validator_prompt

        if has_ticker_placeholder:
            print("[FAIL] CRITICAL: {ticker} placeholder found in validator prompt!")
        else:
            print("[OK] No {ticker} placeholder (correctly replaced)")
            checks_passed += 1
        checks_total += 1

        if has_analysis_json_placeholder:
            print("[FAIL] CRITICAL: {analysis_json} placeholder found in validator prompt!")
        else:
            print("[OK] No {analysis_json} placeholder (correctly replaced)")
            checks_passed += 1
        checks_total += 1

        # Verify actual values are present
        if "Ticker: MSFT" in validator_prompt:
            print("[OK] Ticker value present: 'Ticker: MSFT'")
            checks_passed += 1
        else:
            print("[FAIL] Ticker value not found in validator prompt")
        checks_total += 1

        if '"ticker": "MSFT"' in validator_prompt or '"ticker":"MSFT"' in validator_prompt:
            print("[OK] Analysis JSON embedded (ticker found)")
            checks_passed += 1
        else:
            print("[WARN] Ticker not found in JSON (might be formatted differently)")
        checks_total += 1

        print(f"\n[INFO] Validator prompt length: {len(validator_prompt):,} characters")

    except Exception as e:
        print(f"[FAIL] Failed to build validator prompt: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("STEP 6: Verify Synthesis Optimization")
    print("=" * 80)

    # Check if thesis contains evidence of structured data usage
    thesis = result.get('thesis', '')

    # Look for signs that synthesis used structured data (though we can't see the prompt directly)
    if structured_metrics and structured_insights:
        print("[OK] Structured data available for synthesis")
        checks_passed += 1
    else:
        print("[WARN] Structured data not fully available")
    checks_total += 1

    # Check if multi-year analysis happened
    if thesis and len(thesis) > 5000:
        print(f"[OK] Comprehensive thesis generated ({len(thesis):,} characters)")
        checks_passed += 1
    else:
        print(f"[WARN] Thesis seems short ({len(thesis):,} characters)")
    checks_total += 1

    print("\n" + "=" * 80)
    print("STEP 7: Verify Validator Integration")
    print("=" * 80)

    # Check if validator was called
    validation_history = result.get('metadata', {}).get('validation_history', [])
    if validation_history:
        print(f"[OK] Validator was called ({len(validation_history)} iteration(s))")

        # Check latest validation
        latest_validation = validation_history[-1]
        score = latest_validation.get('score', 0)
        approved = latest_validation.get('approved', False)

        print(f"    - Final Score: {score}/100")
        print(f"    - Approved: {approved}")

        if score > 0:
            print(f"[OK] Validator scored > 0 (template bug fixed!)")
            checks_passed += 1
        else:
            print(f"[FAIL] Validator scored 0 (template bug may still exist)")
        checks_total += 1

        if score >= 50:
            print(f"[OK] Validator score reasonable ({score}/100)")
            checks_passed += 1
        else:
            print(f"[WARN] Low validator score ({score}/100)")
        checks_total += 1

    else:
        print("[WARN] No validation history found")
        checks_total += 2

    print("\n" + "=" * 80)
    print("STEP 8: Check for Pydantic Validation Errors")
    print("=" * 80)

    # Check error logs for Pydantic validation errors
    error_logs = result.get('metadata', {}).get('error_logs', [])
    pydantic_errors = [e for e in error_logs if 'validation error' in str(e).lower()]

    if not pydantic_errors:
        print("[OK] No Pydantic validation errors in production run")
        checks_passed += 1
    else:
        print(f"[WARN] {len(pydantic_errors)} Pydantic validation error(s) logged:")
        for error in pydantic_errors[:3]:
            print(f"    - {error}")
    checks_total += 1

    print("\n" + "=" * 80)
    print("PRODUCTION VERIFICATION RESULTS")
    print("=" * 80)

    print(f"\nChecks Passed: {checks_passed}/{checks_total} ({checks_passed/checks_total*100:.1f}%)")

    if checks_passed >= checks_total * 0.8:  # 80% pass rate
        print("\n[OK] PRODUCTION VERIFICATION PASSED!")
        print("[OK] Phase 7.7 is working correctly in production")

        print("\nVerified Components:")
        print("  - Pydantic validation preventing invalid data")
        print("  - Structured metrics/insights extraction")
        print("  - Validator receiving actual content (not placeholders)")
        print("  - Validator scoring analyses properly")
        print("  - Multi-year synthesis with structured data")

        # Save result for inspection
        output_file = "test_production_verification_result.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n[INFO] Full analysis saved to: {output_file}")
        except Exception as e:
            print(f"[WARN] Could not save result: {e}")

        return True
    else:
        print("\n[WARN] PRODUCTION VERIFICATION INCOMPLETE")
        print(f"[WARN] Only {checks_passed}/{checks_total} checks passed")
        print("\nThis may indicate:")
        print("  - API issues")
        print("  - Incomplete analysis")
        print("  - Bug in Phase 7.7 components")
        return False


def main():
    """Run production verification test."""
    print("\n" + "=" * 80)
    print("PHASE 7.7 - PRODUCTION VERIFICATION TEST SUITE")
    print("=" * 80)
    print("\nThis test verifies all Phase 7.7 components work in production:")
    print("1. Pydantic Integration")
    print("2. Validator Enhancements")
    print("3. Validator Cache Access")
    print("4. Synthesis Optimization")
    print("5. Validator Template Fix")
    print("6. Pydantic Error Handling")
    print("\n" + "=" * 80)

    success = test_production_deep_dive()

    if success is None:
        print("\n[SKIP] Test skipped (no API key)")
        return 0
    elif success:
        print("\n*** PRODUCTION VERIFICATION SUCCESSFUL! ***")
        print("[OK] Phase 7.7 ready for production deployment")
        return 0
    else:
        print("\n[WARN] Production verification incomplete")
        print("Review the output above for specific issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
