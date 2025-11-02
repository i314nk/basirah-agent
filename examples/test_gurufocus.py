"""
GuruFocus Tool - Usage Examples

Module: examples.test_gurufocus
Purpose: Demonstrate GuruFocus Tool usage with real-world companies
Status: Complete - Sprint 3, Phase 2
Created: 2025-10-30

This file demonstrates:
- All 4 endpoints (summary, financials, keyratios, valuation)
- Real-world company examples (Apple, Microsoft, Coca-Cola, Johnson & Johnson)
- Integration with Calculator Tool (hybrid approach)
- Special value detection
- Error handling

Prerequisites:
- GuruFocus Premium API key in .env file
- Environment variable: GURUFOCUS_API_KEY=your_key_here
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.gurufocus_tool import GuruFocusTool
from src.tools.calculator_tool import CalculatorTool


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def example_1_summary_endpoint():
    """Example 1: Get company summary (quick screening)"""
    print_section("EXAMPLE 1: Summary Endpoint - Quick Screening")

    tool = GuruFocusTool()

    # Apple Inc - High-quality technology company
    print("\n📊 Fetching Apple Inc. (AAPL) summary...")
    result = tool.execute(ticker="AAPL", endpoint="summary")

    if result["success"]:
        data = result["data"]
        print(f"✅ Company: {data['company_name']}")

        # General info
        if "general" in data:
            gen = data["general"]
            print(f"   Industry: {gen.get('industry')}")
            print(f"   Sector: {gen.get('sector')}")

        # Key metrics (pre-calculated by GuruFocus)
        metrics = data["metrics"]
        print(f"\n📈 Profitability Metrics:")
        if metrics.get("roic"):
            print(f"   ROIC: {metrics['roic']*100:.1f}%")
        if metrics.get("roe"):
            print(f"   ROE: {metrics['roe']*100:.1f}%")
        if metrics.get("operating_margin"):
            print(f"   Operating Margin: {metrics['operating_margin']*100:.1f}%")
        if metrics.get("net_margin"):
            print(f"   Net Margin: {metrics['net_margin']*100:.1f}%")

        # Financial strength
        if metrics.get("financial_strength_score"):
            print(f"\n💪 Financial Strength Score: {metrics['financial_strength_score']}/10")
        if metrics.get("debt_to_equity"):
            print(f"   Debt/Equity: {metrics['debt_to_equity']:.2f}")

        # Valuation
        valuation = data["valuation"]
        if valuation.get("price"):
            print(f"\n💰 Current Price: ${valuation['price']:.2f}")
        if valuation.get("pe_ratio"):
            print(f"   P/E Ratio: {valuation['pe_ratio']:.1f}")
        if valuation.get("market_cap"):
            print(f"   Market Cap: ${valuation['market_cap']/1e9:.1f}B")

        # Buffett Assessment
        roic = metrics.get("roic", 0)
        print(f"\n🎯 Buffett Assessment:")
        if roic >= 0.25:
            print(f"   WORLD-CLASS: ROIC of {roic*100:.1f}% far exceeds 15% threshold")
        elif roic >= 0.15:
            print(f"   EXCELLENT: ROIC of {roic*100:.1f}% meets Buffett's 15% threshold")
        else:
            print(f"   CONCERNING: ROIC of {roic*100:.1f}% below 15% threshold")

    else:
        print(f"❌ Error: {result['error']}")


def example_2_financials_endpoint():
    """Example 2: Get financial statements (10-year historical data)"""
    print_section("EXAMPLE 2: Financials Endpoint - Historical Data")

    tool = GuruFocusTool()

    # Coca-Cola - Stable dividend payer with long history
    print("\n📊 Fetching Coca-Cola (KO) financial statements...")
    result = tool.execute(ticker="KO", endpoint="financials", period="annual")

    if result["success"]:
        data = result["data"]
        print(f"✅ Company: {data['company_name']}")

        financials = data["financials"]

        # Most recent year data
        print(f"\n📋 Most Recent Annual Data:")
        if financials.get("revenue"):
            print(f"   Revenue: ${financials['revenue']/1e9:.1f}B")
        if financials.get("net_income"):
            print(f"   Net Income: ${financials['net_income']/1e9:.1f}B")
        if financials.get("operating_income"):
            print(f"   Operating Income: ${financials['operating_income']/1e9:.1f}B")
        if financials.get("free_cash_flow"):
            print(f"   Free Cash Flow: ${financials['free_cash_flow']/1e9:.1f}B")

        # Owner Earnings components
        print(f"\n💵 Owner Earnings Components:")
        if financials.get("depreciation_amortization"):
            print(f"   D&A: ${financials['depreciation_amortization']/1e9:.1f}B")
        if financials.get("capex"):
            print(f"   CapEx: ${financials['capex']/1e9:.1f}B")

        # Balance sheet
        print(f"\n📊 Balance Sheet:")
        if financials.get("total_assets"):
            print(f"   Total Assets: ${financials['total_assets']/1e9:.1f}B")
        if financials.get("total_debt"):
            print(f"   Total Debt: ${financials['total_debt']/1e9:.1f}B")
        if financials.get("cash_equivalents"):
            print(f"   Cash: ${financials['cash_equivalents']/1e9:.1f}B")

        # Historical trends
        if "historical" in financials:
            hist = financials["historical"]
            if hist.get("revenue"):
                print(f"\n📈 10-Year Revenue Trend:")
                revenues = [r for r in hist["revenue"] if r is not None]
                if len(revenues) >= 2:
                    print(f"   Most Recent: ${revenues[0]/1e9:.1f}B")
                    print(f"   10 Years Ago: ${revenues[-1]/1e9:.1f}B")
                    growth_rate = ((revenues[0] / revenues[-1]) ** (1/len(revenues)) - 1) * 100
                    print(f"   CAGR: {growth_rate:.1f}%")

    else:
        print(f"❌ Error: {result['error']}")


def example_3_keyratios_endpoint():
    """Example 3: Get key ratios (MOST IMPORTANT - pre-calculated metrics)"""
    print_section("EXAMPLE 3: Key Ratios Endpoint - Pre-Calculated Metrics (PRIMARY)")

    tool = GuruFocusTool()

    # Microsoft - High ROIC technology company
    print("\n📊 Fetching Microsoft (MSFT) key ratios...")
    result = tool.execute(ticker="MSFT", endpoint="keyratios")

    if result["success"]:
        data = result["data"]
        print(f"✅ Company: {data['company_name']}")

        metrics = data["metrics"]

        # Pre-calculated profitability metrics (agent uses these by default)
        print(f"\n🎯 Pre-Calculated Metrics (GuruFocus):")
        if metrics.get("roic"):
            print(f"   ROIC: {metrics['roic']*100:.1f}%")
        if metrics.get("roic_10y_avg"):
            print(f"   ROIC (10-year avg): {metrics['roic_10y_avg']*100:.1f}%")
        if metrics.get("roe"):
            print(f"   ROE: {metrics['roe']*100:.1f}%")
        if metrics.get("roa"):
            print(f"   ROA: {metrics['roa']*100:.1f}%")
        if metrics.get("operating_margin"):
            print(f"   Operating Margin: {metrics['operating_margin']*100:.1f}%")
        if metrics.get("net_margin"):
            print(f"   Net Margin: {metrics['net_margin']*100:.1f}%")

        # Per-share values
        print(f"\n📊 Per-Share Values:")
        if metrics.get("eps"):
            print(f"   EPS: ${metrics['eps']:.2f}")
        if metrics.get("fcf_per_share"):
            print(f"   FCF per Share: ${metrics['fcf_per_share']:.2f}")
        if metrics.get("fcf_per_share_10y_avg"):
            print(f"   FCF per Share (10-year avg): ${metrics['fcf_per_share_10y_avg']:.2f}")
        if metrics.get("revenue_per_share"):
            print(f"   Revenue per Share: ${metrics['revenue_per_share']:.2f}")
        if metrics.get("dividends_per_share"):
            print(f"   Dividends per Share: ${metrics['dividends_per_share']:.2f}")

        # Valuation ratios
        valuation = data.get("valuation", {})
        if valuation:
            print(f"\n💰 Valuation Ratios:")
            if valuation.get("pe_ratio"):
                print(f"   P/E Ratio: {valuation['pe_ratio']:.1f}")
            if valuation.get("pb_ratio"):
                print(f"   P/B Ratio: {valuation['pb_ratio']:.1f}")
            if valuation.get("price_to_fcf"):
                print(f"   Price/FCF: {valuation['price_to_fcf']:.1f}")

        # Quality assessment
        roic = metrics.get("roic", 0)
        roic_10y = metrics.get("roic_10y_avg", 0)
        print(f"\n🏆 Quality Assessment:")
        if roic >= 0.25 and roic_10y >= 0.20:
            print(f"   WORLD-CLASS: Consistently high ROIC (current {roic*100:.1f}%, 10-year {roic_10y*100:.1f}%)")
        elif roic >= 0.15:
            print(f"   EXCELLENT: Strong returns on invested capital")
        else:
            print(f"   ACCEPTABLE: Meets minimum thresholds")

    else:
        print(f"❌ Error: {result['error']}")


def example_4_valuation_endpoint():
    """Example 4: Get valuation metrics"""
    print_section("EXAMPLE 4: Valuation Endpoint - Growth & Valuation")

    tool = GuruFocusTool()

    # Johnson & Johnson - Healthcare dividend aristocrat
    print("\n📊 Fetching Johnson & Johnson (JNJ) valuation...")
    result = tool.execute(ticker="JNJ", endpoint="valuation")

    if result["success"]:
        data = result["data"]
        print(f"✅ Company: {data['company_name']}")

        valuation = data["valuation"]

        # Standard valuation multiples
        print(f"\n💰 Valuation Multiples:")
        if valuation.get("market_cap"):
            print(f"   Market Cap: ${valuation['market_cap']/1e9:.1f}B")
        if valuation.get("enterprise_value"):
            print(f"   Enterprise Value: ${valuation['enterprise_value']/1e9:.1f}B")
        if valuation.get("pe_ratio"):
            print(f"   P/E Ratio: {valuation['pe_ratio']:.1f}")
        if valuation.get("forward_pe"):
            print(f"   Forward P/E: {valuation['forward_pe']:.1f}")
        if valuation.get("pb_ratio"):
            print(f"   P/B Ratio: {valuation['pb_ratio']:.1f}")
        if valuation.get("ev_ebitda"):
            print(f"   EV/EBITDA: {valuation['ev_ebitda']:.1f}")

        # GuruFocus proprietary metrics
        print(f"\n🎯 GuruFocus Valuation:")
        if valuation.get("gf_value"):
            print(f"   GF Value: ${valuation['gf_value']:.2f}")
        if valuation.get("current_price"):
            print(f"   Current Price: ${valuation['current_price']:.2f}")
        if valuation.get("gf_value_rank"):
            print(f"   GF Value Rank: {valuation['gf_value_rank']}")
        if valuation.get("graham_number"):
            print(f"   Graham Number: ${valuation['graham_number']:.2f}")
        if valuation.get("dcf_value"):
            print(f"   DCF Value (GuruFocus): ${valuation['dcf_value']:.2f}")

        # Growth metrics
        metrics = data.get("metrics", {})
        if metrics:
            print(f"\n📈 Growth Metrics:")
            if metrics.get("revenue_growth_3y"):
                print(f"   Revenue Growth (3Y): {metrics['revenue_growth_3y']*100:.1f}%")
            if metrics.get("revenue_growth_5y"):
                print(f"   Revenue Growth (5Y): {metrics['revenue_growth_5y']*100:.1f}%")
            if metrics.get("eps_growth_3y"):
                print(f"   EPS Growth (3Y): {metrics['eps_growth_3y']*100:.1f}%")
            if metrics.get("fcf_growth_3y"):
                print(f"   FCF Growth (3Y): {metrics['fcf_growth_3y']*100:.1f}%")

    else:
        print(f"❌ Error: {result['error']}")


def example_5_integration_with_calculator():
    """Example 5: Integration with Calculator Tool (Hybrid Approach)"""
    print_section("EXAMPLE 5: Integration with Calculator Tool - Hybrid Approach")

    gf_tool = GuruFocusTool()
    calc_tool = CalculatorTool()

    # Apple - Demonstrate full workflow
    ticker = "AAPL"
    print(f"\n📊 Analyzing {ticker} using Hybrid Approach...")

    # Step 1: Get GuruFocus pre-calculated metrics
    print(f"\n1️⃣ Fetching GuruFocus pre-calculated metrics...")
    gf_result = gf_tool.execute(ticker=ticker, endpoint="keyratios")

    if not gf_result["success"]:
        print(f"❌ Error: {gf_result['error']}")
        return

    data = gf_result["data"]
    print(f"✅ Company: {data['company_name']}")

    # Extract key metrics
    metrics = data["metrics"]
    fcf_per_share = metrics.get("fcf_per_share")
    roic = metrics.get("roic")

    print(f"\n📈 GuruFocus Metrics (used by agent by default):")
    print(f"   ROIC: {roic*100:.1f}%")
    print(f"   FCF per Share: ${fcf_per_share:.2f}")

    # Step 2: Use Calculator Tool for DCF (basīrah's conservative model)
    print(f"\n2️⃣ Calculating intrinsic value using Calculator DCF...")

    # Assume shares outstanding (in real implementation, get from API)
    shares_outstanding = 15_700_000_000  # Example for Apple

    # Calculate Owner Earnings from FCF
    owner_earnings = fcf_per_share * shares_outstanding

    dcf_result = calc_tool.execute(
        calculation="dcf",
        data={
            "owner_earnings": owner_earnings,
            "growth_rate": 0.07,  # Conservative 7% growth
            "discount_rate": 0.10,  # Buffett's 10% hurdle rate
            "terminal_growth": 0.03,  # GDP growth
            "years": 10
        }
    )

    if dcf_result["success"]:
        intrinsic_value_total = dcf_result["data"]["result"]
        intrinsic_value_per_share = intrinsic_value_total / shares_outstanding

        print(f"✅ Intrinsic Value: ${intrinsic_value_per_share:.2f} per share")
        print(f"   (Total: ${intrinsic_value_total/1e9:.1f}B)")
    else:
        print(f"❌ DCF Error: {dcf_result['error']}")
        return

    # Step 3: Get current price from GuruFocus
    print(f"\n3️⃣ Fetching current price...")
    summary_result = gf_tool.execute(ticker=ticker, endpoint="summary")

    if summary_result["success"]:
        current_price = summary_result["data"]["valuation"].get("price")
        print(f"✅ Current Price: ${current_price:.2f}")
    else:
        print(f"❌ Price fetch error")
        return

    # Step 4: Calculate Margin of Safety using Calculator
    print(f"\n4️⃣ Calculating Margin of Safety...")
    mos_result = calc_tool.execute(
        calculation="margin_of_safety",
        data={
            "intrinsic_value": intrinsic_value_per_share,
            "current_price": current_price
        }
    )

    if mos_result["success"]:
        margin = mos_result["data"]["result"]
        print(f"✅ Margin of Safety: {margin*100:.1f}%")

        # Interpretation per Buffett criteria
        if margin >= 0.40:
            print(f"   📊 EXCELLENT margin - STRONG BUY signal")
        elif margin >= 0.25:
            print(f"   📊 GOOD margin - BUY signal")
        elif margin >= 0.15:
            print(f"   📊 ACCEPTABLE margin - Conditional BUY")
        elif margin > 0:
            print(f"   📊 INSUFFICIENT margin - WATCH")
        else:
            print(f"   📊 NEGATIVE margin - OVERVALUED (AVOID)")
    else:
        print(f"❌ MoS Error: {mos_result['error']}")

    # Step 5: Final recommendation
    print(f"\n5️⃣ Investment Decision:")
    print(f"   ROIC: {roic*100:.1f}% {'✅ Excellent' if roic >= 0.15 else '❌ Below threshold'}")
    if mos_result["success"]:
        margin = mos_result["data"]["result"]
        print(f"   Margin of Safety: {margin*100:.1f}% {'✅ Adequate' if margin >= 0.25 else '❌ Insufficient'}")

        if roic >= 0.15 and margin >= 0.25:
            print(f"\n🎯 RECOMMENDATION: BUY - Meets Buffett criteria")
        elif roic >= 0.15 and margin >= 0.15:
            print(f"\n🎯 RECOMMENDATION: CONDITIONAL BUY - Good quality, marginal price")
        elif roic >= 0.15:
            print(f"\n🎯 RECOMMENDATION: WATCH - Good quality, wait for better price")
        else:
            print(f"\n🎯 RECOMMENDATION: AVOID - Fails quality criteria")


def example_6_special_values():
    """Example 6: Demonstrating special value detection"""
    print_section("EXAMPLE 6: Special Value Detection")

    tool = GuruFocusTool()

    print("\n📊 Fetching data that may contain special values...")
    print("(Special values: 9999 = Data N/A, 10000 = No debt/Negative equity)")

    # Try a company (any ticker)
    result = tool.execute(ticker="AAPL", endpoint="keyratios")

    if result["success"]:
        special_values = result["data"]["special_values_detected"]

        if special_values:
            print(f"\n⚠️  Found {len(special_values)} special value(s):")
            for sv in special_values:
                print(f"   Field: {sv['field']}")
                print(f"   Value: {sv['value']}")
                print(f"   Meaning: {sv['meaning']}")
                print()
        else:
            print(f"\n✅ No special values detected - all data available")

    else:
        print(f"❌ Error: {result['error']}")


def example_7_error_handling():
    """Example 7: Demonstrating error handling"""
    print_section("EXAMPLE 7: Error Handling")

    tool = GuruFocusTool()

    # Test invalid ticker
    print("\n🔍 Testing invalid ticker...")
    result = tool.execute(ticker="INVALID123", endpoint="summary")

    if not result["success"]:
        print(f"✅ Correctly handled error: {result['error']}")

    # Test invalid endpoint
    print("\n🔍 Testing invalid endpoint...")
    result = tool.execute(ticker="AAPL", endpoint="invalid_endpoint")

    if not result["success"]:
        print(f"✅ Correctly handled error: {result['error']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print(" GuruFocus Tool - Usage Examples")
    print(" basīrah Investment Agent")
    print("=" * 80)

    # Check API key
    if not os.getenv("GURUFOCUS_API_KEY"):
        print("\n❌ ERROR: GURUFOCUS_API_KEY not set in environment")
        print("\nTo run these examples:")
        print("1. Get a GuruFocus Premium API key from: https://www.gurufocus.com/api.php")
        print("2. Copy .env.example to .env")
        print("3. Add your key: GURUFOCUS_API_KEY=your_key_here")
        print("4. Run this script again")
        return

    print("\n✅ GuruFocus API key found")
    print("\nRunning examples with real-world companies...")

    try:
        # Run examples
        example_1_summary_endpoint()
        example_2_financials_endpoint()
        example_3_keyratios_endpoint()
        example_4_valuation_endpoint()
        example_5_integration_with_calculator()
        example_6_special_values()
        example_7_error_handling()

        print_section("All Examples Complete!")
        print("\n✅ All examples executed successfully")
        print("\nNext steps:")
        print("  1. Review the output to understand each endpoint")
        print("  2. Try different tickers (MSFT, KO, JNJ, etc.)")
        print("  3. Explore integration with Calculator Tool for full analysis")

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
