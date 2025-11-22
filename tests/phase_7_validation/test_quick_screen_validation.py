"""
Test quick screen validation with the fixed validator.

This script loads the HSY quick screen analysis and re-validates it
with the corrected validator that properly detects quick screen type.
"""

import json
from src.agent.prompts import get_validator_prompt
from src.llm import LLMClient
from src.llm.base import LLMMessage


def main():
    print("=" * 80)
    print("Quick Screen Validation Test (FIXED)")
    print("=" * 80)
    print("\nLoading HSY quick screen analysis...")

    # Load the HSY quick screen analysis
    with open('basirah_analyses/quick_screen/investigate/HSY_2025-11-11_investigate_183830.json', 'r') as f:
        analysis = json.load(f)

    print(f"Ticker: {analysis['ticker']}")
    print(f"Analysis Type (from metadata): {analysis['metadata']['analysis_type']}")
    print(f"Original Validation Score: {analysis['validation']['score']}/100")
    print(f"Original Issues: {len(analysis['validation']['issues'])}")

    print("\n" + "=" * 80)
    print("Re-validating with FIXED validator...")
    print("=" * 80)

    # Get validator prompt
    prompt = get_validator_prompt(analysis, iteration=0)

    # Check that it's using quick screen criteria
    if "IMPORTANT - Quick Screen" in prompt:
        print("\n✅ Validator correctly detected QUICK SCREEN")
        print("   - Using relaxed criteria (no Owner Earnings/DCF required)")
    else:
        print("\n❌ Validator still using deep dive criteria!")
        return 1

    # Show key differences
    print("\nKey Validation Changes:")
    if "Owner Earnings, DCF, and detailed MoS calculations NOT required" in prompt:
        print("  ✅ Owner Earnings, DCF, MoS: NOT REQUIRED (correct for quick screen)")
    if "IMPORTANT - Quick Screen" in prompt:
        print("  ✅ ROIC calculation: SHOULD be shown (with source)")
    if "Quick screens should be efficient" in prompt:
        print("  ✅ Efficiency valued: Don't penalize for lack of deep analysis")

    print("\n" + "=" * 80)
    print("Calling Validator LLM...")
    print("=" * 80)

    # Initialize LLM client
    llm_client = LLMClient()

    # Call validator
    messages = [LLMMessage(role="user", content=prompt)]
    response = llm_client.provider.generate(
        messages=messages,
        max_tokens=8000,
        temperature=0.0
    )

    # Parse response
    import re
    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
    if not json_match:
        print("❌ Failed to parse validator response")
        return 1

    critique = json.loads(json_match.group(0))

    # Display results
    print("\n" + "=" * 80)
    print("NEW VALIDATION RESULTS")
    print("=" * 80)

    print(f"\nScore: {critique.get('score', 0)}/100")
    print(f"Approved: {'✅ YES' if critique.get('approved') else '❌ NO'}")
    print(f"Recommendation: {critique.get('recommendation', 'unknown').upper()}")

    print(f"\nOverall Assessment:")
    print(f"  {critique.get('overall_assessment', 'No assessment')}")

    # Show score change
    old_score = analysis['validation']['score']
    new_score = critique.get('score', 0)
    score_change = new_score - old_score

    print(f"\nScore Comparison:")
    print(f"  Old (with bug): {old_score}/100")
    print(f"  New (fixed):    {new_score}/100")
    print(f"  Change:         {'+' if score_change >= 0 else ''}{score_change} points")

    # Show issues
    new_issues = critique.get('issues', [])
    old_issues = analysis['validation']['issues']

    print(f"\nIssues Comparison:")
    print(f"  Old: {len(old_issues)} issues")
    print(f"  New: {len(new_issues)} issues")

    # Count by severity
    old_critical = sum(1 for i in old_issues if i.get('severity') == 'critical')
    new_critical = sum(1 for i in new_issues if i.get('severity') == 'critical')

    print(f"\n  Critical Issues:")
    print(f"    Old: {old_critical}")
    print(f"    New: {new_critical}")

    # Show new issues
    if new_issues:
        print(f"\nRemaining Issues ({len(new_issues)}):")
        for i, issue in enumerate(new_issues, 1):
            severity = issue.get('severity', 'unknown').upper()
            category = issue.get('category', 'unknown')
            description = issue.get('description', '')

            marker = "🔴" if severity == 'CRITICAL' else "🟡" if severity == 'IMPORTANT' else "🟢"
            print(f"\n  {marker} [{severity}] {category}")
            print(f"     {description[:120]}...")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if new_score >= 85:
        print("\n✅ SUCCESS: Quick screen now APPROVED!")
    elif new_score > old_score:
        print(f"\n✅ IMPROVEMENT: Score increased by {score_change} points")
        print(f"   Still needs work to reach 85+ threshold")
    else:
        print(f"\n⚠️ No improvement (or decreased)")

    print()
    return 0 if new_score >= 85 else 1


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
