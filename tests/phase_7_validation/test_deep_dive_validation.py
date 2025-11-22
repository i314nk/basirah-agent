"""
Test deep dive analysis with Phase 7.6B validation.

This script runs a deep dive analysis on ZTS (Zoetis) and displays
the validation results to verify the validator correctly evaluates
deep dive analyses.
"""

import sys
from src.agent.buffett_agent import WarrenBuffettAgent


def main():
    print("=" * 80)
    print("Phase 7.6B Deep Dive Validation Test")
    print("=" * 80)
    print("\nTesting: ZTS (Zoetis Inc.)")
    print("Analysis Type: Deep Dive (3 years)")
    print("Validation: ENABLED (expecting full Buffett methodology)")
    print("\n" + "=" * 80)
    print()

    # Initialize agent with validation enabled
    agent = WarrenBuffettAgent(enable_validation=True, max_validation_iterations=3)

    # Run deep dive analysis
    print("Starting deep dive analysis...\n")
    result = agent.analyze_company(
        ticker="ZTS",
        deep_dive=True,
        years_to_analyze=3  # 3 years for faster testing
    )

    # Display analysis results
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print(f"\nTicker: {result['ticker']}")
    print(f"Decision: {result['decision']}")
    print(f"Conviction: {result.get('conviction', 'N/A')}")
    print(f"Intrinsic Value: ${result.get('intrinsic_value', 'N/A')}")
    print(f"Current Price: ${result.get('current_price', 'N/A')}")
    if result.get('margin_of_safety'):
        mos_pct = result['margin_of_safety'] * 100
        print(f"Margin of Safety: {mos_pct:.1f}%")

    # Display validation results
    validation = result.get("validation", {})
    if not validation.get("enabled", False):
        print("\n⚠️ Validation was not enabled!")
        return 1

    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print(f"\nScore: {validation.get('score', 0)}/100")
    print(f"Approved: {'✅ YES' if validation.get('approved') else '❌ NO'}")
    print(f"Recommendation: {validation.get('recommendation', 'unknown').upper()}")

    print(f"\nOverall Assessment:")
    print(f"  {validation.get('overall_assessment', 'No assessment provided')}")

    # Display methodology flags
    print(f"\nMethodology Checks:")
    print(f"  Methodology Correct: {'✅' if validation.get('methodology_correct') else '❌'}")
    print(f"  Calculations Complete: {'✅' if validation.get('calculations_complete') else '❌'}")
    print(f"  Sources Adequate: {'✅' if validation.get('sources_adequate') else '❌'}")
    print(f"  Buffett Principles Followed: {'✅' if validation.get('buffett_principles_followed') else '❌'}")

    # Display strengths
    strengths = validation.get('strengths', [])
    if strengths:
        print(f"\nStrengths ({len(strengths)}):")
        for i, strength in enumerate(strengths, 1):
            print(f"  {i}. {strength}")

    # Display issues
    issues = validation.get('issues', [])
    if issues:
        print(f"\nIssues Found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            severity = issue.get('severity', 'unknown').upper()
            category = issue.get('category', 'unknown')
            description = issue.get('description', '')
            how_to_fix = issue.get('how_to_fix', '')

            # Color code by severity
            if severity == 'CRITICAL':
                marker = "🔴"
            elif severity == 'IMPORTANT':
                marker = "🟡"
            else:
                marker = "🟢"

            print(f"\n  {marker} Issue {i} [{severity}] {category}")
            print(f"     Problem: {description}")
            print(f"     Fix: {how_to_fix}")
    else:
        print("\n✅ No issues found!")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if validation.get('approved'):
        print("\n✅ SUCCESS: Analysis APPROVED by validator")
        print(f"   The deep dive met quality standards (score ≥ 85)")
    else:
        print("\n⚠️ NEEDS IMPROVEMENT: Analysis NOT approved")
        print(f"   Score: {validation.get('score', 0)}/100 (need ≥ 85 to approve)")

        critical_count = sum(1 for issue in issues if issue.get('severity') == 'critical')
        important_count = sum(1 for issue in issues if issue.get('severity') == 'important')
        minor_count = sum(1 for issue in issues if issue.get('severity') == 'minor')

        print(f"   Issues: {critical_count} critical, {important_count} important, {minor_count} minor")

        if critical_count > 0:
            print("\n   Critical issues must be fixed:")
            for issue in issues:
                if issue.get('severity') == 'critical':
                    print(f"   - {issue.get('category')}: {issue.get('description')}")

    print("\n" + "=" * 80)
    print()

    # Return exit code
    return 0 if validation.get('approved') else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
