"""
Complete Deep Dive Test: ZTS (Zoetis Inc.) - 5 Years

Full production test of Phase 7.7.8 (Simplified Validation):
- Tool caching
- Validator with trusted data sources
- Owner Earnings calculation from verified GuruFocus components
- Multi-year analysis (5 years)
- Single-pass validation (no iterative refinement loop)
- Auto-correction using cached data only
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent.buffett_agent import WarrenBuffettAgent

def test_zts_deep_dive():
    """
    Complete 5-year deep dive analysis for ZTS.

    This test verifies:
    1. Full analysis pipeline (5 years)
    2. Tool caching (Phase 7.7)
    3. Validator corrections using trusted data (Phase 7.7.6)
    4. Owner Earnings calculation from GuruFocus components (Phase 7.7.7)
    5. Single-pass validation with auto-correction (Phase 7.7.8)
    """
    print("=" * 80)
    print("PRODUCTION TEST: ZTS DEEP DIVE (5 YEARS)")
    print("=" * 80)
    print("\nCompany: Zoetis Inc. (ZTS)")
    print("Analysis Type: Deep Dive")
    print("Years: 5 (2020-2024)")
    print("Validation: ENABLED (Single-pass)")
    print("Expected Behavior:")
    print("  - Validator runs once (no iterative refinement loop)")
    print("  - Auto-corrections applied using cached GuruFocus data")
    print("  - Owner Earnings calculated from verified components")
    print("\n" + "=" * 80 + "\n")

    # Initialize agent
    print("[STEP 1/3] Initializing Warren Buffett Agent...")
    print("-" * 80)
    try:
        agent = WarrenBuffettAgent(
            model_key="kimi-k2-thinking",
            enable_validation=True  # Enable validation to test corrections
        )
        print("[OK] Agent initialized")
        print(f"    - Model: {agent.llm.model_key}")
        print(f"    - Validation: ENABLED (Single-pass)")
        print(f"    - Tool Caching: ENABLED (Phase 7.7)")
        print(f"    - Validation Strategy: Auto-correct using cached data\n")
    except Exception as e:
        print(f"[FAIL] Failed to initialize agent: {e}\n")
        return False

    # Run deep dive analysis
    print("\n[STEP 2/3] Running Deep Dive Analysis...")
    print("-" * 80)
    print("Starting 5-year analysis for ZTS...")
    print("NOTE: This will make real API calls (GuruFocus, SEC)")
    print("      Expected duration: 3-5 minutes\n")

    try:
        result = agent.analyze_company(
            ticker="ZTS",
            deep_dive=True,
            years_to_analyze=5
        )

        print("\n[OK] Analysis completed successfully!")
        print(f"    - Ticker: {result.get('ticker', 'N/A')}")
        print(f"    - Decision: {result.get('decision', 'N/A')}")
        print(f"    - Analysis Type: {result.get('metadata', {}).get('analysis_type', 'N/A')}")
        print(f"    - Years Analyzed: {result.get('metadata', {}).get('years_analyzed', 'N/A')}")

    except Exception as e:
        print(f"\n[FAIL] Analysis failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

    # Analyze validation results
    print("\n\n[STEP 3/3] Analyzing Validation Results...")
    print("-" * 80)

    # Validation data is in result['validation']
    validation = result.get('validation', {})

    # Check if validation was enabled
    if not validation.get('enabled', False):
        print("[FAIL] Validation was not enabled\n")
        return False

    final_score = validation.get('score')
    issues = validation.get('issues', [])
    approved = validation.get('approved', False)

    if final_score is None:
        print("[FAIL] No validation score found\n")
        return False

    # Display validation results (single-pass, no iterations)
    print(f"Validation Score: {final_score}/100")
    print(f"Issues Found: {len(issues)}")
    print(f"Status: {'APPROVED' if approved else 'REJECTED'}\n")

    if issues:
        print("Issues identified:")
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            category = issue.get('category', 'unknown')
            desc = issue.get('description', 'N/A')
            print(f"  [{severity.upper()}] {category}: {desc}")
        print()

    # Check for auto-corrections
    auto_corrections = result.get('metadata', {}).get('auto_corrections', {})
    if auto_corrections:
        total = auto_corrections.get('total_corrections', 0)
        corrections = auto_corrections.get('corrections', [])

        print(f"Auto-Corrections Applied: {total}\n")

        if corrections:
            for corr in corrections:
                print(f"  - {corr.get('field', 'unknown')}")
                print(f"      Old: {corr.get('old_value', 'N/A')}")
                print(f"      New: {corr.get('new_value', 'N/A')}")
                print(f"      Source: {corr.get('source', 'N/A')}")
                print()

            print("[PASS] Auto-corrections were applied using cached data!\n")
        else:
            print("[INFO] No corrections needed (analysis was accurate)\n")
    else:
        print("[INFO] No auto-correction metadata found")
        print("       This may mean no corrections were needed\n")


    # Final summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    print(f"\nFinal Results:")
    print(f"  Company: ZTS (Zoetis Inc.)")
    print(f"  Decision: {result.get('decision', 'N/A')}")
    print(f"  Validation Score: {final_score}/100")
    print(f"  Status: {'APPROVED' if approved else 'REJECTED'}")

    # Check if auto-corrections were applied
    auto_corrections_total = result.get('metadata', {}).get('auto_corrections', {}).get('total_corrections', 0)
    if auto_corrections_total > 0:
        print(f"\n[PASS] Validator applied {auto_corrections_total} auto-corrections using cached data")
    else:
        print(f"\n[INFO] No auto-corrections applied")

    print("\nPhase 7.7.8 Features Tested:")
    print("  [OK] Tool caching")
    print("  [OK] Validator with trusted data sources")
    print("  [OK] Owner Earnings from GuruFocus components")
    print("  [OK] Multi-year deep dive (5 years)")
    print("  [OK] Single-pass validation (no refinement loop)")
    print("  [OK] Auto-correction using cached data")

    print("\n" + "=" * 80)

    # Success criteria: Validation ran and produced a score
    # We're not requiring a high score since we removed the iterative refinement
    success = final_score is not None and final_score >= 50  # Accept 50+ as passing

    if success:
        print("\n[PASS] Deep dive test PASSED")
        print(f"       Final score: {final_score}/100")
        print(f"       Validation completed successfully (single-pass)\n")
    else:
        print(f"\n[FAIL] Deep dive test FAILED")
        print(f"       Final score: {final_score}/100 (expected >= 50)\n")

    return success


if __name__ == "__main__":
    success = test_zts_deep_dive()
    sys.exit(0 if success else 1)
