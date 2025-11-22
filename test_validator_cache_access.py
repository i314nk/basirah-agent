"""
Test validator cache access feature.

Verifies that the validator prompt includes cached tool outputs
for verification without redundant API calls.
"""

from src.agent.prompts import get_validator_prompt
import json


def test_cache_access_in_prompt():
    """Test that validator prompt includes cached tool outputs."""
    print("=" * 80)
    print("TEST: Validator Cache Access")
    print("=" * 80)

    # Mock analysis result with tool cache
    analysis_result = {
        "ticker": "LULU",
        "thesis": "Lululemon has a strong brand...",
        "decision": "BUY",
        "conviction": "HIGH",
        "metadata": {
            "analysis_type": "deep_dive",
            "tool_cache": {
                "gurufocus_summary": {
                    "roic": 0.32,
                    "revenue": 8800.0,
                    "operating_margin": 0.18,
                    "debt_equity": 0.12
                },
                "calculator": {
                    "owner_earnings": {
                        "result": 800000000.0,
                        "per_share": 6.25
                    },
                    "roic": {
                        "result": 0.32,
                        "nopat": 810000000.0,
                        "invested_capital": 2530000000.0
                    },
                    "dcf": {
                        "intrinsic_value": 125.50,
                        "margin_of_safety": 0.25
                    }
                },
                "sec_10k_full": "LULULEMON ATHLETICA INC. - Form 10-K... (very long filing text...)",
                "web_search_recent_news": {
                    "results": [
                        {"title": "Lululemon expands to Asia", "date": "2024-01-15"}
                    ]
                }
            },
            "structured_metrics": {
                "current_year": {
                    "year": 2024,
                    "metrics": {
                        "roic": 0.32,
                        "revenue": 8800.0,
                        "operating_margin": 0.18
                    }
                }
            },
            "structured_insights": {
                "current_year": {
                    "year": 2024,
                    "insights": {
                        "decision": "BUY",
                        "conviction": "HIGH",
                        "moat_rating": "STRONG"
                    }
                }
            }
        }
    }

    # Generate validator prompt
    prompt = get_validator_prompt(analysis_result, iteration=0)

    print(f"\n[INFO] Generated prompt length: {len(prompt):,} characters")

    # Test 1: Check for cache section header
    if "CACHED TOOL OUTPUTS" in prompt:
        print("[PASS] Cache section header present")
    else:
        print("[FAIL] Cache section header missing")
        return False

    # Test 2: Check for GuruFocus data
    if "GuruFocus Data (Cached)" in prompt:
        print("[PASS] GuruFocus cache section present")
    else:
        print("[FAIL] GuruFocus cache section missing")
        return False

    # Test 3: Check for Calculator data
    if "Calculator Outputs (Cached)" in prompt:
        print("[PASS] Calculator cache section present")
    else:
        print("[FAIL] Calculator cache section missing")
        return False

    # Test 4: Check for SEC filings
    if "SEC Filings (Cached)" in prompt:
        print("[PASS] SEC filings cache section present")
    else:
        print("[FAIL] SEC filings cache section missing")
        return False

    # Test 5: Check for Web Search results
    if "Web Search Results (Cached)" in prompt:
        print("[PASS] Web search cache section present")
    else:
        print("[FAIL] Web search cache section missing")
        return False

    # Test 6: Check for structured data (Phase 7.7)
    if "Structured Data (Phase 7.7 - Pydantic Validated)" in prompt:
        print("[PASS] Structured data section present")
    else:
        print("[FAIL] Structured data section missing")
        return False

    # Test 7: Check for verification protocol instructions
    if "IMPORTANT VERIFICATION PROTOCOL" in prompt:
        print("[PASS] Verification protocol instructions present")
    else:
        print("[FAIL] Verification protocol instructions missing")
        return False

    # Test 8: Verify specific ROIC value is in prompt (from cache)
    if "0.32" in prompt or "32%" in prompt or '"roic": 0.32' in prompt:
        print("[PASS] Cached ROIC value (0.32) found in prompt")
    else:
        print("[FAIL] Cached ROIC value not found")
        return False

    # Test 9: Verify DCF intrinsic value is in prompt
    if "125.50" in prompt or "125.5" in prompt:
        print("[PASS] Cached DCF intrinsic value ($125.50) found in prompt")
    else:
        print("[FAIL] Cached DCF intrinsic value not found")
        return False

    # Test 10: Verify structured metrics included
    if '"year": 2024' in prompt and '"revenue": 8800' in prompt:
        print("[PASS] Structured metrics from Phase 7.7 found in prompt")
    else:
        print("[FAIL] Structured metrics not found")
        return False

    print("\n[INFO] Sample cache section from prompt:")
    print("=" * 80)

    # Extract and display a portion of the cache section
    cache_start = prompt.find("CACHED TOOL OUTPUTS")
    if cache_start >= 0:
        cache_end = prompt.find("ANALYSIS TO REVIEW", cache_start)
        cache_section = prompt[cache_start:cache_end] if cache_end >= 0 else prompt[cache_start:cache_start+2000]

        # Show first 1500 chars of cache section (ASCII safe)
        preview = cache_section[:1500].replace('\u2500', '-').replace('\u2501', '=')
        print(preview)
        if len(cache_section) > 1500:
            print(f"\n[... {len(cache_section) - 1500} more characters ...]")

    print("=" * 80)

    return True


def test_empty_cache():
    """Test that prompt still works with empty tool cache."""
    print("\n" + "=" * 80)
    print("TEST: Empty Tool Cache Handling")
    print("=" * 80)

    analysis_result = {
        "ticker": "TEST",
        "thesis": "Test analysis",
        "decision": "WATCH",
        "conviction": "MODERATE",
        "metadata": {
            "analysis_type": "quick_screen",
            "tool_cache": {}  # Empty cache
        }
    }

    prompt = get_validator_prompt(analysis_result, iteration=0)

    # Should NOT have cache section if cache is empty
    if "CACHED TOOL OUTPUTS" not in prompt:
        print("[PASS] No cache section when cache is empty (correct behavior)")
        return True
    else:
        print("[FAIL] Cache section present even with empty cache")
        return False


def test_missing_cache():
    """Test that prompt works when tool_cache is missing entirely."""
    print("\n" + "=" * 80)
    print("TEST: Missing Tool Cache Handling")
    print("=" * 80)

    analysis_result = {
        "ticker": "TEST",
        "thesis": "Test analysis",
        "decision": "WATCH",
        "conviction": "MODERATE",
        "metadata": {
            "analysis_type": "quick_screen"
            # No tool_cache key at all
        }
    }

    try:
        prompt = get_validator_prompt(analysis_result, iteration=0)

        # Should NOT crash and should NOT have cache section
        if "CACHED TOOL OUTPUTS" not in prompt:
            print("[PASS] No cache section when tool_cache missing (correct behavior)")
            return True
        else:
            print("[FAIL] Cache section present without tool_cache")
            return False
    except Exception as e:
        print(f"[FAIL] Exception raised: {e}")
        return False


def main():
    """Run all validator cache access tests."""
    print("\n" + "=" * 80)
    print("VALIDATOR CACHE ACCESS TEST SUITE")
    print("Testing Phase 7.7 Validator Cache Access Feature")
    print("=" * 80 + "\n")

    results = []

    results.append(("Cache Access in Prompt", test_cache_access_in_prompt()))
    results.append(("Empty Cache Handling", test_empty_cache()))
    results.append(("Missing Cache Handling", test_missing_cache()))

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
        print("\n*** All validator cache access tests PASSED!")
        print("[OK] Validator can access cached tool outputs")
        print("[OK] Validator can verify claims using same data")
        print("[OK] Prevents redundant API calls")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
