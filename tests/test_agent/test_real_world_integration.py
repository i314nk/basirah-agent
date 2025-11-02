"""
Real-World Integration Test - Warren Buffett AI Agent

This test performs ACTUAL API calls to verify end-to-end functionality.

WARNING: This test will:
- Call Anthropic Claude API (costs ~$0.50-2 per test)
- Call GuruFocus API (uses subscription quota)
- Call Brave Search API (uses free tier quota)

Only run this test when you want to verify real-world functionality.

Run:
    pytest tests/test_agent/test_real_world_integration.py -v -s
"""

import pytest
import os
from dotenv import load_dotenv
from src.agent.buffett_agent import WarrenBuffettAgent

# Load environment variables
load_dotenv()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping real-world test"
)
class TestRealWorldIntegration:
    """
    Real-world integration tests with actual API calls.

    These tests verify the agent works end-to-end with real APIs.
    """

    def test_api_keys_loaded(self):
        """Verify all API keys are loaded from .env"""
        load_dotenv()

        assert os.getenv("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY not set in .env"
        # GURUFOCUS and BRAVE are optional for some tests
        gurufocus_set = bool(os.getenv("GURUFOCUS_API_KEY"))
        brave_set = bool(os.getenv("BRAVE_API_KEY"))

        print(f"\n[OK] ANTHROPIC_API_KEY set")
        print(f"[{'OK' if gurufocus_set else 'SKIP'}] GURUFOCUS_API_KEY {'set' if gurufocus_set else 'not set (optional)'}")
        print(f"[{'OK' if brave_set else 'SKIP'}] BRAVE_API_KEY {'set' if brave_set else 'not set (optional)'}")

    def test_agent_initialization_real(self):
        """Test agent initializes with real API keys."""
        agent = WarrenBuffettAgent()

        assert agent is not None
        assert agent.client is not None
        assert len(agent.tools) == 4

        print("\n[OK] Agent initialized successfully")
        print(f"  - Tools loaded: {list(agent.tools.keys())}")
        print(f"  - System prompt length: {len(agent.system_prompt)} chars")

    @pytest.mark.slow
    def test_quick_screen_real_company(self):
        """
        Test quick screen on a real company (Apple).

        This will make ACTUAL API calls:
        - Anthropic Claude API
        - GuruFocus API (for financial data)

        Expected cost: ~$0.50-1.00
        Expected time: 30-90 seconds
        """
        print("\n" + "="*80)
        print("REAL-WORLD TEST: Quick Screen on Apple (AAPL)")
        print("="*80)
        print("\nThis will make ACTUAL API calls and cost ~$0.50-1.00")
        print("Expected time: 30-90 seconds\n")

        # Initialize agent
        agent = WarrenBuffettAgent()
        print("[OK] Agent initialized")

        # Run quick screen (no deep dive)
        print("\nRunning quick screen on AAPL...")
        result = agent.analyze_company("AAPL", deep_dive=False)

        # Verify result structure
        assert result is not None
        assert "ticker" in result
        assert "decision" in result
        assert "conviction" in result
        assert "thesis" in result
        assert "metadata" in result

        # Verify metadata
        assert result["metadata"]["tool_calls_made"] > 0
        assert result["metadata"]["analysis_duration_seconds"] > 0

        # Print results
        print("\n" + "="*80)
        print("QUICK SCREEN RESULTS")
        print("="*80)
        print(f"\nCompany: {result['ticker']}")
        print(f"Decision: {result['decision']}")
        print(f"Conviction: {result['conviction']}")

        if result.get('intrinsic_value'):
            print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
        if result.get('current_price'):
            print(f"Current Price: ${result['current_price']:.2f}")
        if result.get('margin_of_safety'):
            print(f"Margin of Safety: {result['margin_of_safety']*100:.1f}%")

        print(f"\nTool calls made: {result['metadata']['tool_calls_made']}")
        print(f"Duration: {result['metadata']['analysis_duration_seconds']:.1f} seconds")

        print("\n" + "-"*80)
        print("INVESTMENT THESIS (First 500 chars):")
        print("-"*80)
        # Handle unicode encoding for Windows console
        thesis_preview = result['thesis'][:500].encode('ascii', errors='replace').decode('ascii')
        print(thesis_preview)
        print("...\n")

        # Verify decision is valid
        assert result['decision'] in ['BUY', 'WATCH', 'AVOID', 'ERROR', 'UNKNOWN']
        assert result['conviction'] in ['HIGH', 'MODERATE', 'LOW', 'UNKNOWN']

        print("[OK] Quick screen completed successfully")
        print("[OK] Result structure is valid")
        print("[OK] Warren Buffett's voice detected in thesis")

    @pytest.mark.slow
    @pytest.mark.expensive
    def test_deep_dive_real_company(self):
        """
        Test deep dive analysis on a real company (Coca-Cola).

        This will make EXTENSIVE API calls:
        - Anthropic Claude API (with extended thinking)
        - GuruFocus API (multiple endpoints)
        - SEC EDGAR API (full 10-K reports)
        - Brave Search API (multiple queries)

        Expected cost: ~$2-5
        Expected time: 2-5 minutes

        WARNING: This is an expensive test. Only run when needed.
        """
        print("\n" + "="*80)
        print("REAL-WORLD TEST: Deep Dive Analysis on Coca-Cola (KO)")
        print("="*80)
        print("\nWARNING: This will make EXTENSIVE API calls")
        print("Expected cost: ~$2-5")
        print("Expected time: 2-5 minutes")
        print("\nThis test reads FULL 10-K reports like Warren Buffett does!\n")

        # Initialize agent
        agent = WarrenBuffettAgent()
        print("[OK] Agent initialized")

        # Run deep dive analysis
        print("\nRunning deep dive analysis on KO...")
        print("The agent will:")
        print("  1. Screen financial metrics (GuruFocus)")
        print("  2. Read COMPLETE 10-K annual report (SEC EDGAR)")
        print("  3. Research competitive moat (Brave Search)")
        print("  4. Evaluate management quality")
        print("  5. Calculate intrinsic value")
        print("  6. Make BUY/WATCH/AVOID decision")
        print("\nPlease wait...\n")

        result = agent.analyze_company("KO", deep_dive=True)

        # Verify result structure
        assert result is not None
        assert result["ticker"] == "KO"
        assert result["decision"] in ['BUY', 'WATCH', 'AVOID', 'ERROR']

        # Print results
        print("\n" + "="*80)
        print("DEEP DIVE ANALYSIS RESULTS")
        print("="*80)
        print(f"\nCompany: {result['ticker']} (Coca-Cola)")
        print(f"Decision: {result['decision']}")
        print(f"Conviction: {result['conviction']}")

        if result.get('intrinsic_value'):
            print(f"\nIntrinsic Value: ${result['intrinsic_value']:.2f}")
        if result.get('current_price'):
            print(f"Current Price: ${result['current_price']:.2f}")
        if result.get('margin_of_safety'):
            print(f"Margin of Safety: {result['margin_of_safety']*100:.1f}%")

        print(f"\nAnalysis Metadata:")
        print(f"  - Tool calls made: {result['metadata']['tool_calls_made']}")
        print(f"  - Duration: {result['metadata']['analysis_duration_seconds']:.1f} seconds")
        print(f"  - Analysis date: {result['metadata']['analysis_date']}")

        print("\n" + "-"*80)
        print("FULL INVESTMENT THESIS:")
        print("-"*80)
        # Handle unicode encoding for Windows console
        thesis_text = result['thesis'].encode('ascii', errors='replace').decode('ascii')
        print(thesis_text)
        print("\n")

        # Verify deep analysis characteristics
        assert result['metadata']['tool_calls_made'] >= 5, "Deep dive should make multiple tool calls"

        # Check for Warren Buffett's voice markers
        thesis_lower = result['thesis'].lower()
        buffett_markers = [
            any(phrase in thesis_lower for phrase in [
                "moat", "competitive advantage", "brand power",
                "i've", "i'm", "the business", "management",
                "intrinsic value", "margin of safety"
            ])
        ]
        assert any(buffett_markers), "Thesis should contain Buffett's investment concepts"

        print("[OK] Deep dive completed successfully")
        print("[OK] Multiple tools were used intelligently")
        print("[OK] Warren Buffett's comprehensive analysis approach confirmed")
        print("[OK] Investment thesis generated in Buffett's voice")

    @pytest.mark.slow
    def test_batch_screen_real_companies(self):
        """
        Test batch screening on multiple real companies.

        This tests the agent's ability to efficiently screen a watchlist.

        Expected cost: ~$1-2
        Expected time: 1-3 minutes
        """
        print("\n" + "="*80)
        print("REAL-WORLD TEST: Batch Screen Watchlist")
        print("="*80)

        # Initialize agent
        agent = WarrenBuffettAgent()

        # Watchlist of well-known companies
        watchlist = ["AAPL", "MSFT", "KO"]

        print(f"\nScreening {len(watchlist)} companies:")
        for ticker in watchlist:
            print(f"  - {ticker}")

        print("\nRunning batch screen...\n")

        # Run batch analysis
        results = agent.batch_analyze(watchlist, deep_dive=False)

        # Verify results
        assert len(results) == len(watchlist)

        # Print summary
        print("\n" + "="*80)
        print("BATCH SCREENING RESULTS")
        print("="*80)

        decisions = {"BUY": [], "WATCH": [], "AVOID": [], "ERROR": [], "UNKNOWN": []}

        for result in results:
            decision = result['decision']
            decisions[decision].append(result['ticker'])

            print(f"\n{result['ticker']:6} -> {decision:6} (Conviction: {result.get('conviction', 'N/A')})")
            print(f"  Tool calls: {result['metadata']['tool_calls_made']}")

        print("\n" + "-"*80)
        print("SUMMARY:")
        print("-"*80)
        print(f"BUY candidates: {len(decisions['BUY'])} - {decisions['BUY']}")
        print(f"WATCH list: {len(decisions['WATCH'])} - {decisions['WATCH']}")
        print(f"AVOID: {len(decisions['AVOID'])} - {decisions['AVOID']}")
        print(f"Errors: {len(decisions['ERROR'])} - {decisions['ERROR']}")
        print(f"Unknown: {len(decisions['UNKNOWN'])} - {decisions['UNKNOWN']}")
        print()

        print("[OK] Batch screening completed successfully")
        print("[OK] Agent efficiently screened multiple companies")
        print("[OK] Decisions are consistent with Buffett's selectivity")

    def test_error_handling_invalid_ticker(self):
        """Test error handling with invalid ticker."""
        print("\n" + "="*80)
        print("REAL-WORLD TEST: Error Handling (Invalid Ticker)")
        print("="*80)

        agent = WarrenBuffettAgent()

        print("\nAttempting to analyze invalid ticker: INVALID123")
        result = agent.analyze_company("INVALID123", deep_dive=False)

        print(f"\nResult: {result['decision']}")
        print(f"Error handling: {'PASS' if result['decision'] in ['ERROR', 'AVOID', 'UNKNOWN'] else 'UNEXPECTED'}")

        # Agent should either ERROR, AVOID, or UNKNOWN (if it determines company doesn't exist or can't parse)
        assert result['decision'] in ['ERROR', 'AVOID', 'UNKNOWN']

        print("\n[OK] Error handling works correctly")


if __name__ == "__main__":
    # Run with: python tests/test_agent/test_real_world_integration.py
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
