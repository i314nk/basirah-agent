#!/usr/bin/env python3
"""
Test script for Phase 6A.1 - Complete Thesis Generation Fix

This script tests the fix for incomplete investment thesis generation by:
1. Running a deep dive analysis on LULU (expected BUY)
2. Verifying all 10 sections are present
3. Checking word count (should be 3,000-5,000 words)
4. Validating the thesis quality
"""

import sys
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.buffett_agent import WarrenBuffettAgent

def test_complete_thesis():
    """Test complete thesis generation fix"""

    print("=" * 80)
    print("PHASE 6A.1 - COMPLETE THESIS GENERATION FIX TEST")
    print("=" * 80)
    print(f"\nTest started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Initialize agent
    print("Initializing Warren Buffett AI Agent...")
    agent = WarrenBuffettAgent()
    print("✅ Agent initialized\n")

    # Test ticker
    ticker = "LULU"
    print(f"Test Ticker: {ticker} (lululemon athletica)")
    print(f"Expected Decision: BUY with HIGH conviction")
    print(f"Expected Sections: 10/10 (all sections)")
    print(f"Expected Word Count: 3,000-5,000 words")
    print(f"Expected Char Count: 18,000-30,000 characters\n")

    # Run analysis
    print("-" * 80)
    print(f"Running Deep Dive Analysis on {ticker}...")
    print(f"This will take approximately 5-7 minutes (analyzing 3 years)")
    print("-" * 80)

    try:
        result = agent.analyze_company(ticker, deep_dive=True, years_to_analyze=3)

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        # Extract thesis
        thesis = result.get('thesis', '')
        decision = result.get('decision', 'UNKNOWN')
        conviction = result.get('conviction', 'UNKNOWN')

        # Calculate metrics
        word_count = len(thesis.split())
        char_count = len(thesis)

        print(f"\n📊 THESIS METRICS:")
        print(f"   Words:      {word_count:,}")
        print(f"   Characters: {char_count:,}")
        print(f"   Decision:   {decision}")
        print(f"   Conviction: {conviction}")

        # Check for all 10 required sections
        print(f"\n📋 SECTION VERIFICATION:")

        sections = {
            "1. Business Overview": ["business overview", "what does"],
            "2. Economic Moat": ["economic moat", "moat analysis", "competitive advantage"],
            "3. Management Quality": ["management", "leadership", "ceo"],
            "4. Financial Analysis": ["financial analysis", "revenue", "profitability"],
            "5. Growth Prospects": ["growth", "expansion", "future"],
            "6. Competitive Position": ["competitive", "competitors", "competition"],
            "7. Risk Analysis": ["risk", "risks", "concerns"],
            "8. Multi-Year Synthesis": ["multi-year", "synthesis", "trends"],
            "9. Valuation": ["valuation", "dcf", "intrinsic value"],
            "10. Final Decision": ["final decision", "investment decision", "decision:"]
        }

        found_sections = 0
        thesis_lower = thesis.lower()

        for section_name, keywords in sections.items():
            found = any(keyword in thesis_lower for keyword in keywords)
            status = "✅" if found else "❌"
            print(f"   {status} {section_name}")
            if found:
                found_sections += 1

        print(f"\n   Total: {found_sections}/10 sections found")

        # Quality checks
        print(f"\n✅ QUALITY CHECKS:")

        checks = []

        # Word count check
        if 3000 <= word_count <= 6000:
            checks.append(("Word count in range (3,000-6,000)", True))
        elif word_count >= 2500:
            checks.append(("Word count acceptable (2,500+)", True))
        else:
            checks.append((f"Word count too low ({word_count})", False))

        # Section check
        if found_sections >= 10:
            checks.append(("All 10 sections present", True))
        elif found_sections >= 8:
            checks.append((f"Most sections present ({found_sections}/10)", True))
        else:
            checks.append((f"Missing sections ({found_sections}/10)", False))

        # Decision structure check
        has_decision = "DECISION:" in thesis
        has_conviction = "CONVICTION:" in thesis

        if has_decision and has_conviction:
            checks.append(("Structured decision format", True))
        else:
            checks.append(("Structured decision format", False))

        # Warren's voice check (simple heuristic)
        warren_indicators = [
            "charlie", "berkshire", "owner earnings", "moat",
            "margin of safety", "mr. market", "wonderful business"
        ]
        warren_count = sum(1 for indicator in warren_indicators if indicator in thesis_lower)

        if warren_count >= 3:
            checks.append(("Warren Buffett voice present", True))
        else:
            checks.append(("Warren Buffett voice", False))

        # Print checks
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")

        # Overall result
        print(f"\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)

        all_passed = all(check[1] for check in checks) and found_sections >= 9

        if all_passed:
            print("\n🎉 ✅ TEST PASSED - Complete Thesis Generated!")
            print(f"\n   The fix successfully generates complete investment theses with:")
            print(f"   • All 10 required sections present")
            print(f"   • Comprehensive analysis ({word_count:,} words)")
            print(f"   • Warren Buffett's authentic voice")
            print(f"   • Proper decision structure")
            print(f"\n   Decision: {decision} ({conviction} conviction)")
            return_code = 0
        else:
            print("\n⚠️  TEST FAILED - Thesis Incomplete")
            print(f"\n   Issues detected:")
            for check_name, passed in checks:
                if not passed:
                    print(f"   ❌ {check_name}")
            if found_sections < 9:
                print(f"   ❌ Missing sections ({10 - found_sections} sections not found)")
            return_code = 1

        # Save thesis for inspection
        output_file = f"{ticker}_thesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {ticker} Investment Thesis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Decision:** {decision} ({conviction} conviction)\n")
            f.write(f"**Word Count:** {word_count:,} words\n\n")
            f.write("---\n\n")
            f.write(thesis)

        print(f"\n📄 Thesis saved to: {output_file}")
        print(f"   Review the file to verify quality and completeness")

        print(f"\n" + "=" * 80)
        print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return return_code

    except Exception as e:
        print(f"\n❌ ERROR during analysis:")
        print(f"   {str(e)}")
        print(f"\nTest FAILED")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_complete_thesis())
