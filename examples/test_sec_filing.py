"""
SEC Filing Tool - Usage Examples

5 real-world examples demonstrating SEC filing retrieval for investment analysis.

Prerequisites:
    - No API key required (SEC EDGAR is free)
    - Internet connection needed

Usage:
    python examples/test_sec_filing.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.sec_filing_tool import SECFilingTool


def print_separator(title):
    """Print formatted separator."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def example_1_apple_business_description():
    """
    Example 1: Apple Business Description (Circle of Competence)

    Warren Buffett: "Never invest in a business you cannot understand."

    Use SEC 10-K Business section to understand what the company does.
    """
    print_separator("EXAMPLE 1: Apple Business Description")

    tool = SECFilingTool()

    result = tool.execute(
        ticker="AAPL",
        filing_type="10-K",
        section="business"
    )

    if result["success"]:
        print(f"[SUCCESS]")
        print(f"Company: {result['data']['company_name']}")
        print(f"Filing Date: {result['data']['filing_date']}")
        print(f"Section: {result['data']['section']}")
        print(f"Content Length: {result['data']['content_length']:,} characters")
        print(f"\nFirst 500 characters:\n")
        print(result['data']['content'][:500])
        print("\n** Investment Insight:")
        print("   - Read business description to assess circle of competence")
        print("   - Can you explain this business in simple terms?")
        print("   - If yes -> Proceed with analysis")
        print("   - If no -> Pass (outside circle of competence)")
    else:
        print(f"[ERROR]: {result['error']}")


def example_2_microsoft_risk_factors():
    """
    Example 2: Microsoft Risk Factors (Risk Assessment)

    Warren Buffett: "Risk comes from not knowing what you're doing."

    Extract Risk Factors section to identify management-disclosed risks.
    """
    print_separator("EXAMPLE 2: Microsoft Risk Factors")

    tool = SECFilingTool()

    result = tool.execute(
        ticker="MSFT",
        filing_type="10-K",
        section="risk_factors"
    )

    if result["success"]:
        print(f"[SUCCESS]")
        print(f"Company: {result['data']['company_name']}")
        print(f"Filing Date: {result['data']['filing_date']}")
        print(f"Content Length: {result['data']['content_length']:,} characters")
        print(f"\nRisk Factors Preview:\n")
        print(result['data']['content'][:400])
        print("\n** Investment Insight:")
        print("   - Identify top disclosed risks")
        print("   - Assess if risks are manageable")
        print("   - Look for new risks vs previous filings")
        print("   - Red flag: Increasing risk disclosures")
    else:
        print(f"[ERROR]: {result['error']}")


def example_3_coca_cola_mda():
    """
    Example 3: Coca-Cola MD&A (Management Quality)

    Warren Buffett: "Look for honest management."

    Review Management's Discussion & Analysis to assess transparency.
    """
    print_separator("EXAMPLE 3: Coca-Cola MD&A")

    tool = SECFilingTool()

    result = tool.execute(
        ticker="KO",
        filing_type="10-K",
        section="mda"
    )

    if result["success"]:
        print(f"[SUCCESS]")
        print(f"Company: {result['data']['company_name']}")
        print(f"Filing Date: {result['data']['filing_date']}")
        print(f"Content Length: {result['data']['content_length']:,} characters")
        print(f"\nMD&A Preview:\n")
        print(result['data']['content'][:400])
        print("\n** Investment Insight:")
        print("   - Is management candid about challenges?")
        print("   - Do they take responsibility or blame externals?")
        print("   - Is language clear or full of jargon?")
        print("   - Good sign: Clear, honest communication")
    else:
        print(f"[ERROR]: {result['error']}")


def example_4_latest_10q():
    """
    Example 4: Latest 10-Q Quarterly Report

    Get most recent quarterly filing for up-to-date information.
    """
    print_separator("EXAMPLE 4: Tesla Latest 10-Q")

    tool = SECFilingTool()

    result = tool.execute(
        ticker="TSLA",
        filing_type="10-Q",
        quarter=3,  # Q3
        section="full"
    )

    if result["success"]:
        print(f"[SUCCESS]")
        print(f"Company: {result['data']['company_name']}")
        print(f"Filing Date: {result['data']['filing_date']}")
        print(f"Fiscal Year: {result['data']['fiscal_year']}")
        print(f"Fiscal Quarter: Q{result['data']['fiscal_quarter']}")
        print(f"Content Length: {result['data']['content_length']:,} characters")
        print(f"\n** Use Case:")
        print("   - Review quarterly performance")
        print("   - Check for material changes")
        print("   - Monitor business trends")
    else:
        print(f"[ERROR]: {result['error']}")


def example_5_error_handling():
    """
    Example 5: Error Handling

    Demonstrate graceful error handling for invalid inputs.
    """
    print_separator("EXAMPLE 5: Error Handling")

    tool = SECFilingTool()

    # Test 1: Invalid ticker
    print("Test 1: Invalid Ticker")
    result = tool.execute(ticker="INVALID123", filing_type="10-K")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    # Test 2: Invalid filing type
    print("Test 2: Invalid Filing Type")
    result = tool.execute(ticker="AAPL", filing_type="INVALID")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    # Test 3: 10-Q without quarter
    print("Test 3: 10-Q Without Quarter")
    result = tool.execute(ticker="AAPL", filing_type="10-Q")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    print("** Error Handling Features:")
    print("   - Clear, actionable error messages")
    print("   - No exceptions raised (graceful degradation)")
    print("   - Returns error dict with success=False")


def main():
    """Run all examples."""
    print("\n")
    print("=" * 80)
    print("  SEC FILING TOOL - USAGE EXAMPLES".center(80))
    print("  Warren Buffett-Style Investment Analysis".center(80))
    print("=" * 80)

    print("\nNote: These examples make real API calls to SEC EDGAR")
    print("   - No API key required (completely free)")
    print("   - Rate limited to 9 requests/second")
    print("   - Each example takes 3-7 seconds\n")

    try:
        # Run examples
        example_1_apple_business_description()
        print("\n" + "=" * 80)

        example_2_microsoft_risk_factors()
        print("\n" + "=" * 80)

        example_3_coca_cola_mda()
        print("\n" + "=" * 80)

        example_4_latest_10q()
        print("\n" + "=" * 80)

        example_5_error_handling()

        # Summary
        print_separator("EXAMPLES COMPLETE")
        print("[SUCCESS] All 5 examples executed\n")
        print("Key Takeaways:")
        print("1. SEC filings provide authoritative company disclosures")
        print("2. Section extraction reduces token usage (93% savings)")
        print("3. Business section -> Circle of competence assessment")
        print("4. Risk Factors -> Risk identification")
        print("5. MD&A -> Management quality assessment")
        print("6. Error handling is graceful and informative")
        print("\nNext Steps:")
        print("- Integrate with GuruFocus for quantitative + qualitative analysis")
        print("- Use Web Search to cross-reference findings")
        print("- Build complete investment thesis with all tools")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted. Exiting.")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == "__main__":
    main()
