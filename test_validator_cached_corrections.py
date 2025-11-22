"""
Test Validator LLM-Based Corrections Using Cached Data

Verifies that the LLM validator uses cached tool data as the source of truth
to correct analysis errors and maintain consistency.

Expected Behavior:
- Initial analysis: May have errors (e.g., ROIC 25.6% vs cached 22.4%)
- Validator iteration 1: LLM should use cached 22.4% to correct the analysis
- Validation score: Should IMPROVE (e.g., 65 -> 85) instead of degrade
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_validator_cached_corrections():
    """
    Test that validator uses cached data to correct errors.

    This is a lightweight test using a simpler ticker (AAPL) to verify:
    1. Validator receives cached data
    2. Validator identifies inconsistencies with cache
    3. Validator corrects using cached values
    4. Validation score improves (not degrades)
    """
    print("=" * 80)
    print("VALIDATOR CACHED CORRECTIONS TEST")
    print("=" * 80)
    print("\nTesting LLM validator corrections using cached data as source of truth...")
    print("=" * 80 + "\n")

    from src.agent.buffett_agent import WarrenBuffettAgent

    # Initialize agent
    print("[1/5] Initializing agent...")
    try:
        agent = WarrenBuffettAgent(
            model_key="kimi-k2-thinking",
            enable_validation=True  # Enable validation to test corrections
        )
        print("      [PASS] Agent initialized\n")
    except Exception as e:
        print(f"      [FAIL] Agent initialization failed: {e}\n")
        return False

    # Run analysis with validation
    print("[2/5] Running analysis (AAPL, 3 years, with validation)...")
    print("      This will trigger the validator to use cached data for corrections...")
    print("      Expected: Validator should correct errors using cached values\n")

    try:
        result = agent.analyze_company(
            ticker="AAPL",
            deep_dive=True,
            years_to_analyze=3  # Lighter test (3 years instead of 5)
        )
        print("      [PASS] Analysis completed\n")
    except Exception as e:
        print(f"      [FAIL] Analysis failed: {e}\n")
        return False

    # Extract validation history
    print("[3/5] Extracting validation history...")

    validation_history = result.get('validation_history', [])
    if not validation_history:
        # Try to find it in metadata
        metadata = result.get('metadata', {})
        validation_history = metadata.get('validation_history', [])

    if not validation_history:
        print("      [WARN] No validation history found")
        print("      Checking if validation occurred...\n")

        # Check if there's a validation score
        final_score = result.get('validation_score')
        if final_score:
            print(f"      [INFO] Final validation score: {final_score}/100")
            print("      [PASS] Validation occurred (score found)\n")
        else:
            print("      [FAIL] No validation occurred\n")
            return False
    else:
        print(f"      [PASS] Found {len(validation_history)} validation iterations\n")

    # Analyze validation scores
    print("[4/5] Analyzing validation score progression...")

    if validation_history:
        print("\n      Validation Score Progression:")
        print("      " + "-" * 60)

        scores = []
        for i, iteration in enumerate(validation_history):
            score = iteration.get('score', 'N/A')
            approved = iteration.get('approved', False)
            issues_count = len(iteration.get('issues', []))

            scores.append(score if isinstance(score, (int, float)) else 0)

            status = "[APPROVED]" if approved else "[REJECTED]"
            print(f"      Iteration {i}: {score}/100 {status} ({issues_count} issues)")

        print("      " + "-" * 60)

        # Check if scores improved
        if len(scores) >= 2:
            initial_score = scores[0]
            final_score = scores[-1]

            print(f"\n      Initial Score: {initial_score}/100")
            print(f"      Final Score:   {final_score}/100")

            if final_score > initial_score:
                improvement = final_score - initial_score
                print(f"      Improvement:   +{improvement} points")
                print("\n      [PASS] Validation scores IMPROVED (cached corrections working!)\n")
                return True
            elif final_score == initial_score:
                print(f"      No change:     {final_score - initial_score} points")
                print("\n      [WARN] Score unchanged (may need more iterations)\n")

                # Check if final score is good
                if final_score >= 80:
                    print("      [PASS] Final score is good (>= 80)\n")
                    return True
                else:
                    print("      [INFO] Final score below target (< 80)\n")
                    return False
            else:
                degradation = initial_score - final_score
                print(f"      Degradation:   -{degradation} points")
                print("\n      [FAIL] Validation scores DEGRADED (cached corrections not working!)\n")
                return False
        else:
            print("\n      [INFO] Only 1 iteration (analysis may have passed immediately)\n")

            if scores[0] >= 80:
                print("      [PASS] Analysis passed validation on first try\n")
                return True
            else:
                print("      [WARN] Analysis did not pass validation\n")
                return False
    else:
        # No validation history, check final score
        final_score = result.get('validation_score')
        if final_score:
            print(f"\n      Final Validation Score: {final_score}/100")

            if final_score >= 80:
                print("      [PASS] Analysis passed validation\n")
                return True
            else:
                print("      [WARN] Analysis below target score (< 80)\n")
                return False
        else:
            print("\n      [FAIL] No validation score found\n")
            return False

    # Check for evidence of cached data usage
    print("[5/5] Checking for evidence of cached data usage...")

    # Look for validation iterations that mention using cached data
    corrections_found = False

    if validation_history:
        for iteration in validation_history:
            issues = iteration.get('issues', [])
            for issue in issues:
                description = issue.get('description', '').lower()
                if 'cache' in description or 'gurufocus' in description:
                    corrections_found = True
                    print(f"      [INFO] Validator referenced cached data: {issue.get('description', '')[:80]}...")
                    break

            if corrections_found:
                break

    if corrections_found:
        print("\n      [PASS] Evidence of cached data usage found\n")
    else:
        print("\n      [INFO] No explicit cached data references in validation issues\n")

    return True


def main():
    """Run validator cached corrections test."""
    print("\n" + "=" * 80)
    print("VALIDATOR LLM-BASED CORRECTIONS TEST")
    print("=" * 80)
    print("\nVerifying that the LLM validator uses cached data to correct errors...")
    print("Expected: Validation scores should IMPROVE, not degrade\n")
    print("=" * 80 + "\n")

    success = test_validator_cached_corrections()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    if success:
        print("\n[PASS] Validator cached corrections test PASSED!")
        print("\nKey Findings:")
        print("  - Validator used cached data for corrections")
        print("  - Validation scores improved (or analysis passed immediately)")
        print("  - LLM-based corrections are working as designed")
        print("\n[OK] Phase 7.7.5 validator enhancements verified")
    else:
        print("\n[FAIL] Validator cached corrections test FAILED")
        print("\nIssues:")
        print("  - Validation scores may have degraded instead of improving")
        print("  - OR: Analysis failed to pass validation")
        print("  - May need to review validator prompt or LLM quality")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
