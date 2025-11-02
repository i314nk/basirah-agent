"""
Web Search Tool - Real-World Usage Examples

This module demonstrates the Web Search Tool with real-world investment research
queries following Warren Buffett's philosophy. Each example shows how to use
web search for qualitative analysis to complement quantitative metrics from
GuruFocus.

Examples included:
1. Apple - Management Quality Research
2. Coca-Cola - Economic Moat Assessment (Brand Strength)
3. Microsoft - Competitive Landscape Analysis
4. Tesla - Recent News Monitoring
5. Meta - Risk Assessment (Litigation & Regulatory)
6. Johnson & Johnson - Product Innovation Research
7. Berkshire Hathaway - Insurance Competitive Advantage
8. Integration with GuruFocus Tool
9. Error Handling Demonstration
10. Advanced: Multi-Query Moat Assessment

Prerequisites:
- BRAVE_SEARCH_API_KEY environment variable set in .env file
- Get free API key from: https://brave.com/search/api/

Usage:
    python examples/test_web_search.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.web_search_tool import WebSearchTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_separator(title: str):
    """Print a formatted separator for output clarity."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result_summary(result: Dict[str, Any], max_results: int = 3):
    """Print a summary of search results."""
    if not result["success"]:
        print(f"❌ Search failed: {result['error']}")
        return

    data = result["data"]
    print(f"✅ Search successful")
    print(f"Query: {data['query']}")
    print(f"Total Results: {data['total_results']}")
    print(f"Search Type: {data['search_type']}")
    if data.get("freshness"):
        print(f"Freshness: {data['freshness']}")

    print(f"\n📄 Top {min(max_results, len(data['results']))} Results:\n")

    for i, result_item in enumerate(data["results"][:max_results], 1):
        print(f"{i}. {result_item['title']}")
        print(f"   URL: {result_item['url']}")
        print(f"   Domain: {result_item['domain']}")

        if result_item.get("published_date"):
            print(f"   Published: {result_item['published_date']}")

        print(f"   Description: {result_item['description'][:150]}...")

        # Show RAG-optimized snippets (CRITICAL for AI agent)
        if result_item.get("extra_snippets"):
            print(f"   📝 Extra Snippets ({len(result_item['extra_snippets'])} total):")
            for j, snippet in enumerate(result_item["extra_snippets"][:2], 1):
                print(f"      {j}. {snippet[:120]}...")

        print()


# =============================================================================
# EXAMPLE 1: Apple - Management Quality Research
# =============================================================================

def example_1_apple_management_research():
    """
    Example 1: Research Apple's Management Quality

    Warren Buffett emphasizes: "I try to buy stock in businesses that are so
    wonderful that an idiot can run them. Because sooner or later, one will."

    Despite this, management quality matters. This search investigates:
    - CEO leadership track record
    - Capital allocation decisions
    - Corporate governance
    - Management continuity

    Use Case: Phase 3 of investigation workflow (Management Assessment)
    """
    print_separator("EXAMPLE 1: Apple - Management Quality Research")

    tool = WebSearchTool()

    # Research Tim Cook's leadership and track record
    result = tool.execute(
        query="Tim Cook CEO leadership track record performance",
        company="Apple Inc",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=3)

    print("\n💡 Investment Insight:")
    print("   - Look for consistent capital allocation discipline")
    print("   - Assess management's focus on shareholder returns vs empire building")
    print("   - Verify alignment with shareholder interests (insider ownership)")
    print("   - Check for scandals, ethical issues, or governance red flags")


# =============================================================================
# EXAMPLE 2: Coca-Cola - Economic Moat Assessment (Brand Strength)
# =============================================================================

def example_2_coca_cola_moat_assessment():
    """
    Example 2: Assess Coca-Cola's Economic Moat - Brand Strength

    Warren Buffett: "The most important thing is the moat around the business."

    Coca-Cola's primary moat is brand power. This search investigates:
    - Brand recognition and customer loyalty
    - Pricing power (ability to raise prices without losing customers)
    - Market share stability
    - Distribution network advantages

    Use Case: Phase 2 of investigation workflow (Economic Moat Validation)
    """
    print_separator("EXAMPLE 2: Coca-Cola - Economic Moat Assessment")

    tool = WebSearchTool()

    # Research Coca-Cola's brand strength and customer loyalty
    result = tool.execute(
        query="brand strength customer loyalty pricing power",
        company="Coca-Cola",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=3)

    print("\n💡 Investment Insight:")
    print("   - Strong brands can maintain pricing power through economic cycles")
    print("   - Customer loyalty = predictable revenue streams")
    print("   - Brand moats are durable but can erode (watch for changing preferences)")
    print("   - Look for evidence of pricing discipline vs desperate discounting")


# =============================================================================
# EXAMPLE 3: Microsoft - Competitive Landscape Analysis
# =============================================================================

def example_3_microsoft_competitive_landscape():
    """
    Example 3: Analyze Microsoft's Competitive Position

    Warren Buffett: "In business, I look for economic castles protected by
    unbreachable moats."

    This search investigates:
    - Competitive advantages (switching costs, network effects)
    - Market share trends
    - Threats from competitors
    - Moat durability

    Use Case: Phase 4 of investigation workflow (Competitive Threats)
    """
    print_separator("EXAMPLE 3: Microsoft - Competitive Landscape")

    tool = WebSearchTool()

    # Research Microsoft's competitive advantages and market position
    result = tool.execute(
        query="competitive advantages market share cloud computing",
        company="Microsoft",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=3)

    print("\n💡 Investment Insight:")
    print("   - Assess moat type: switching costs (Office), network effects (Teams)")
    print("   - Validate moat durability against new entrants and tech changes")
    print("   - Look for expanding moats (Azure cloud growth)")
    print("   - Check for complacency that could weaken competitive position")


# =============================================================================
# EXAMPLE 4: Tesla - Recent News Monitoring
# =============================================================================

def example_4_tesla_recent_news():
    """
    Example 4: Monitor Recent Tesla News

    This search demonstrates:
    - News search type for current events
    - Freshness filter for recency (past week)
    - Real-time monitoring of company developments

    Use Case: Phase 5 of investigation workflow (Risk Assessment)
    Also useful for ongoing monitoring after investment
    """
    print_separator("EXAMPLE 4: Tesla - Recent News (Past Week)")

    tool = WebSearchTool()

    # Get recent news about Tesla (past week)
    result = tool.execute(
        query="latest news developments",
        company="Tesla",
        count=10,
        search_type="news",
        freshness="week"
    )

    print_result_summary(result, max_results=5)

    print("\n💡 Investment Insight:")
    print("   - Monitor for material changes: product recalls, regulatory issues")
    print("   - Track management commentary and guidance changes")
    print("   - Identify emerging risks before they impact financials")
    print("   - Distinguish noise from signal (celebrity CEO tweets vs real news)")


# =============================================================================
# EXAMPLE 5: Meta - Risk Assessment (Litigation & Regulatory)
# =============================================================================

def example_5_meta_risk_assessment():
    """
    Example 5: Assess Regulatory and Legal Risks for Meta

    Warren Buffett: "Risk comes from not knowing what you're doing."

    This search investigates:
    - Regulatory threats (antitrust, privacy laws)
    - Litigation exposure
    - Reputational risks
    - Political/social pressures

    Use Case: Phase 5 of investigation workflow (Risk Assessment)
    Critical for companies with regulatory uncertainty
    """
    print_separator("EXAMPLE 5: Meta - Risk Assessment (Regulatory & Legal)")

    tool = WebSearchTool()

    # Research Meta's regulatory and litigation risks
    result = tool.execute(
        query="antitrust lawsuit regulatory investigation privacy",
        company="Meta Platforms",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=3)

    print("\n💡 Investment Insight:")
    print("   - Regulatory risk can impair business models (ad targeting restrictions)")
    print("   - Quantify potential fines relative to earnings power")
    print("   - Assess moat vulnerability to regulatory changes")
    print("   - Consider circle of competence: Can you predict regulatory outcomes?")


# =============================================================================
# EXAMPLE 6: Johnson & Johnson - Product Innovation Research
# =============================================================================

def example_6_jnj_product_innovation():
    """
    Example 6: Research Product Pipeline and Innovation

    For healthcare/pharma companies, innovation drives future growth.

    This search investigates:
    - R&D productivity
    - New product pipeline
    - Patent expiration risks
    - Competitive innovation threats

    Use Case: Industry-specific moat assessment for healthcare
    """
    print_separator("EXAMPLE 6: J&J - Product Innovation & Pipeline")

    tool = WebSearchTool()

    # Research J&J's product pipeline and innovation
    result = tool.execute(
        query="drug pipeline new products FDA approval R&D",
        company="Johnson & Johnson",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=3)

    print("\n💡 Investment Insight:")
    print("   - Strong pipelines indicate durable competitive advantage")
    print("   - Patent expirations = future margin compression risk")
    print("   - R&D productivity: Are they getting ROI on research spending?")
    print("   - Diversification reduces single-product dependency risk")


# =============================================================================
# EXAMPLE 7: Berkshire Hathaway - Insurance Competitive Advantage
# =============================================================================

def example_7_berkshire_insurance_advantage():
    """
    Example 7: Research Industry-Specific Moats (Insurance Float)

    Warren Buffett built Berkshire using insurance float as leverage.

    This search investigates:
    - Underwriting discipline
    - Float generation and cost
    - Insurance industry competitive dynamics
    - Claims paying ability ratings

    Use Case: Understanding complex business models and moat sources
    """
    print_separator("EXAMPLE 7: Berkshire Hathaway - Insurance Float Advantage")

    tool = WebSearchTool()

    # Research Berkshire's insurance operations and float advantage
    result = tool.execute(
        query="insurance float underwriting discipline competitive advantage",
        company="Berkshire Hathaway",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=3)

    print("\n💡 Investment Insight:")
    print("   - Insurance float = free leverage IF underwriting is disciplined")
    print("   - Cost of float < risk-free rate = exceptional advantage")
    print("   - Underwriting discipline separates great insurers from mediocre ones")
    print("   - Look for evidence of pricing discipline during soft markets")


# =============================================================================
# EXAMPLE 8: Integration with GuruFocus Tool
# =============================================================================

def example_8_integration_with_gurufocus():
    """
    Example 8: Integration with GuruFocus Tool

    Demonstrates how Web Search complements quantitative analysis:
    1. GuruFocus provides metrics (ROIC, financial strength)
    2. Web Search validates qualitative factors (moat, management)
    3. Combined analysis = complete investment picture

    Use Case: Full investigation workflow (Phases 1-7)
    """
    print_separator("EXAMPLE 8: Integration - GuruFocus + Web Search")

    # First, get quantitative metrics from GuruFocus
    # (This would use GuruFocusTool in real scenario)
    print("Step 1: GuruFocus Quantitative Analysis")
    print("   - ROIC: 31.2% (excellent)")
    print("   - Financial Strength: 8/10 (strong)")
    print("   - 10Y ROIC Average: 33.5% (consistent)")
    print("   ✅ Quantitative screen: PASSED\n")

    # Then, validate with qualitative research
    print("Step 2: Web Search Qualitative Validation\n")

    tool = WebSearchTool()

    # Research moat durability
    result = tool.execute(
        query="economic moat competitive advantage sustainability",
        company="Apple Inc",
        count=10,
        search_type="general"
    )

    print_result_summary(result, max_results=2)

    print("\n💡 Investment Insight:")
    print("   - High ROIC (31.2%) suggests strong moat")
    print("   - Web search validates moat source: ecosystem lock-in, brand premium")
    print("   - Consistency (10Y avg 33.5%) suggests durable moat")
    print("   - Qualitative + Quantitative = High-confidence investment thesis")


# =============================================================================
# EXAMPLE 9: Error Handling Demonstration
# =============================================================================

def example_9_error_handling():
    """
    Example 9: Error Handling

    Demonstrates graceful error handling for:
    - Invalid input (empty query)
    - Missing API key
    - API errors (invalid ticker)

    Use Case: Production robustness
    """
    print_separator("EXAMPLE 9: Error Handling Demonstration")

    tool = WebSearchTool()

    # Test 1: Empty query
    print("Test 1: Empty Query")
    result = tool.execute(query="", company="Apple")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    # Test 2: Query too long
    print("Test 2: Query Too Long (>400 chars)")
    long_query = "a" * 401
    result = tool.execute(query=long_query, company="Apple")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    # Test 3: Invalid search type
    print("Test 3: Invalid Search Type")
    result = tool.execute(query="test", search_type="invalid_type")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    # Test 4: Invalid freshness
    print("Test 4: Invalid Freshness Filter")
    result = tool.execute(query="test", freshness="invalid_freshness")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")

    print("\n💡 Error Handling Features:")
    print("   - Input validation prevents bad API calls")
    print("   - Graceful degradation: returns error dict, not exception")
    print("   - Informative error messages for debugging")
    print("   - Retry logic with exponential backoff for transient errors")


# =============================================================================
# EXAMPLE 10: Advanced - Multi-Query Moat Assessment
# =============================================================================

def example_10_advanced_multi_query_moat():
    """
    Example 10: Advanced - Comprehensive Moat Assessment

    Demonstrates sophisticated moat analysis using multiple targeted queries:
    1. Brand strength query
    2. Switching cost query
    3. Network effect query
    4. Cost advantage query

    This mirrors how an AI agent would comprehensively assess moat durability.

    Use Case: Phase 2 (Economic Moat) - comprehensive assessment
    """
    print_separator("EXAMPLE 10: Advanced - Multi-Query Moat Assessment")

    tool = WebSearchTool()
    company = "Microsoft"

    moat_queries = [
        ("brand strength reputation customer perception", "Brand Power"),
        ("switching costs vendor lock-in migration difficulty", "Switching Costs"),
        ("network effects platform ecosystem", "Network Effects"),
        ("cost advantage economies of scale operational efficiency", "Cost Advantage"),
    ]

    print(f"Comprehensive Moat Assessment for {company}\n")

    for query, moat_type in moat_queries:
        print(f"\n--- {moat_type} Analysis ---")
        result = tool.execute(
            query=query,
            company=company,
            count=5,
            search_type="general"
        )

        if result["success"]:
            print(f"✅ Found {result['data']['total_results']} results")

            # Show top result
            if result["data"]["results"]:
                top_result = result["data"]["results"][0]
                print(f"Top Result: {top_result['title']}")
                print(f"Snippet: {top_result['description'][:200]}...")
        else:
            print(f"❌ Search failed: {result['error']}")

    print("\n\n💡 Advanced Analysis Insight:")
    print("   - Multiple targeted queries = comprehensive moat picture")
    print("   - Microsoft shows evidence of ALL four moat types:")
    print("     1. Brand Power: Trusted enterprise brand")
    print("     2. Switching Costs: Office, Azure migration complexity")
    print("     3. Network Effects: Teams, LinkedIn, developer ecosystem")
    print("     4. Cost Advantage: Cloud infrastructure scale")
    print("   - Multi-layered moats = exceptional durability")
    print("   - This is how an AI agent builds high-confidence investment theses")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all examples sequentially."""

    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  WEB SEARCH TOOL - REAL-WORLD USAGE EXAMPLES".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Warren Buffett-Style Investment Research".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")

    # Check for API key
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key or api_key == "your_key_here":
        print("\n⚠️  WARNING: BRAVE_SEARCH_API_KEY not set in .env file")
        print("   Get a free API key from: https://brave.com/search/api/")
        print("   2,000 free searches/month - no credit card required\n")
        print("   Examples will demonstrate error handling instead.\n")

        # Run only error handling example
        example_9_error_handling()
        return

    print("\n✅ API Key configured. Running all examples...\n")

    try:
        # Run all examples
        example_1_apple_management_research()
        input("\nPress Enter to continue to Example 2...")

        example_2_coca_cola_moat_assessment()
        input("\nPress Enter to continue to Example 3...")

        example_3_microsoft_competitive_landscape()
        input("\nPress Enter to continue to Example 4...")

        example_4_tesla_recent_news()
        input("\nPress Enter to continue to Example 5...")

        example_5_meta_risk_assessment()
        input("\nPress Enter to continue to Example 6...")

        example_6_jnj_product_innovation()
        input("\nPress Enter to continue to Example 7...")

        example_7_berkshire_insurance_advantage()
        input("\nPress Enter to continue to Example 8...")

        example_8_integration_with_gurufocus()
        input("\nPress Enter to continue to Example 9...")

        example_9_error_handling()
        input("\nPress Enter to continue to Example 10...")

        example_10_advanced_multi_query_moat()

        # Summary
        print_separator("EXAMPLES COMPLETE")
        print("✅ All 10 examples executed successfully\n")
        print("Key Takeaways:")
        print("1. Web Search complements quantitative analysis (GuruFocus)")
        print("2. Qualitative research validates moats, management, and risks")
        print("3. Multiple search types (general, news, recent) serve different use cases")
        print("4. Freshness filters enable real-time monitoring")
        print("5. RAG-optimized snippets provide rich context for AI agents")
        print("6. Integration with GuruFocus creates complete investment picture")
        print("7. Error handling ensures production robustness")
        print("8. Multi-query strategies enable comprehensive analysis")
        print("\nNext Steps:")
        print("- Run test suite: python -m pytest tests/test_tools/test_web_search.py -v")
        print("- Review Phase 3 User Testing Package: PHASE_3_USER_TESTING.md")
        print("- Integrate into AI agent for autonomous investment research")

    except KeyboardInterrupt:
        print("\n\n⏸️  Examples interrupted by user. Exiting gracefully.")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    main()
