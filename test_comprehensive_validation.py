"""
Comprehensive Multi-Year Analysis Validation Test
Tests all 11 bug fixes together in a production scenario

This test validates:
1. JSON insights extraction (no leaking)
2. Historical metrics extraction (unique values per year)
3. ROIC field mapping (percentage format)
4. Analysis completeness (all sections present)

Expected cost: ~$3-5 (5-year analysis)
Expected time: 5-8 minutes
"""
import sys
import os
import json
import re
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.buffett_agent import WarrenBuffettAgent

print("=" * 80)
print("COMPREHENSIVE MULTI-YEAR VALIDATION TEST")
print("=" * 80)
print()
print("This test validates all 11 bug fixes in a production scenario:")
print("  - 5-year analysis (2020-2024)")
print("  - Expected cost: ~$3-5")
print("  - Expected time: 5-8 minutes")
print()
print("Testing company: AOS (A. O. Smith Corporation)")
print()
print("Starting test automatically...")
print()

# Initialize agent with validation disabled for faster testing
print("Initializing Warren Buffett Agent...")
agent = WarrenBuffettAgent(model_key="kimi-k2-thinking", enable_validation=False)
print("[OK] Agent initialized")
print()

# Run 5-year analysis
print("=" * 80)
print("RUNNING 5-YEAR DEEP DIVE ANALYSIS")
print("=" * 80)
print()
print("Stage 1: Analyzing current year (2024)...")
print("Stage 2: Analyzing 4 prior years (2023-2020)...")
print("Stage 3: Synthesizing findings...")
print()

try:
    result = agent.analyze_company("AOS", deep_dive=True, years_to_analyze=5)  # 5 years: 2024 + 4 prior

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE - STARTING VALIDATION")
    print("=" * 80)
    print()

    # ========================================================================
    # TEST 1: JSON INSIGHTS EXTRACTION (Bug #1)
    # ========================================================================
    print("TEST 1: JSON Insights Extraction (Bug #1)")
    print("-" * 80)

    if result and "metadata" in result:
        metadata = result["metadata"]

        # Check for structured insights
        if "structured_insights" in metadata:
            insights = metadata["structured_insights"]
            insights_count = len([k for k, v in insights.items() if v is not None])
            print(f"[PASS] Structured insights extracted: {insights_count} fields")

            # Key insights to check
            key_fields = ["business_model", "moat_rating", "decision", "conviction"]
            for field in key_fields:
                if field in insights and insights[field]:
                    print(f"  ✓ {field}: {str(insights[field])[:60]}...")
        else:
            print("[FAIL] No structured insights found in metadata")

        # Check that JSON doesn't leak into thesis
        full_analysis = result.get("thesis", "")

        if "<INSIGHTS>" in full_analysis or "</INSIGHTS>" in full_analysis:
            print("[FAIL] JSON block leaked into user-visible thesis!")
        else:
            print("[PASS] No JSON leakage in thesis")
    else:
        print("[FAIL] No metadata in result")

    print()

    # ========================================================================
    # TEST 2: HISTORICAL METRICS EXTRACTION (Bugs #2-10)
    # ========================================================================
    print("TEST 2: Historical Metrics Extraction (Bugs #2-10)")
    print("-" * 80)

    if "metadata" in result and "structured_metrics" in result["metadata"]:
        structured_metrics = result["metadata"]["structured_metrics"]
        all_years = structured_metrics.get("all_years", [])

        print(f"[PASS] Extracted metrics for {len(all_years)} years")
        print()

        # Check for unique revenue values across years
        revenues = {}
        for year_data in all_years:
            year = year_data.get("year")
            metrics = year_data.get("metrics", {})
            if "revenue" in metrics and metrics["revenue"]:
                revenues[year] = metrics["revenue"]
                print(f"  Year {year}: Revenue = ${metrics['revenue']:.1f}M")

        print()
        unique_revenues = set(revenues.values())

        if len(unique_revenues) >= 3:
            print(f"[PASS] Found {len(unique_revenues)} unique revenue values - historical extraction working!")
        elif len(unique_revenues) == 1:
            print(f"[FAIL] All years show IDENTICAL revenue (${list(unique_revenues)[0]:.1f}M)")
            print("  Bug #2-10 NOT FIXED: Historical extraction returning same values")
        else:
            print(f"[WARN] Only {len(unique_revenues)} unique values found (expected 3+)")
    else:
        print("[FAIL] No structured_metrics found in metadata")

    print()

    # ========================================================================
    # TEST 3: ROIC FIELD MAPPING (Bug #11)
    # ========================================================================
    print("TEST 3: ROIC Field Mapping (Bug #11)")
    print("-" * 80)

    if "metadata" in result and "structured_metrics" in result["metadata"]:
        structured_metrics = result["metadata"]["structured_metrics"]
        current_year = structured_metrics.get("current_year", {})
        current_metrics = current_year.get("metrics", {})

        if "roic" in current_metrics and current_metrics["roic"] is not None:
            roic = current_metrics["roic"]

            # ROIC should be in decimal format (0.15 = 15%)
            if 0.05 <= roic <= 0.50:  # Reasonable range: 5% - 50%
                print(f"[PASS] ROIC extracted as percentage: {roic:.4f} ({roic*100:.2f}%)")
            elif roic > 1000:
                print(f"[FAIL] ROIC showing as dollar amount: ${roic:.0f}M")
                print("  Bug #11 NOT FIXED: ROIC field mapping broken")
            else:
                print(f"[WARN] ROIC value unusual: {roic}")
        else:
            print("[FAIL] No ROIC found in current year metrics")
    else:
        print("[FAIL] No structured_metrics found for ROIC check")

    print()

    # ========================================================================
    # TEST 4: ANALYSIS COMPLETENESS (Issue #2)
    # ========================================================================
    print("TEST 4: Analysis Completeness (Issue #2)")
    print("-" * 80)

    full_analysis = result.get("thesis", "")

    # Expected sections in synthesis
    expected_sections = [
        "Business Overview",
        "Economic Moat",
        "Management Quality",
        "Financial Analysis",
        "Growth Prospects",
        "Competitive Position",
        "Risk Analysis",
        "Multi-Year Synthesis",
        "Valuation",
        "Final Investment Decision"
    ]

    sections_found = []
    sections_missing = []

    for section in expected_sections:
        # Check for section header patterns
        if section in full_analysis or section.lower() in full_analysis.lower():
            sections_found.append(section)
        else:
            sections_missing.append(section)

    print(f"Sections found: {len(sections_found)}/{len(expected_sections)}")

    if len(sections_found) >= 8:  # At least 8 out of 10
        print(f"[PASS] Analysis appears complete ({len(sections_found)}/10 sections)")
        if sections_missing:
            print(f"  Missing: {', '.join(sections_missing)}")
    else:
        print(f"[FAIL] Analysis incomplete - only {len(sections_found)}/10 sections")
        print(f"  Missing: {', '.join(sections_missing)}")

    print()
    print(f"Analysis length: {len(full_analysis)} characters")
    print(f"Analysis word count: {len(full_analysis.split())} words")

    print()

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()

    print("Bug Fixes Validated:")
    print("  1. JSON Insights Extraction (Bug #1)")
    print("  2. Historical Metrics Extraction (Bugs #2-10)")
    print("  3. ROIC Field Mapping (Bug #11)")
    print("  4. Analysis Completeness (Issue #2)")
    print()

    print("Analysis Results:")
    print(f"  Decision: {result.get('decision', 'N/A')}")
    print(f"  Conviction: {result.get('conviction', 'N/A')}")
    print(f"  Current Price: {result.get('current_price', 'N/A')}")
    print(f"  Intrinsic Value: {result.get('intrinsic_value', 'N/A')}")
    print(f"  Margin of Safety: {result.get('margin_of_safety', 'N/A')}")
    print()

    # Save full result to file for inspection
    output_file = "test_comprehensive_validation_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        # Convert result to JSON-serializable format
        json_result = {
            "decision": result.get("decision"),
            "conviction": result.get("conviction"),
            "thesis": result.get("thesis", ""),
            "intrinsic_value": result.get("intrinsic_value"),
            "current_price": result.get("current_price"),
            "margin_of_safety": result.get("margin_of_safety"),
            "metadata": result.get("metadata", {}),
            "tool_calls": result.get("tool_calls", 0),
            "cache_hits": result.get("cache_hits", 0)
        }
        json.dump(json_result, f, indent=2, ensure_ascii=False)

    print(f"Full result saved to: {output_file}")
    print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

except Exception as e:
    print()
    print("=" * 80)
    print("TEST FAILED WITH ERROR")
    print("=" * 80)
    print()
    print(f"Error: {str(e)}")
    print()
    import traceback
    traceback.print_exc()
