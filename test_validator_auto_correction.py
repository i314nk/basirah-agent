"""
Test Validator Auto-Correction Using Cached Data

Tests the validator's ability to automatically correct analysis errors
using cached tool data as the source of truth.
"""

import sys
import json


def test_roic_correction():
    """Test auto-correction of ROIC using cached GuruFocus data."""
    print("=" * 80)
    print("TEST 1: ROIC Auto-Correction")
    print("=" * 80)

    from src.agent.validator_corrections import ValidatorCorrections

    # Mock analysis with incorrect ROIC
    analysis = {
        'ticker': 'MSFT',
        'roic': 0.256,  # INCORRECT: 25.6%
        'decision': 'BUY'
    }

    # Validator identified this issue
    validator_issues = [
        {
            'severity': 'important',
            'category': 'data',
            'description': 'ROIC is 25.6% in analysis but GuruFocus shows 22.4%'
        }
    ]

    # Cached GuruFocus data (source of truth)
    tool_cache = {
        'gurufocus_keyratios_MSFT': {
            'success': True,
            'data': {
                'metrics': {
                    'roic': 0.224,  # CORRECT: 22.4%
                    'operating_margin': 0.42,
                    'debt_equity': 0.25
                }
            }
        }
    }

    # Apply auto-correction
    corrector = ValidatorCorrections()
    corrected = corrector.auto_correct_analysis(analysis, validator_issues, tool_cache)

    # Verify correction
    print(f"\nOriginal ROIC: {analysis.get('roic', 'N/A'):.1%}")
    print(f"Cached ROIC (GuruFocus): 22.4%")
    print(f"Corrected ROIC: {corrected.get('roic', 'N/A'):.1%}")

    corrections_meta = corrected.get('metadata', {}).get('auto_corrections', {})
    total = corrections_meta.get('total_corrections', 0)
    corrections = corrections_meta.get('corrections', [])

    print(f"\nCorrections Applied: {total}")
    if corrections:
        for corr in corrections:
            print(f"  - {corr['field']}: {corr['old_value']} -> {corr['new_value']} (from {corr['source']})")

    # Verify
    success = (
        corrected['roic'] == 0.224 and
        total == 1 and
        corrections[0]['field'] == 'roic'
    )

    if success:
        print("\n[PASS] ROIC auto-correction working!")
        return True
    else:
        print("\n[FAIL] ROIC auto-correction failed")
        return False


def test_owner_earnings_correction():
    """Test auto-correction of Owner Earnings using GuruFocus components calculation."""
    print("\n" + "=" * 80)
    print("TEST 2: Owner Earnings Auto-Correction (Calculated from GuruFocus Components)")
    print("=" * 80)

    from src.agent.validator_corrections import ValidatorCorrections

    # Mock analysis with incorrect Owner Earnings
    analysis = {
        'ticker': 'MSFT',
        'owner_earnings': 78000,  # INCORRECT: $78B
        'decision': 'BUY'
    }

    # Validator identified this issue
    validator_issues = [
        {
            'severity': 'critical',
            'category': 'calculations',
            'description': 'Owner Earnings calculation appears incorrect'
        }
    ]

    # Cached GuruFocus data (TRUSTED source)
    # NOTE: Calculator tool is intentionally NOT used (it's LLM-generated, untrusted)
    # Owner Earnings = Net Income + D&A - CapEx - Change in WC
    # Expected: 97400 + 13900 - 44400 - 0 = 66,900 million ($66.9B)
    tool_cache = {
        'gurufocus_financials_MSFT': {
            'success': True,
            'data': {
                'financials': {
                    'net_income': [97400],  # FY2024: $97.4B (verified)
                    'depreciation_amortization': [13900],  # FY2024: $13.9B (verified)
                    'capex': [44400],  # FY2024: $44.4B (verified)
                    'working_capital_change': [0],  # Assume minimal change
                    'free_cash_flow': [74100],  # Available as fallback
                    'operating_cash_flow': [118500]
                }
            }
        }
    }

    # Apply auto-correction
    corrector = ValidatorCorrections()
    corrected = corrector.auto_correct_analysis(analysis, validator_issues, tool_cache)

    # Verify correction
    print(f"\nOriginal Owner Earnings: ${analysis.get('owner_earnings', 0)/1000:.1f}B")
    print(f"\nGuruFocus Components (VERIFIED):")
    print(f"  Net Income:       $97.4B")
    print(f"  + D&A:            $13.9B")
    print(f"  - CapEx:          $44.4B")
    print(f"  - Change in WC:   $0.0B")
    print(f"  = Owner Earnings: $66.9B")
    print(f"\nCorrected Owner Earnings: ${corrected.get('owner_earnings', 0)/1000:.1f}B")

    corrections_meta = corrected.get('metadata', {}).get('auto_corrections', {})
    total = corrections_meta.get('total_corrections', 0)

    # Expected: 97400 + 13900 - 44400 - 0 = 66900
    expected_oe = 66900

    success = (
        corrected['owner_earnings'] == expected_oe and
        total == 1
    )

    if success:
        print("\n[PASS] Owner Earnings auto-correction working (calculated from verified components)!")
        return True
    else:
        print(f"\n[FAIL] Owner Earnings auto-correction failed")
        print(f"  Expected: ${expected_oe/1000:.1f}B")
        print(f"  Got: ${corrected.get('owner_earnings', 0)/1000:.1f}B")
        return False


def test_multiple_corrections():
    """Test auto-correction of multiple fields at once."""
    print("\n" + "=" * 80)
    print("TEST 3: Multiple Auto-Corrections")
    print("=" * 80)

    from src.agent.validator_corrections import ValidatorCorrections

    # Mock analysis with multiple errors
    analysis = {
        'ticker': 'MSFT',
        'roic': 0.256,  # INCORRECT
        'revenue': 245000,  # INCORRECT
        'operating_margin': 0.45,  # INCORRECT
        'debt_equity': 0.50,  # INCORRECT
        'decision': 'BUY'
    }

    # Validator identified these issues
    validator_issues = [
        {
            'severity': 'important',
            'category': 'data',
            'description': 'ROIC is 25.6% but GuruFocus shows 22.4%'
        },
        {
            'severity': 'important',
            'category': 'data',
            'description': 'Revenue is $245B but GuruFocus shows $245.1B'
        },
        {
            'severity': 'important',
            'category': 'data',
            'description': 'Operating margin is 45% but GuruFocus shows 42%'
        },
        {
            'severity': 'important',
            'category': 'data',
            'description': 'Debt/Equity is 0.50 but GuruFocus shows 0.25'
        }
    ]

    # Cached data (source of truth)
    tool_cache = {
        'gurufocus_keyratios_MSFT': {
            'success': True,
            'data': {
                'metrics': {
                    'roic': 0.224,
                    'operating_margin': 0.42,
                    'debt_equity': 0.25
                }
            }
        },
        'gurufocus_financials_MSFT': {
            'success': True,
            'data': {
                'financials': {
                    'revenue': [245122]  # Latest
                }
            }
        }
    }

    # Apply auto-correction
    corrector = ValidatorCorrections()
    corrected = corrector.auto_correct_analysis(analysis, validator_issues, tool_cache)

    # Verify corrections
    print("\nCorrections Summary:")
    corrections_meta = corrected.get('metadata', {}).get('auto_corrections', {})
    total = corrections_meta.get('total_corrections', 0)
    corrections = corrections_meta.get('corrections', [])

    print(f"  Total Corrections: {total}")
    for corr in corrections:
        print(f"    - {corr['field']}: {corr['old_value']} -> {corr['new_value']}")

    # Verify all corrections applied
    success = (
        corrected['roic'] == 0.224 and
        corrected['revenue'] == 245122 and
        corrected['operating_margin'] == 0.42 and
        corrected['debt_equity'] == 0.25 and
        total == 4
    )

    if success:
        print("\n[PASS] Multiple auto-corrections working!")
        return True
    else:
        print(f"\n[FAIL] Expected 4 corrections, got {total}")
        return False


def test_no_correction_when_no_cache():
    """Test that no correction is applied when cached data is missing."""
    print("\n" + "=" * 80)
    print("TEST 4: Graceful Handling of Missing Cache")
    print("=" * 80)

    from src.agent.validator_corrections import ValidatorCorrections

    analysis = {
        'ticker': 'MSFT',
        'roic': 0.256,
        'decision': 'BUY'
    }

    validator_issues = [
        {
            'severity': 'important',
            'category': 'data',
            'description': 'ROIC value needs verification'
        }
    ]

    # Empty cache - no source data available
    tool_cache = {}

    # Apply auto-correction
    corrector = ValidatorCorrections()
    corrected = corrector.auto_correct_analysis(analysis, validator_issues, tool_cache)

    corrections_meta = corrected.get('metadata', {}).get('auto_corrections', {})
    total = corrections_meta.get('total_corrections', 0)

    print(f"\nCorrections Applied: {total}")
    print(f"Original ROIC: {analysis['roic']:.1%}")
    print(f"Corrected ROIC: {corrected['roic']:.1%}")

    # Verify no correction (cache was empty)
    success = (
        corrected['roic'] == 0.256 and  # Unchanged
        total == 0
    )

    if success:
        print("\n[PASS] Gracefully handled missing cache!")
        return True
    else:
        print("\n[FAIL] Unexpected correction without cache data")
        return False


def main():
    """Run all validator auto-correction tests."""
    print("\n" + "=" * 80)
    print("VALIDATOR AUTO-CORRECTION TEST SUITE")
    print("=" * 80)
    print("\nTesting automatic correction using cached data as source of truth...")
    print("=" * 80 + "\n")

    results = []

    results.append(("ROIC Correction", test_roic_correction()))
    results.append(("Owner Earnings Correction", test_owner_earnings_correction()))
    results.append(("Multiple Corrections", test_multiple_corrections()))
    results.append(("Graceful Cache Handling", test_no_correction_when_no_cache()))

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
        print("\n*** All validator auto-correction tests PASSED!")
        print("[OK] Auto-correction using cached data working correctly")
        print("[OK] Multiple corrections applied successfully")
        print("[OK] Graceful handling when cache is missing")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
