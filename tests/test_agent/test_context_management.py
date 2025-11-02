"""
Context Management Tests for Deep Dive Analysis

These tests verify that the progressive summarization strategy successfully
manages context window limits while maintaining multi-year analysis quality.

CRITICAL REQUIREMENT: Deep dive analysis must stay under 200K token limit.
"""

import pytest
from src.agent.buffett_agent import WarrenBuffettAgent
import os
from dotenv import load_dotenv


class TestContextManagement:
    """Test suite for context window management in deep dive analysis"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load environment variables for all tests"""
        load_dotenv()

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.expensive
    def test_deep_dive_stays_within_context_limit(self):
        """
        CRITICAL TEST: Verify deep dive doesn't exceed 200K context

        This test MUST pass before Phase 5 can be approved for production.

        Expected behavior:
        - Analysis completes successfully
        - Context stays under 200K tokens
        - Multi-year analysis (3+ years)
        - Valid BUY/WATCH/AVOID decision
        """
        agent = WarrenBuffettAgent()

        # Run deep dive on Apple
        result = agent.analyze_company("AAPL", deep_dive=True)

        # Verify success
        assert result["decision"] in ["BUY", "WATCH", "AVOID"], \
            f"Invalid decision: {result['decision']}"

        assert result["thesis"] is not None, "Thesis is missing"
        assert len(result["thesis"]) > 1000, "Thesis too short - likely incomplete"

        # Verify multi-year analysis occurred
        assert "context_management" in result.get("metadata", {}), \
            "Context management metadata missing"

        cm = result["metadata"]["context_management"]

        assert "years_analyzed" in cm, "Years analyzed not recorded"
        assert len(cm["years_analyzed"]) >= 3, \
            f"Expected 3+ years analyzed, got {len(cm['years_analyzed'])}"

        # Verify context stayed reasonable
        total_tokens = cm.get("total_token_estimate", 0)
        assert total_tokens > 0, "Token estimate not recorded"
        assert total_tokens < 200000, \
            f"Context too large: {total_tokens:,} tokens (exceeds 200K limit)"

        print(f"\n✓ Context Management Test PASSED")
        print(f"  - Decision: {result['decision']}")
        print(f"  - Conviction: {result['conviction']}")
        print(f"  - Years Analyzed: {cm['years_analyzed']}")
        print(f"  - Total Tokens: {total_tokens:,} (< 200K limit)")
        print(f"  - Reduction: {((212000 - total_tokens) / 212000 * 100):.1f}% from original 212K")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_multi_year_insights_present(self):
        """
        Verify agent actually uses multi-year data in thesis

        The thesis should demonstrate analysis across multiple years,
        not just current year snapshot.
        """
        agent = WarrenBuffettAgent()

        result = agent.analyze_company("AAPL", deep_dive=True)

        thesis = result["thesis"].lower()

        # Check for multi-year language
        multi_year_indicators = [
            "over the past",
            "historically",
            "trend",
            "consistently",
            "previous years",
            "compared to",
            "year over year",
            "across",
            "from 20",  # e.g., "from 2022 to 2024"
            "through 20"  # e.g., "through 2024"
        ]

        found_indicators = [ind for ind in multi_year_indicators if ind in thesis]

        assert len(found_indicators) >= 3, \
            f"Thesis doesn't demonstrate multi-year analysis. " \
            f"Only found {len(found_indicators)} indicators: {found_indicators}"

        # Verify years are mentioned
        years_mentioned = []
        for year in [2024, 2023, 2022, 2021]:
            if str(year) in thesis:
                years_mentioned.append(year)

        assert len(years_mentioned) >= 2, \
            f"Expected multiple years mentioned in thesis, found: {years_mentioned}"

        print(f"\n✓ Multi-Year Analysis Test PASSED")
        print(f"  - Multi-year indicators found: {len(found_indicators)}")
        print(f"  - Examples: {found_indicators[:3]}")
        print(f"  - Years mentioned: {years_mentioned}")

    @pytest.mark.integration
    @pytest.mark.expensive
    def test_prior_year_summaries_concise(self):
        """
        Verify prior year summaries are concise (target: 2-3K tokens each)

        This ensures the progressive summarization strategy actually
        reduces context vs reading full historical 10-Ks.
        """
        agent = WarrenBuffettAgent()

        # Run analysis
        result = agent.analyze_company("AAPL", deep_dive=True)

        # Check metadata
        cm = result["metadata"].get("context_management", {})

        current_year_tokens = cm.get("current_year_tokens", 0)
        prior_years_tokens = cm.get("prior_years_tokens", 0)
        num_prior_years = len(cm.get("years_analyzed", [])) - 1  # Subtract current year

        if num_prior_years > 0:
            avg_prior_year_tokens = prior_years_tokens / num_prior_years

            # Each prior year should be much smaller than current year
            assert avg_prior_year_tokens < current_year_tokens / 2, \
                f"Prior year summaries not concise enough: " \
                f"avg {avg_prior_year_tokens:.0f} tokens vs current {current_year_tokens:.0f}"

            # Each prior year should be in target range (500-5000 tokens)
            assert 500 < avg_prior_year_tokens < 5000, \
                f"Prior year summaries outside target range: {avg_prior_year_tokens:.0f} tokens"

        print(f"\n✓ Summary Conciseness Test PASSED")
        print(f"  - Current year: ~{current_year_tokens:,} tokens")
        print(f"  - Prior years total: ~{prior_years_tokens:,} tokens")
        if num_prior_years > 0:
            print(f"  - Average per prior year: ~{avg_prior_year_tokens:.0f} tokens")
            print(f"  - Compression ratio: {(current_year_tokens / avg_prior_year_tokens):.1f}x")

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.expensive
    def test_multiple_companies(self):
        """
        Verify context management works across different companies

        Tests that the strategy isn't overfitted to one company's
        filing structure.
        """
        agent = WarrenBuffettAgent()

        companies = ["AAPL", "KO"]  # Apple and Coca-Cola
        results = []

        for ticker in companies:
            print(f"\n  Testing {ticker}...")
            result = agent.analyze_company(ticker, deep_dive=True)

            # Verify success
            assert result["decision"] in ["BUY", "WATCH", "AVOID"]

            # Verify context management
            cm = result["metadata"].get("context_management", {})
            total_tokens = cm.get("total_token_estimate", 0)

            assert total_tokens < 200000, \
                f"{ticker}: Context exceeded limit: {total_tokens:,} tokens"

            results.append({
                'ticker': ticker,
                'tokens': total_tokens,
                'years': len(cm.get("years_analyzed", [])),
                'decision': result['decision']
            })

        print(f"\n✓ Multiple Companies Test PASSED")
        for r in results:
            print(f"  - {r['ticker']}: {r['tokens']:,} tokens, "
                  f"{r['years']} years, Decision: {r['decision']}")

    def test_quick_screen_still_works(self):
        """
        Verify quick screen mode wasn't broken by refactoring

        Quick screen should complete quickly with minimal context.
        """
        agent = WarrenBuffettAgent()

        result = agent.analyze_company("AAPL", deep_dive=False)

        # Verify success
        assert result["decision"] in ["BUY", "WATCH", "AVOID"]
        assert "thesis" in result
        assert result["metadata"]["tool_calls_made"] > 0

        # Quick screen should be fast
        assert result["metadata"]["analysis_duration_seconds"] < 120, \
            f"Quick screen too slow: {result['metadata']['analysis_duration_seconds']:.0f}s"

        print(f"\n✓ Quick Screen Test PASSED")
        print(f"  - Decision: {result['decision']}")
        print(f"  - Duration: {result['metadata']['analysis_duration_seconds']:.1f}s")
        print(f"  - Tool calls: {result['metadata']['tool_calls_made']}")


class TestContextManagementImplementation:
    """Test the implementation details of context management"""

    def test_extract_summary_with_markers(self):
        """Test summary extraction with proper markers"""
        from src.agent.buffett_agent import WarrenBuffettAgent

        agent = WarrenBuffettAgent()

        # Test text with markers
        test_text = """
Some preamble text.

=== 2023 ANNUAL REPORT SUMMARY ===

This is the summary content for 2023.
It has multiple lines.
And some key metrics.

=== END 2023 SUMMARY ===

Some trailing text.
"""

        summary = agent._extract_summary_from_response(test_text, year=2023)

        assert "This is the summary content for 2023" in summary
        assert "Some preamble text" not in summary
        assert "Some trailing text" not in summary

    def test_extract_summary_without_markers(self):
        """Test summary extraction falls back to full text"""
        from src.agent.buffett_agent import WarrenBuffettAgent

        agent = WarrenBuffettAgent()

        # Test text without markers
        test_text = "This is the full response with no markers."

        summary = agent._extract_summary_from_response(test_text, year=2023)

        # Should return full text as fallback
        assert summary == test_text

    def test_extract_metrics_from_summary(self):
        """Test financial metrics extraction from summary text"""
        from src.agent.buffett_agent import WarrenBuffettAgent

        agent = WarrenBuffettAgent()

        test_summary = """
        Revenue: $394.3B (+8.2% YoY)
        Operating Margin: 30.1%
        ROIC: 33.7%
        Debt/Equity: 1.55
        Free Cash Flow: $99.6B
        """

        metrics = agent._extract_metrics_from_summary(test_summary)

        assert 'revenue_billions' in metrics
        assert abs(metrics['revenue_billions'] - 394.3) < 0.1

        assert 'roic_percent' in metrics
        assert abs(metrics['roic_percent'] - 33.7) < 0.1

        assert 'margin_percent' in metrics
        assert abs(metrics['margin_percent'] - 30.1) < 0.1

        assert 'debt_equity' in metrics
        assert abs(metrics['debt_equity'] - 1.55) < 0.1


# Mark expensive tests to run selectively
pytestmark = pytest.mark.integration


if __name__ == "__main__":
    """
    Run context management tests manually
    """
    print("="*80)
    print("CONTEXT MANAGEMENT TESTS")
    print("="*80)
    print()
    print("These tests verify that deep dive analysis:")
    print("1. Stays under 200K token context limit")
    print("2. Analyzes 3+ years of annual reports")
    print("3. Produces multi-year insights in thesis")
    print("4. Works across different companies")
    print()
    print("WARNING: These tests make real API calls and cost $4-8 total")
    print()

    input("Press ENTER to run tests (or Ctrl+C to cancel)...")

    pytest.main([__file__, "-v", "-s", "-m", "integration"])
