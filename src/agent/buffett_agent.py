"""
Warren Buffett AI Agent - Core Implementation

Module: src.agent.buffett_agent
Purpose: Main agent orchestration implementing Warren Buffett's investment analysis
Status: Complete - Sprint 3, Phase 5
Created: 2025-10-30

This module implements the autonomous AI agent that thinks, analyzes, and
communicates exactly like Warren Buffett. It uses Claude 4.5 Sonnet with
Extended Thinking to perform deep investment analysis.

Key Features:
- ReAct (Reasoning + Acting) loop for autonomous investigation
- Integration with all 4 tools (GuruFocus, SEC Filing, Web Search, Calculator)
- Warren Buffett's personality and investment philosophy
- Reads COMPLETE 10-K annual reports (not just excerpts)
- Patient, selective decision-making (comfortable saying "I'll pass")
- Comprehensive investment thesis generation
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import anthropic

from src.llm import LLMClient
from src.agent.buffett_prompt import (
    get_buffett_personality_prompt,
    get_tool_descriptions_for_prompt
)
from src.agent.universal_react import UniversalReActLoop
from src.tools.calculator_tool import CalculatorTool
from src.tools.gurufocus_tool import GuruFocusTool
from src.tools.web_search_tool import WebSearchTool
from src.tools.sec_filing_tool import SECFilingTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WarrenBuffettAgent:
    """
    Warren Buffett AI - Autonomous investment analysis agent.

    This agent thinks, analyzes, and communicates like Warren Buffett.
    It reads complete annual reports, studies business fundamentals,
    and makes patient, high-conviction investment decisions.

    The agent uses a ReAct (Reasoning + Acting) loop with Claude 4.5 Sonnet's
    Extended Thinking capability to perform deep, autonomous analysis.
    """

    # Model configuration
    MODEL = "claude-sonnet-4-20250514"  # Claude 4.5 Sonnet
    MAX_TOKENS = 20000  # Response limit (increased for comprehensive thesis generation)
    THINKING_BUDGET = 10000  # Extended thinking budget (must be < MAX_TOKENS)
    MAX_ITERATIONS = 30  # Maximum tool call iterations

    # Context window management
    MAX_CONTEXT_TOKENS = 200000  # Claude's max context
    CONTEXT_PRUNE_THRESHOLD = 100000  # Start pruning at 100K tokens (conservative for safety)
    MIN_RECENT_MESSAGES = 4  # Keep at least last 2 exchanges (user+assistant pairs)

    @property
    def current_year(self) -> int:
        """Get the current calendar year."""
        return datetime.now().year

    @property
    def most_recent_fiscal_year(self) -> int:
        """
        Get the most recent completed fiscal year for which 10-Ks are available.

        For most calendar-year companies, 10-Ks are filed 2-3 months after year end.
        So the most recent available 10-K is typically for the prior calendar year.

        Returns:
            int: Most recent fiscal year (current_year - 1)
        """
        return self.current_year - 1

    def __init__(self, api_key: Optional[str] = None, model_key: Optional[str] = None):
        """
        Initialize Warren Buffett AI Agent.

        Args:
            api_key: Anthropic API key (deprecated, use LLM_MODEL env var)
            model_key: LLM model to use (defaults to LLM_MODEL env var)

        Raises:
            ValueError: If required configuration is missing
        """
        # Initialize LLM client with plug-and-play model selection
        try:
            self.llm = LLMClient(model_key=model_key)
            logger.info(f"Initialized LLM: {self.llm.get_provider_info()}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise ValueError(f"LLM initialization failed: {e}")

        # Backward compatibility: if api_key provided, ensure it's set
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

        # Keep legacy client for anthropic-specific features (like error handling)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None  # Will use LLM abstraction

        # Initialize all 4 tools
        logger.info("Initializing tools...")
        self.tools = {
            "calculator": CalculatorTool(),
            "gurufocus": GuruFocusTool(),
            "web_search": WebSearchTool(),
            "sec_filing": SECFilingTool()
        }
        logger.info(f"Initialized {len(self.tools)} tools successfully")

        # Build system prompt with Buffett personality + tool descriptions
        self.system_prompt = self._build_system_prompt()
        logger.info(f"System prompt built ({len(self.system_prompt)} characters)")

    def _build_system_prompt(self) -> str:
        """
        Build complete system prompt with Buffett personality and tool descriptions.

        Returns:
            str: Complete system prompt for Claude
        """
        buffett_prompt = get_buffett_personality_prompt()
        tool_descriptions = get_tool_descriptions_for_prompt()

        return f"{buffett_prompt}\n\n{tool_descriptions}"

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Convert basīrah tools to Claude API tool format.

        Returns:
            List of tool definitions for Claude API
        """
        return [
            {
                "name": "gurufocus_tool",
                "description": self.tools["gurufocus"].description,
                "input_schema": self.tools["gurufocus"].parameters
            },
            {
                "name": "sec_filing_tool",
                "description": self.tools["sec_filing"].description,
                "input_schema": self.tools["sec_filing"].parameters
            },
            {
                "name": "web_search_tool",
                "description": self.tools["web_search"].description,
                "input_schema": self.tools["web_search"].parameters
            },
            {
                "name": "calculator_tool",
                "description": self.tools["calculator"].description,
                "input_schema": self.tools["calculator"].parameters
            }
        ]

    def analyze_company(
        self,
        ticker: str,
        deep_dive: bool = True,
        years_to_analyze: int = 3,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze a company like Warren Buffett would.

        This implements the complete investigation workflow:
        1. Initial Screen - Quick quantitative check
        2. Business Understanding - Read full 10-Ks
        3. Economic Moat - Assess competitive advantages
        4. Management Quality - Evaluate leadership
        5. Financial Analysis - Owner Earnings & ROIC
        6. Valuation - Calculate intrinsic value & margin of safety
        7. Risk Assessment - Identify top risks
        8. Decision - BUY / WATCH / AVOID

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            deep_dive: If True, reads full 10-Ks (Buffett style)
                      If False, quick screen only
            years_to_analyze: Number of years to analyze (1-10, default 3)
                            Includes current year + (years_to_analyze - 1) prior years
            progress_callback: Optional callback function for progress updates
                             Called with dict: {"stage": str, "progress": float, "message": str}

        Returns:
            {
                "ticker": str,
                "decision": "BUY" | "WATCH" | "AVOID",
                "conviction": "HIGH" | "MODERATE" | "LOW",
                "thesis": str,  # Full investment thesis in Buffett's voice
                "intrinsic_value": float | None,
                "current_price": float | None,
                "margin_of_safety": float | None,  # As decimal (e.g., 0.25 = 25%)
                "analysis_summary": {
                    "circle_of_competence": str,
                    "economic_moat": str,
                    "management_quality": str,
                    "financial_strength": str,
                    "valuation": str,
                    "risks": str
                },
                "metadata": {
                    "analysis_date": str,
                    "tool_calls_made": int,
                    "analysis_duration_seconds": float
                }
            }
        """
        start_time = datetime.now()

        # Store progress callback for use throughout analysis
        self._progress_callback = progress_callback

        # Reset token counters for this analysis
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        logger.info("=" * 80)
        logger.info(f"  Warren Buffett AI - Analyzing {ticker}")
        logger.info("=" * 80)

        try:
            # Route to appropriate analysis method
            if deep_dive:
                logger.info(f"Starting DEEP DIVE analysis with context management (analyzing {years_to_analyze} years)")
                result = self._analyze_deep_dive_with_context_management(ticker, years_to_analyze)
            else:
                logger.info("Starting QUICK SCREEN analysis")
                result = self._analyze_quick_screen(ticker)

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            result["metadata"]["analysis_duration_seconds"] = duration

            logger.info("=" * 80)
            logger.info(f"  Analysis Complete - Decision: {result['decision']}")
            logger.info("=" * 80)

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return {
                "ticker": ticker,
                "decision": "ERROR",
                "conviction": "NONE",
                "thesis": f"Analysis failed: {str(e)}",
                "intrinsic_value": None,
                "current_price": None,
                "margin_of_safety": None,
                "analysis_summary": {},
                "metadata": {
                    "analysis_date": datetime.now().isoformat(),
                    "tool_calls_made": 0,
                    "analysis_duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "error": str(e)
                }
            }

    def _analyze_quick_screen(self, ticker: str) -> Dict[str, Any]:
        """
        Perform quick screen analysis (original single-pass implementation).

        This works well for quick screens since context doesn't get too large.

        Args:
            ticker: Stock ticker

        Returns:
            Analysis result with decision
        """
        initial_message = self._get_quick_screen_prompt(ticker)
        return self._run_analysis_loop(ticker, initial_message)

    def _analyze_deep_dive_with_context_management(
        self,
        ticker: str,
        years_to_analyze: int = 3
    ) -> Dict[str, Any]:
        """
        Perform deep dive analysis with progressive summarization.

        This implements a 3-stage process to manage context window:

        Stage 1: Analyze current year in full detail (keep in context)
        Stage 2: Analyze prior years, creating summaries (replace full text with summaries)
        Stage 3: Synthesize findings across all years for final decision

        This keeps context under 200K tokens while maintaining Warren Buffett's
        thorough multi-year analysis approach.

        Args:
            ticker: Stock ticker
            years_to_analyze: Number of years to analyze (1-10, default 3)
                            Includes current year + (years_to_analyze - 1) prior years

        Returns:
            Complete investment thesis with multi-year insights
        """
        logger.info(f"=" * 80)
        logger.info(f"DEEP DIVE WITH CONTEXT MANAGEMENT: {ticker}")
        logger.info(f"=" * 80)

        # Stage 1: Current Year Full Analysis (0-40% progress)
        logger.info(f"\n[STAGE 1] Analyzing current year ({self.most_recent_fiscal_year}) 10-K in detail...")
        self._report_progress(
            stage="current_year",
            progress=0.0,
            message=f"📖 Stage 1: Reading most recent 10-K (FY {self.most_recent_fiscal_year})..."
        )
        current_year_analysis = self._analyze_current_year(ticker)
        logger.info(f"[STAGE 1] Complete. Estimated tokens: ~{current_year_analysis.get('token_estimate', 0)}")
        self._report_progress(
            stage="current_year",
            progress=0.4,
            message=f"✅ Stage 1 Complete: FY {self.most_recent_fiscal_year} analyzed"
        )

        # Stage 2: Prior Years with Summarization (40-80% progress)
        # years_to_analyze includes current year, so subtract 1 for prior years
        num_prior_years = max(0, years_to_analyze - 1)
        logger.info(f"\n[STAGE 2] Analyzing prior years with summarization... (analyzing {num_prior_years} prior years)")

        if num_prior_years > 0:
            self._report_progress(
                stage="prior_years",
                progress=0.4,
                message=f"📚 Stage 2: Analyzing {num_prior_years} prior years..."
            )

        prior_years_summaries, missing_years = self._analyze_prior_years(ticker, num_years=num_prior_years, years_to_analyze=years_to_analyze)
        total_prior_tokens = sum(p.get('token_estimate', 0) for p in prior_years_summaries)

        # Log comprehensive summary of analysis coverage
        actual_years_analyzed = len(prior_years_summaries)
        if missing_years:
            logger.info(
                f"[STAGE 2] Complete. {actual_years_analyzed} years successfully analyzed. "
                f"Skipped {len(missing_years)} years (10-Ks not available). Tokens: ~{total_prior_tokens}"
            )
        else:
            logger.info(f"[STAGE 2] Complete. {actual_years_analyzed} years summarized. Tokens: ~{total_prior_tokens}")

        if num_prior_years > 0:
            self._report_progress(
                stage="prior_years",
                progress=0.8,
                message=f"✅ Stage 2 Complete: {num_prior_years} prior years analyzed"
            )

        # Stage 3: Multi-Year Synthesis (80-100% progress)
        logger.info("\n[STAGE 3] Synthesizing multi-year findings...")
        self._report_progress(
            stage="synthesis",
            progress=0.8,
            message=f"🧠 Stage 3: Synthesizing {years_to_analyze}-year analysis..."
        )
        final_thesis = self._synthesize_multi_year_analysis(
            ticker=ticker,
            current_year=current_year_analysis,
            prior_years=prior_years_summaries
        )
        logger.info(f"[STAGE 3] Complete. Final decision: {final_thesis['decision']}")
        self._report_progress(
            stage="synthesis",
            progress=1.0,
            message=f"✅ Analysis Complete: Decision is {final_thesis['decision']}"
        )

        # Add context management metadata
        total_token_estimate = (
            current_year_analysis.get('token_estimate', 0) +
            total_prior_tokens
        )

        # Determine overall strategy based on current year approach
        current_year_strategy = current_year_analysis.get('strategy', 'standard')
        adaptive_used = current_year_strategy == 'adaptive_summarization'

        final_thesis["metadata"]["context_management"] = {
            "strategy": current_year_strategy,  # 'standard' or 'adaptive_summarization'
            "current_year_tokens": current_year_analysis.get('token_estimate', 0),
            "prior_years_tokens": total_prior_tokens,
            "total_token_estimate": total_token_estimate,
            "years_analyzed": [current_year_analysis.get('year')] + [p['year'] for p in prior_years_summaries],
            "years_requested": years_to_analyze,
            "years_skipped": missing_years if missing_years else None,  # List of years with no 10-K available
            "years_skipped_count": len(missing_years),

            # Additional fields for adaptive strategy
            "adaptive_used": adaptive_used,
            "filing_size": current_year_analysis.get('filing_size'),
            "summary_size": current_year_analysis.get('summary_size'),
            "reduction_percent": current_year_analysis.get('reduction_percent')
        }

        logger.info(f"\nTotal estimated context: ~{total_token_estimate} tokens")
        logger.info(f"Strategy: {current_year_strategy}" + (f" (adaptive applied to large filing)" if adaptive_used else ""))
        logger.info(f"Years analyzed: {final_thesis['metadata']['context_management']['years_analyzed']}")
        if missing_years:
            logger.info(f"Years skipped (no 10-K available): {sorted(missing_years, reverse=True)}")

        return final_thesis

    def _get_deep_dive_prompt(self, ticker: str) -> str:
        """
        Get the prompt for deep-dive analysis (full Buffett process).

        Args:
            ticker: Stock ticker

        Returns:
            str: Prompt for agent
        """
        return f"""I'd like you to analyze {ticker} as an investment opportunity.

Please follow your standard process:

1. **Initial Screen**: Use GuruFocus to check quantitative metrics
   - ROIC >15%?
   - Manageable debt?
   - Consistent earnings?
   - If metrics look poor, feel free to PASS immediately

2. **Deep Dive** (if initial screen passes):
   - Read the COMPLETE 10-K (section="full") for current year
   - Read previous 2-3 years of 10-Ks for historical context
   - Understand the business deeply
   - If you can't explain it simply, PASS (circle of competence)

3. **Economic Moat**: Assess competitive advantages
   - Brand, network effects, switching costs, cost advantages?
   - Durable for 10+ years?
   - Compare to competitors if helpful

4. **Management Quality**: Evaluate leadership
   - Read MD&A across multiple years
   - Check proxy statement (DEF 14A) for compensation
   - Honest and transparent communication?

5. **Financial Strength**: Analyze fundamentals
   - Owner Earnings calculation
   - ROIC trends
   - Free cash flow
   - Debt levels

6. **Risk Assessment**: Identify potential issues
   - Read Risk Factors section
   - Recent news and controversies
   - What could permanently impair the business?

7. **Valuation & Decision**:
   - Calculate intrinsic value (DCF with conservative assumptions)
   - Determine margin of safety vs current price
   - Make decision: BUY / WATCH / AVOID
   - Include structured decision in your final response:
     **DECISION: [BUY/WATCH/AVOID]**
     **CONVICTION: [HIGH/MODERATE/LOW]**
     **INTRINSIC VALUE: $XXX** (if calculated)
     **CURRENT PRICE: $XXX** (if known)
     **MARGIN OF SAFETY: XX%** (if calculated)

Take your time. Read the full annual reports. Think deeply. And remember -
it's perfectly fine to say "I don't understand this" or "The price isn't right."

You don't have to swing at every pitch.
"""

    def _get_quick_screen_prompt(self, ticker: str) -> str:
        """
        Get the prompt for enhanced quick screening.

        This generates a 1-year business snapshot with a clear recommendation
        on whether the company deserves a full deep dive analysis.

        Args:
            ticker: Stock ticker

        Returns:
            str: Enhanced prompt for agent
        """
        return f"""I'd like you to do an ENHANCED QUICK SCREEN on {ticker}.

This is a rapid 1-year business snapshot to help me decide if this company
deserves a full deep dive (spending 7+ minutes reading complete annual reports
and $3-4 in analysis costs).

**YOUR PROCESS:**

**Phase 1: Get the Numbers (GuruFocus)**
Use GuruFocus to check core metrics:
- ROIC (need >15% for quality businesses)
- Debt/Equity ratio (prefer <0.7)
- Financial Strength Score
- Profitability trends
- Revenue growth

**Phase 2: Understand the Business (SEC Filing)**
Read the most recent 10-K but ONLY these sections:
- section="business" (understand what they do)
- Don't read full 10-K yet - that's for deep dive

Get clarity on:
- What products/services do they sell?
- Who are their customers?
- What industry/market?
- Basic business model

**Phase 3: Quick Moat Check (Web Search if needed)**
Look for obvious competitive advantages:
- Brand power?
- High switching costs?
- Network effects?
- Cost advantages?
- Pricing power?

**YOUR OUTPUT:**

Provide a structured 1-year snapshot in this exact format:

---

# ⚡ WARREN'S QUICK SCREEN: {ticker}

## 1. Business at a Glance (2-3 paragraphs)

Explain what {ticker} does in plain English:
- What products/services they sell
- Who buys from them (customers)
- How they make money (business model)
- What industry/market they operate in
- Basic market position

Make this so clear that someone unfamiliar with the company can understand
it in 30 seconds. Use your simple, folksy language.

## 2. Financial Health Snapshot (Current Year)

Present the key metrics clearly:

**Core Metrics:**
- Revenue: $XXB (±X% YoY)
- Operating Margin: X%
- Net Margin: X%
- ROIC: X% (vs 15% hurdle)
- Debt/Equity: X.X

**Quick Assessment:**
[2-3 sentences on financial strength - excellent/good/concerning/poor]

## 3. Economic Moat (Quick Take)

**Moat Assessment:** Strong / Moderate / Weak / None

[2-3 paragraphs explaining:]
- What competitive advantages (if any) are evident?
- Any obvious pricing power?
- High customer switching costs?
- Brand strength?
- Be honest - if no moat is visible, say so

## 4. Red Flags 🚩 & Green Flags ✅

**Green Flags (Positive Signs):**
- [Flag 1 with brief explanation]
- [Flag 2 with brief explanation]
- [Flag 3 with brief explanation]

**Red Flags (Concerns):**
- [Flag 1 with brief explanation]
- [Flag 2 with brief explanation]
- [Flag 3 with brief explanation]

Be specific. Use actual numbers and facts.

## 5. My Deep Dive Recommendation

[This is the KEY section - be decisive and clear]

**RECOMMENDATION:** 🟢 INVESTIGATE or 🔴 PASS

[3-4 paragraphs explaining your decision:]

If **INVESTIGATE** (recommend deep dive):
- Why this business has potential
- What specific aspects deserve deeper investigation
- What you'd look for in the full 10-K
- Estimated value at first glance
- Why it's worth spending $3-4 and 7+ minutes

If **PASS** (skip deep dive):
- What disqualifies this business
- Why the numbers/business model don't work
- What would have to change for you to reconsider
- Why your time is better spent elsewhere
- Be blunt but fair

**Confidence Level:** HIGH / MODERATE / LOW

[1-2 sentences on why you're confident or uncertain]

---

**DECISION: [INVESTIGATE / PASS]**
**CONVICTION: [HIGH / MODERATE / LOW]**

---

**CRITICAL REQUIREMENTS:**

1. **Be decisive** - Users need clear guidance on whether to spend $3-4 on deep dive
2. **Be honest** - If ROIC is 8%, say it's below your 15% hurdle and explain why that matters
3. **Be specific** - Use actual numbers, not vague statements
4. **Be concise** - Target 800-1,000 words total (much shorter than deep dive's 3,500)
5. **Be helpful** - Users should walk away with clear understanding of business + recommendation
6. **Use your voice** - Sound like Warren Buffett explaining to a friend over coffee

Remember: This quick screen costs $1-2 and takes 2-3 minutes. Its purpose is to
help investors decide whether to invest $3-4 and 7+ minutes in a full deep dive.
Be the filter that saves them from wasting time on weak businesses.

Good businesses with bad prices → INVESTIGATE (might be opportunity)
Bad businesses → PASS (no price makes a bad business good)
Confusing businesses → PASS (circle of competence)
"""

    # ========================================================================
    # CONTEXT MANAGEMENT: 3-STAGE PROGRESSIVE SUMMARIZATION
    # ========================================================================

    def _analyze_current_year(self, ticker: str) -> Dict[str, Any]:
        """
        Stage 1: Analyze current year 10-K with adaptive strategy.

        ADAPTIVE LOGIC:
        - For normal-sized 10-Ks (<400K chars): Use standard approach (keep full analysis)
        - For large 10-Ks (>400K chars): Use summarization approach (compress to ~10K tokens)

        This ensures all companies stay under 200K token limit while maintaining quality.

        Args:
            ticker: Stock ticker

        Returns:
            {
                'year': int,
                'full_analysis': str,
                'tool_calls_made': int,
                'token_estimate': int,
                'strategy': 'standard' | 'adaptive_summarization',
                'filing_size': int
            }
        """
        logger.info(f"Analyzing current fiscal year ({self.most_recent_fiscal_year}) 10-K for {ticker}")

        # Pre-fetch 10-K to check size and determine strategy
        logger.info(f"Pre-fetching 10-K to determine analysis strategy...")

        try:
            filing_result = self.tools["sec_filing"].execute(
                ticker=ticker,
                filing_type="10-K",
                section="full"
            )

            if not filing_result.get("success"):
                logger.error(f"Failed to fetch 10-K for {ticker}: {filing_result.get('error')}")
                raise Exception(f"Failed to retrieve 10-K: {filing_result.get('error')}")

            filing_content = filing_result["data"]["content"]
            filing_size = len(filing_content)

            # ADAPTIVE THRESHOLD: 400K characters
            LARGE_FILING_THRESHOLD = 400000

            if filing_size > LARGE_FILING_THRESHOLD:
                logger.warning(
                    f"Large filing detected for {ticker}: {filing_size:,} characters "
                    f"(>{LARGE_FILING_THRESHOLD:,} threshold). "
                    f"Using ADAPTIVE SUMMARIZATION strategy."
                )
                return self._analyze_current_year_with_summarization(ticker, filing_size)
            else:
                logger.info(
                    f"Normal filing size for {ticker}: {filing_size:,} characters "
                    f"(<={LARGE_FILING_THRESHOLD:,} threshold). "
                    f"Using STANDARD strategy."
                )
                return self._analyze_current_year_standard(ticker, filing_size)

        except Exception as e:
            logger.error(f"Error in adaptive current year analysis: {e}")
            # Fallback to standard approach if size detection fails
            logger.warning("Falling back to standard approach")
            return self._analyze_current_year_standard(ticker, filing_size=None)

    def _analyze_current_year_standard(self, ticker: str, filing_size: int = None) -> Dict[str, Any]:
        """
        Standard approach for normal-sized 10-Ks (<400K characters).

        This is the ORIGINAL implementation that works perfectly for Apple, Microsoft, etc.
        Keeps full analysis in context for synthesis.

        Args:
            ticker: Stock ticker
            filing_size: Pre-fetched filing size (optional)

        Returns:
            Analysis result with strategy='standard'
        """
        logger.info(f"Running STANDARD current year analysis for {ticker}")

        current_year_prompt = f"""I'd like you to analyze {ticker}'s most recent 10-K annual report.

**YOUR TASK:**

Perform a thorough current-year analysis following these steps:

1. **Financial Screening** - Use GuruFocus to get:
   - Current ROIC, margins, debt levels
   - 10-year financial trends
   - Profitability metrics

2. **Read Complete 10-K** - Use SEC Filing Tool:
   - section="full" (read the whole thing!)
   - Current fiscal year
   - This is the primary source - read it carefully

3. **Business Understanding**:
   - What does the company do? (simple terms)
   - How do they make money?
   - Is this within your circle of competence?

4. **Economic Moat**:
   - Identify competitive advantages
   - Use Web Search to validate market perception
   - Assess durability (10+ years?)

5. **Management Quality**:
   - Read MD&A section from 10-K
   - Check compensation via GuruFocus or proxy
   - Capital allocation track record?

6. **Financial Strength**:
   - Use Calculator for Owner Earnings
   - Analyze cash flow sustainability
   - Debt levels manageable?

7. **Risk Assessment**:
   - Read Risk Factors section thoroughly
   - Search for recent news/controversies
   - What are the major threats?

8. **Preliminary Valuation**:
   - Use Calculator for conservative DCF
   - Estimate intrinsic value range
   - Current price vs value?

**IMPORTANT:**

This is ONLY the current year analysis. You'll analyze prior years next to identify
trends. So focus on understanding the business as it stands today.

At the end, provide a summary of your key findings from the current year. We'll use
this as a baseline to compare against historical performance.

Take your time. Be thorough. This is the foundation of your multi-year analysis.
"""

        # Run analysis on current year
        result = self._run_analysis_loop(ticker, current_year_prompt)

        # Estimate tokens (rough: 1 token ≈ 4 characters)
        token_estimate = len(result.get('thesis', '')) // 4

        return {
            'year': self.most_recent_fiscal_year,
            'full_analysis': result.get('thesis', ''),
            'tool_calls_made': result.get('metadata', {}).get('tool_calls_made', 0),
            'token_estimate': token_estimate,
            'strategy': 'standard',
            'filing_size': filing_size
        }

    def _analyze_current_year_with_summarization(self, ticker: str, filing_size: int) -> Dict[str, Any]:
        """
        Adaptive approach for exceptionally large 10-Ks (>400K characters).

        For companies like Coca-Cola with massive filings, this approach:
        1. Agent reads full 10-K and analyzes with tools
        2. Agent creates comprehensive summary (~8-10K tokens)
        3. Summary replaces full analysis in context
        4. Allows analysis of ANY size 10-K while staying under 200K limit

        Args:
            ticker: Stock ticker
            filing_size: Size of the 10-K in characters

        Returns:
            Analysis result with strategy='adaptive_summarization' and compressed summary
        """
        logger.info(
            f"Running ADAPTIVE SUMMARIZATION for {ticker} "
            f"(filing size: {filing_size:,} characters)"
        )

        summarization_prompt = f"""I'd like you to analyze {ticker}'s most recent 10-K annual report.

**IMPORTANT - LARGE FILING NOTICE:**

This company has an exceptionally large 10-K filing ({filing_size:,} characters).
To manage context efficiently, I need you to:

1. Perform your complete, thorough analysis using all necessary tools
2. Read the full 10-K carefully (section="full")
3. Use GuruFocus, Calculator, Web Search as needed
4. **At the end, create a COMPREHENSIVE SUMMARY (8-10K tokens)**

**YOUR ANALYSIS PROCESS:**

1. **Financial Screening** (GuruFocus):
   - ROIC, margins, debt levels, 10-year trends

2. **Read Complete 10-K** (SEC Filing Tool):
   - section="full" (read everything)
   - Focus on: Business, MD&A, Risk Factors, Financials

3. **Business Understanding**:
   - What does the company do? (simple explanation)
   - How do they make money?
   - Within circle of competence?

4. **Economic Moat** (10-K + Web Search):
   - Brand power, network effects, switching costs
   - Market perception and competitive position
   - Durability assessment (10+ years?)

5. **Management Quality** (10-K):
   - Read MD&A across sections
   - Capital allocation track record
   - Communication style (candid vs obfuscated?)

6. **Financial Strength** (Calculator + 10-K):
   - Owner Earnings calculation
   - Cash flow analysis and sustainability
   - Debt levels manageable?

7. **Risk Assessment** (10-K + Web Search):
   - Read Risk Factors thoroughly
   - Recent news and controversies
   - Major threats to business model

8. **Preliminary Valuation** (Calculator):
   - DCF with conservative assumptions
   - Intrinsic value estimate
   - Margin of safety

**CRITICAL - CREATE COMPREHENSIVE SUMMARY:**

After completing your analysis, create a summary using this EXACT format:

===== {ticker.upper()} CURRENT YEAR (2024) ANALYSIS SUMMARY =====

**BUSINESS OVERVIEW:**
[3-4 paragraphs explaining what the company does, how they make money,
competitive position, and business model. Use Warren Buffett's simple,
clear language.]

**FINANCIAL PERFORMANCE (2024):**
- Revenue: $X.XB (±X% YoY)
- Operating Margin: X.X%
- Net Income: $X.XB
- ROIC: X.X%
- Debt/Equity: X.XX
- Free Cash Flow: $X.XB
- Owner Earnings: $X.XB (calculated)
- EPS: $X.XX

**ECONOMIC MOAT ASSESSMENT:**
[2-3 paragraphs analyzing competitive advantages: brand power, network
effects, switching costs, cost advantages, regulatory barriers. Include
evidence from 10-K and market research. Rate: STRONG/MODERATE/WEAK]

**MANAGEMENT QUALITY:**
[2-3 paragraphs on CEO/leadership, capital allocation decisions,
compensation philosophy, track record. Include 1-2 key quotes from MD&A
that reveal management thinking. Rate: EXCELLENT/GOOD/CONCERNING]

**KEY RISKS IDENTIFIED:**
1. [Most significant risk with explanation]
2. [Second major risk]
3. [Third risk]
4. [Fourth risk]
5. [Fifth risk]

**PRELIMINARY VALUATION:**
- Intrinsic Value Estimate: $XXX per share
- DCF Assumptions: [growth rate, discount rate, terminal growth]
- Current Market Price: $XXX
- Preliminary Margin of Safety: XX%

**CIRCLE OF COMPETENCE:**
[Can you explain this business clearly? Is it understandable? YES/UNCERTAIN/NO]

**KEY INSIGHTS FROM 10-K:**
- [Critical insight 1 from annual report]
- [Critical insight 2]
- [Critical insight 3]
- [Notable management quotes or statements]

===== END CURRENT YEAR SUMMARY =====

**TARGET LENGTH:** 8,000-10,000 tokens (comprehensive but concise)

This summary will be compared against prior years to identify trends and make
the final investment decision. Include all essential information for multi-year
comparison.
"""

        # Run analysis with summarization instructions
        result = self._run_analysis_loop(ticker, summarization_prompt)

        # Extract the structured summary from response
        full_response = result.get('thesis', '')
        summary = self._extract_summary_from_response(
            full_response,
            year=2024,
            ticker=ticker
        )

        # Calculate reduction metrics
        original_response_size = len(full_response)
        summary_size = len(summary)
        reduction_pct = ((original_response_size - summary_size) / original_response_size * 100) if original_response_size > 0 else 0

        # Estimate tokens
        token_estimate = len(summary) // 4

        logger.info(
            f"Adaptive summarization complete for {ticker}:\n"
            f"  Filing size: {filing_size:,} chars\n"
            f"  Full response: {original_response_size:,} chars\n"
            f"  Extracted summary: {summary_size:,} chars (~{token_estimate:,} tokens)\n"
            f"  Reduction: {reduction_pct:.1f}%"
        )

        return {
            'year': self.most_recent_fiscal_year,
            'full_analysis': summary,  # Use summary instead of full response
            'tool_calls_made': result.get('metadata', {}).get('tool_calls_made', 0),
            'token_estimate': token_estimate,
            'strategy': 'adaptive_summarization',
            'filing_size': filing_size,
            'summary_size': summary_size,
            'original_response_size': original_response_size,
            'reduction_percent': reduction_pct
        }

    def _analyze_prior_years(self, ticker: str, num_years: int = 2, years_to_analyze: int = 3) -> List[Dict[str, Any]]:
        """
        Stage 2: Analyze prior years and create concise summaries.

        For each prior year:
        1. Read the full 10-K
        2. Extract key insights
        3. Create 2-3K token summary
        4. Return summary (NOT full text)

        This prevents context overflow while maintaining historical perspective.

        Args:
            ticker: Stock ticker
            num_years: Number of prior years to analyze (default: 2)
            years_to_analyze: Total years being analyzed (for progress calculation)

        Returns:
            Tuple of (summaries, missing_years):
            - summaries: List of year summaries for successfully analyzed years
            - missing_years: List of fiscal years where 10-Ks were not available (sorted desc)

            Example:
            (
                [{'year': 2023, 'summary': '...', ...}, {'year': 2022, 'summary': '...', ...}],
                [2018, 2017, 2016]  # Missing years
            )
        """
        summaries = []
        missing_years = []  # Track years where 10-Ks weren't available
        most_recent_year = self.most_recent_fiscal_year

        for i in range(num_years):
            year = most_recent_year - 1 - i  # 2023, 2022, etc. (starting from year before most recent)
            year_number = i + 2  # Year 2 of total analysis (after most recent which is year 1)

            # Calculate progress within Stage 2 (40-80% overall)
            # Stage 2 covers 40% of total progress, distributed across prior years
            if num_years > 0:
                year_progress_start = 0.4 + (i / num_years) * 0.4
                year_progress_end = 0.4 + ((i + 1) / num_years) * 0.4
            else:
                year_progress_start = 0.4
                year_progress_end = 0.8

            logger.info(f"  Checking availability of {year} 10-K for {ticker}...")

            # Pre-check if filing exists to avoid wasting iterations
            try:
                filing_check = self.tools["sec_filing"].execute(
                    ticker=ticker,
                    filing_type="10-K",
                    section="full",
                    year=year
                )

                if not filing_check.get("success"):
                    logger.warning(f"  Skipping {year}: 10-K not available ({filing_check.get('error', 'unknown error')})")
                    logger.info(f"  Note: This is common for companies spun off from parent companies or with limited filing history")
                    missing_years.append(year)  # Track missing year
                    continue

            except Exception as e:
                logger.warning(f"  Skipping {year}: Unable to retrieve 10-K ({str(e)})")
                missing_years.append(year)  # Track missing year
                continue

            logger.info(f"  Analyzing {year} 10-K for {ticker}...")
            self._report_progress(
                stage="prior_years",
                progress=year_progress_start,
                message=f"📅 Year {year_number} of {years_to_analyze}: Reading FY {year} 10-K..."
            )

            prior_year_prompt = f"""I'd like you to analyze {ticker}'s {year} annual report (10-K).

**CONTEXT:**

You've already analyzed the most recent fiscal year ({self.most_recent_fiscal_year}). Now we're looking at {year} to
identify trends and changes over time.

**YOUR TASK:**

1. **Read the {year} 10-K**: Use SEC Filing Tool
   - ticker: "{ticker}"
   - filing_type: "10-K"
   - section: "full"
   - year: {year}

2. **Extract Key Information**:
   - Revenue, margins, ROIC for {year}
   - Business model or strategy changes vs today
   - Management commentary and priorities
   - Major risk factors disclosed
   - Significant events in {year}

3. **Create a Concise Summary** (CRITICAL):

   Your summary MUST be 2-3K tokens maximum and follow this structure:

   === {year} ANNUAL REPORT SUMMARY ===

   **Business & Strategy ({year}):**
   - Core operations and market positioning
   - Any notable changes from prior year
   - Strategic priorities mentioned

   **Financial Performance ({year}):**
   - Revenue: $X.XB (±X% YoY)
   - Operating Margin: X%
   - ROIC: X%
   - Debt/Equity: X.X
   - Free Cash Flow: $X.XB
   - EPS: $X.XX

   **Management Insights:**
   - 2-3 key quotes from MD&A
   - Capital allocation decisions
   - How they addressed challenges

   **Risk Factors ({year}):**
   - Top 5 risks disclosed
   - Any new risks vs prior year

   **Notable Changes:**
   - What changed in {year}?
   - How does {year} compare to current year?

   **Trends & Patterns:**
   - Improving, stable, or declining?
   - Consistency in execution?

   === END {year} SUMMARY ===

**CRITICAL REQUIREMENT:**

Keep your summary under 3,000 tokens while capturing all essential insights.
Be concise but thorough. This summary will be used to identify multi-year
trends without overwhelming the context window.

Focus on facts and metrics that matter for long-term investment decisions.
"""

            # Analyze this prior year
            result = self._run_analysis_loop(ticker, prior_year_prompt)

            # Extract the summary from the response
            summary_text = self._extract_summary_from_response(
                result.get('thesis', ''),
                year=year
            )

            # Extract key metrics
            key_metrics = self._extract_metrics_from_summary(summary_text)

            # Estimate tokens
            token_estimate = len(summary_text) // 4

            summaries.append({
                'year': year,
                'summary': summary_text,
                'key_metrics': key_metrics,
                'token_estimate': token_estimate
            })

            logger.info(f"  Created {year} summary: ~{token_estimate} tokens")

            # Report progress for this completed year
            self._report_progress(
                stage="prior_years",
                progress=year_progress_end,
                message=f"✅ Year {year_number} of {years_to_analyze} complete: FY {year} analyzed"
            )

        # Log summary of missing years
        if missing_years:
            logger.warning(f"Skipped {len(missing_years)} years due to unavailable 10-Ks: {', '.join(map(str, sorted(missing_years, reverse=True)))}")

        return summaries, missing_years

    def _get_complete_thesis_prompt(
        self,
        ticker: str,
        current_year: Dict[str, Any],
        prior_years: List[Dict[str, Any]]
    ) -> str:
        """
        Get synthesis prompt that ensures COMPLETE investment thesis generation.

        This prompt explicitly requires all 10 sections of a Warren Buffett-style
        comprehensive analysis, preventing the agent from generating only conclusions.

        Args:
            ticker: Stock ticker
            current_year: Current year analysis results
            prior_years: Prior years summaries

        Returns:
            Complete synthesis prompt with explicit structure
        """
        # Build prior years section
        prior_years_text = ""
        for prior in prior_years:
            prior_years_text += f"""
**{prior['year']} SUMMARY:**

{prior['summary']}

---

"""

        # Total years analyzed
        total_years = len([current_year] + prior_years)

        synthesis_prompt = f"""You've completed a thorough multi-year analysis of {ticker}.
Now it's time to write your COMPLETE investment thesis as you would in one of
your Berkshire Hathaway shareholder letters.

**CURRENT YEAR (2024) - FULL ANALYSIS:**

{current_year['full_analysis']}

---

**PRIOR YEARS - SUMMARIES:**

{prior_years_text}

---

**YOUR TASK: Write a COMPLETE Investment Thesis**

Warren, write a comprehensive investment thesis for {ticker} that includes ALL of
these sections. This should be a complete analysis that any investor could read
to understand the entire investment case.

**REQUIRED STRUCTURE - YOU MUST INCLUDE ALL 10 SECTIONS:**

## **1. Business Overview** (3-4 paragraphs)

Start by explaining what {ticker} actually does:
- What products/services do they sell?
- Who are their customers?
- How do they make money?
- What industry are they in?
- Market position and size
- Geographic footprint

Make this so clear that someone who's never heard of this company can understand
it. Use your simple, plain language.

## **2. Economic Moat Analysis** (4-5 paragraphs)

This is critical. Explain their competitive advantages in detail:

**Identify the moat type(s):**
- Brand Power? (examples of customer loyalty, pricing power)
- Network Effects? (gets better with more users)
- Switching Costs? (customers can't easily leave)
- Cost Advantages? (economies of scale)
- Intangible Assets? (patents, licenses, regulatory barriers)

**Provide specific evidence:**
- Market share data
- Customer retention rates
- Pricing trends vs competitors
- Examples from the 10-Ks of moat strength
- Competitive dynamics you observed

**Assess durability:**
- Will this moat last 10+ years?
- Is it strengthening or weakening?
- What threats could erode it?

## **3. Management Quality** (3-4 paragraphs)

Evaluate the leadership team:

**Competence:**
- Track record of execution across the years you analyzed
- Strategic decisions and outcomes
- Industry expertise

**Integrity:**
- Honest communication in MD&A sections?
- Conservative or aggressive accounting?
- How they discuss setbacks
- Specific quotes from filings

**Capital Allocation:**
- Historical ROIC on reinvested capital
- M&A decisions (if any)
- Dividend/buyback policy
- Share count trends

**Owner Mentality:**
- Insider ownership
- Compensation structure
- Long-term thinking vs short-term pressure

## **4. Financial Analysis** (5-6 paragraphs)

Deep dive into the numbers across the {total_years} years you analyzed:

**Revenue & Growth:**
Create a table showing trends:
```
2024: $X.XB (±X% YoY)
2023: $X.XB (±X% YoY)
[...for each year analyzed...]

Overall trend: Accelerating / Stable / Declining?
CAGR: X%
```

**Profitability Trends:**
```
Gross Margin:     2024: X%  →  [first year]: X%  (expanding/stable/declining)
Operating Margin: 2024: X%  →  [first year]: X%  (expanding/stable/declining)
Net Margin:       2024: X%  →  [first year]: X%  (expanding/stable/declining)
```

**ROIC & Capital Efficiency:**
```
ROIC trend:  2024: X%  →  [first year]: X%
Average ROIC: X% over {total_years}-year period
Consistency: High / Moderate / Volatile
vs 15% hurdle: Passes / Fails / Marginal
```

**Balance Sheet Strength:**
```
Debt/Equity: X.X (trending up/down/stable)
Interest Coverage: Xx (comfortable/tight)
Cash vs Debt: $X.XB cash vs $X.XB debt
Working Capital: [trends]
```

**Cash Flow Quality:**
```
Owner Earnings: $X.XB in 2024 (vs $X.XB in [first year])
Growth: X% CAGR
FCF vs Net Income: [conversion rate]
Capital intensity: Low / Moderate / High
```

Explain what these numbers tell you about business quality.

## **5. Growth Prospects** (3-4 paragraphs)

Where is future growth coming from?

**Organic Growth Drivers:**
- Market expansion (geographic, demographic)
- New products/services in pipeline
- Pricing power opportunities
- Market share gain potential

**Total Addressable Market (TAM):**
- How big is the opportunity?
- Current market share: X%
- Room to expand?

**Management's Growth Strategy:**
- What are they saying in recent 10-Ks?
- Are they executing on stated plans?
- Is strategy realistic or overly optimistic?

**Your Assessment:**
- Conservative growth estimate: X% annually
- Based on which specific factors?
- What could accelerate or decelerate growth?

## **6. Competitive Position** (3-4 paragraphs)

Who are they competing against?

**Key Competitors:**
- List the main competitors
- Market share comparison (if available)
- How does {ticker} compare on moat, financials, management?

**Competitive Dynamics:**
- Rational or irrational competition?
- Price wars or value-focused competition?
- New entrants posing threats?
- Technology disruption risk?

**Differentiation:**
- What makes {ticker} different?
- Can competitors easily replicate it?
- Sustainable advantages?

## **7. Risk Analysis** (3-4 paragraphs)

What keeps you up at night about this investment?

**Top 5 Risks** (be specific):
1. [Risk 1 with detailed explanation]
2. [Risk 2 with detailed explanation]
3. [Risk 3 with detailed explanation]
4. [Risk 4 with detailed explanation]
5. [Risk 5 with detailed explanation]

**Risk Evolution:**
- Are these risks increasing or decreasing over time?
- Any new risks mentioned in recent filings?
- How well is management addressing known risks?

**What Could Permanently Impair the Business:**
- Regulatory changes?
- Technology disruption?
- Competitive dynamics shift?
- Management succession issues?
- Cyclical exposure?

**Overall Risk Assessment:**
- Risk level: Low / Moderate / High
- Most concerning risk and why
- Are you comfortable with this risk profile?

## **8. Multi-Year Synthesis** (4-5 paragraphs)

Now synthesize what you learned from analyzing {total_years} years:

**Trend Analysis:**
Across the {total_years} years you studied, what patterns emerged?
- Revenue growth: Accelerating, stable, or declining?
- Margins: Expanding, stable, or compressing?
- ROIC: Improving, consistent, or deteriorating?
- Debt levels: Increasing, stable, or decreasing?
- Cash generation: Stronger or weaker?

**Consistency Assessment:**
- Has business model remained consistent?
- Is competitive advantage strengthening or weakening?
- Track record of management execution?
- Any concerning strategy shifts?

**Business Quality Evolution:**
- Is this a better business today than {total_years} years ago?
- What improved? What deteriorated?
- Trajectory: Upward, flat, or downward?

**The 10-Year Question:**
- Will this business be STRONGER in 10 years?
- Would you be comfortable owning it forever?
- Does management think like an owner?

## **9. Valuation & Margin of Safety** (4-5 paragraphs)

Time to calculate what this business is worth:

**DCF Calculation:**
Use the Calculator Tool with conservative assumptions:
```
Owner Earnings (base): $X.XB (from 2024)
Growth Rate: X% annually (explain why this rate)
Discount Rate: 10% (your standard hurdle)
Terminal Growth: 2.5% (GDP growth)

Calculation result:
Enterprise Value: $X.XB
÷ Shares Outstanding: X.XM
= Intrinsic Value per share: $XXX
```

**Why These Assumptions Are Conservative:**
- Growth rate X% is below historical Y% because [reasons]
- Assumes no margin expansion despite [potential]
- Terminal growth of 2.5% is conservative given [context]
- If wrong, here's what would have to happen: [scenarios]

**Current Market Price:**
- Trading at: $XXX per share
- Implied P/E: XXx
- Implied EV/EBITDA: XXx
- Your IV vs Market Price: Overvalued / Fairly valued / Undervalued by X%

**Margin of Safety Calculation:**
```
Intrinsic Value: $XXX
Current Price: $XXX
Difference: $XXX (±X%)
Margin of Safety: X%

Your Requirements by Business Quality:
- Excellent business (wide moat): Can accept 15-20% margin (high certainty)
- Good business (moderate moat): Need 25-30% margin (moderate certainty)
- Fair/Average business: Need 40%+ margin (low certainty, higher risk)

Rationale: Wider moats = more predictable = lower margin needed.
          Narrow moats = less predictable = higher margin needed.

Current margin: X%
Status: Sufficient / Insufficient / Marginal
```

**Valuation Context:**
- How does this compare to historical valuations?
- What's the market pricing in (growth/decline)?
- Opportunity or value trap?

## **10. Final Investment Decision** (5-6 paragraphs)

After all this analysis, here's your investment decision:

**The Complete Investment Case:**

Synthesize everything into your decision. This should be several paragraphs in
your authentic Warren Buffett voice explaining:

**Summary of Key Findings:**
- Business quality: [1-2 sentences]
- Moat strength: [1-2 sentences]
- Management: [1-2 sentences]
- Financial strength: [1-2 sentences]
- Valuation: [1-2 sentences]

**Why This Decision Makes Sense:**

If **BUY**:
- What makes this compelling right now?
- Why is Mr. Market offering this discount?
- What price would you pay up to before stopping?
- How much conviction do you have and why?
- What would make you sell if you owned it?

If **WATCH**:
- Why is this a quality business worth monitoring?
- At what specific price would it become a BUY?
- What would you like to see improve?
- How will you monitor this going forward?
- What catalyst could create buying opportunity?

If **AVOID**:
- What are the specific dealbreakers?
- Is it the business quality, price, or both?
- At what price (if any) would you reconsider?
- What's fundamentally missing?
- Better opportunities elsewhere?

**Price Targets:**
```
Current Market Price: $XXX
Your Intrinsic Value: $XXX
Buy Price (with margin): $XXX
Sell Price (if owned): $XXX
```

**Final Conviction Statement:**

Include your structured decision clearly:

**DECISION: [BUY / WATCH / AVOID]**
**CONVICTION: [HIGH / MODERATE / LOW]**
**INTRINSIC VALUE: $XXX**
**CURRENT PRICE: $XXX**
**MARGIN OF SAFETY: ±XX%**

End with one of your signature Warren Buffett quotes and a final thought about
patience, discipline, or long-term thinking that's specifically relevant to this
investment decision.

---

**CRITICAL REQUIREMENTS:**

1. **Include ALL 10 sections above** - DO NOT skip any section
2. **Use specific numbers and examples** from the filings you read
3. **Write in Warren Buffett's authentic voice** throughout (folksy, clear, humble)
4. **Make it comprehensive** - target 3,000-5,000 words total
5. **Show your work** - explain reasoning, don't just state conclusions
6. **Use tables and formatting** where helpful for readability
7. **Be honest** about limitations and uncertainties
8. **Connect multi-year insights** - reference trends you observed
9. **Use proper section headers** exactly as shown (## **1. Business Overview**, etc.)
10. **End with structured decision** with all required fields

This thesis should be so complete that an investor could read ONLY this document
and fully understand the entire investment case without needing any other analysis.

Remember your principle: "It's far better to buy a wonderful company at a fair
price than a fair company at a wonderful price."

Now write your complete investment thesis with all 10 sections.
"""

        return synthesis_prompt

    def _synthesize_multi_year_analysis(
        self,
        ticker: str,
        current_year: Dict[str, Any],
        prior_years: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 3: Synthesize findings from current year + prior year summaries.

        This is where Warren Buffett's real insight emerges:
        - Identifying trends (improving vs declining)
        - Assessing consistency (ROIC stable over time?)
        - Evaluating management track record
        - Understanding moat durability

        Args:
            ticker: Stock ticker
            current_year: Full analysis of current year
            prior_years: List of prior year summaries

        Returns:
            Final investment thesis with BUY/WATCH/AVOID decision
        """
        logger.info(f"Synthesizing multi-year analysis for {ticker}")

        # Build complete thesis prompt with explicit 10-section structure
        synthesis_prompt = self._get_complete_thesis_prompt(ticker, current_year, prior_years)

        # Run final synthesis
        result = self._run_analysis_loop(ticker, synthesis_prompt)

        # Parse decision from result
        decision_data = self._parse_decision(ticker, result.get('thesis', ''))

        # Build complete result
        final_result = {
            'ticker': ticker,
            'decision': decision_data['decision'],
            'conviction': decision_data['conviction'],
            'thesis': result.get('thesis', ''),
            'intrinsic_value': decision_data.get('intrinsic_value'),
            'current_price': decision_data.get('current_price'),
            'margin_of_safety': decision_data.get('margin_of_safety'),

            # Multi-year context
            'analysis_summary': {
                'years_analyzed': [current_year.get('year')] + [p['year'] for p in prior_years],
                'current_year_calls': current_year.get('tool_calls_made', 0),
                'total_tool_calls': (
                    current_year.get('tool_calls_made', 0) +
                    result.get('metadata', {}).get('tool_calls_made', 0)
                )
            },

            # Metadata
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'tool_calls_made': (
                    current_year.get('tool_calls_made', 0) +
                    result.get('metadata', {}).get('tool_calls_made', 0)
                ),
                'analysis_type': 'deep_dive_multi_year'
            }
        }

        logger.info(f"Synthesis complete: {final_result['decision']} with {final_result['conviction']} conviction")

        return final_result

    # ========================================================================
    # HELPER METHODS FOR PROGRESS REPORTING
    # ========================================================================

    def _report_progress(self, stage: str, progress: float, message: str):
        """
        Report progress to callback if provided.

        Args:
            stage: Current stage (e.g., "current_year", "prior_years", "synthesis")
            progress: Progress as float 0.0-1.0 (0-100%)
            message: Human-readable status message
        """
        if self._progress_callback:
            try:
                self._progress_callback({
                    "stage": stage,
                    "progress": progress,
                    "message": message
                })
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    # ========================================================================
    # HELPER METHODS FOR CONTEXT MANAGEMENT
    # ========================================================================

    def _estimate_message_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate total tokens in message history.

        Uses rough heuristic: 1 token ≈ 4 characters
        This is conservative for safety.

        Args:
            messages: List of message dicts with role and content

        Returns:
            Estimated token count
        """
        total_chars = 0

        for msg in messages:
            content = msg.get("content", "")

            # Handle different content formats
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        # Tool result
                        if "content" in block:
                            total_chars += len(str(block["content"]))
                    else:
                        # Content block from API response
                        if hasattr(block, "text"):
                            total_chars += len(block.text)
                        elif hasattr(block, "thinking"):
                            total_chars += len(block.thinking)
                        elif hasattr(block, "input"):
                            total_chars += len(str(block.input))

        # Convert to tokens (1 token ≈ 4 chars, conservative)
        return total_chars // 4

    def _prune_old_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prune old messages to keep context under threshold.

        Strategy:
        1. Always keep initial user prompt (messages[0])
        2. Keep only recent N message pairs (user + assistant)
        3. NO summary message (to preserve Extended Thinking format)
        4. Ensure first assistant message starts with thinking block (Extended Thinking requirement)

        IMPORTANT: When Extended Thinking is enabled, we cannot insert arbitrary
        user messages as they break the thinking block requirements. We only keep
        initial prompt + most recent exchanges.

        Additionally, Claude requires that when Extended Thinking is enabled, ALL
        assistant messages must start with a thinking block. After pruning, we
        verify this requirement is met.

        Args:
            messages: Current message history

        Returns:
            Pruned message list
        """
        if len(messages) <= self.MIN_RECENT_MESSAGES + 1:
            # Not enough messages to prune
            return messages

        logger.warning(
            f"Context approaching limit. Pruning old messages to keep "
            f"last {self.MIN_RECENT_MESSAGES // 2} exchanges."
        )

        # Keep initial prompt
        initial_prompt = messages[0]

        # CRITICAL: Extended Thinking requires ALL assistant messages start with thinking block
        # Strategy: Search backwards through message history to find the most recent assistant
        # message that starts with a thinking block, then keep everything from there forward

        logger.info("Searching backwards for assistant message with thinking block...")

        # Search from most recent to oldest (excluding initial prompt)
        valid_start_idx = None
        for idx in range(len(messages) - 1, 0, -1):  # Start from end, go to 1 (skip initial prompt)
            msg = messages[idx]

            if msg.get("role") != "assistant":
                continue

            # Check if this assistant message starts with thinking
            content = msg.get("content", [])
            has_thinking_first = False

            if isinstance(content, list) and len(content) > 0:
                first_block = content[0]
                if isinstance(first_block, dict):
                    has_thinking_first = first_block.get("type") in ["thinking", "redacted_thinking"]
                elif hasattr(first_block, "type"):
                    has_thinking_first = first_block.type in ["thinking", "redacted_thinking"]

            if has_thinking_first:
                # Found it! This is our starting point
                valid_start_idx = idx
                logger.info(f"✓ Found assistant with thinking at index {idx} (Extended Thinking OK)")
                break

        if valid_start_idx is None:
            # No assistant messages with thinking found - this shouldn't happen but handle it
            logger.error("No assistant messages with thinking blocks found! Keeping recent messages anyway...")
            recent_messages = messages[-(self.MIN_RECENT_MESSAGES):]
        else:
            # Keep from the valid start point forward
            recent_messages = messages[valid_start_idx:]

            # If still too many messages, we need to find a MORE RECENT assistant with thinking
            # that fits within MIN_RECENT_MESSAGES, otherwise we'll cut off the thinking block
            if len(recent_messages) > self.MIN_RECENT_MESSAGES:
                logger.warning(
                    f"Still have {len(recent_messages)} messages after finding thinking block. "
                    f"Searching for more recent assistant with thinking..."
                )

                # Search backwards within recent_messages for the most recent assistant with thinking
                # that would fit within MIN_RECENT_MESSAGES
                found_closer = False
                for i in range(len(recent_messages) - 1, 0, -1):
                    msg = recent_messages[i]

                    if msg.get("role") != "assistant":
                        continue

                    # Check if this assistant has thinking
                    content = msg.get("content", [])
                    has_thinking = False

                    if isinstance(content, list) and len(content) > 0:
                        first_block = content[0]
                        if isinstance(first_block, dict):
                            has_thinking = first_block.get("type") in ["thinking", "redacted_thinking"]
                        elif hasattr(first_block, "type"):
                            has_thinking = first_block.type in ["thinking", "redacted_thinking"]

                    if has_thinking:
                        # Check if keeping from here forward would fit
                        remaining_from_here = len(recent_messages) - i
                        if remaining_from_here <= self.MIN_RECENT_MESSAGES:
                            # This works! Use this as the new start
                            recent_messages = recent_messages[i:]
                            logger.info(
                                f"✓ Found closer assistant with thinking. "
                                f"Keeping {len(recent_messages)} messages (Extended Thinking OK)"
                            )
                            found_closer = True
                            break

                # If we couldn't find a closer one that fits, we MUST keep the original thinking assistant
                # to satisfy Extended Thinking requirements, even if it exceeds MIN_RECENT_MESSAGES
                if not found_closer:
                    logger.warning(
                        f"No closer assistant with thinking found within limit. "
                        f"Keeping all {len(recent_messages)} messages from thinking assistant forward "
                        f"(Extended Thinking requirement)."
                    )
                    # Keep all messages from the thinking assistant forward
                    # This is necessary because Extended Thinking is a hard requirement


        # Calculate pruned count for logging
        pruned_count = len(messages) - len(recent_messages) - 1

        # Combine: initial + recent (NO summary message to preserve thinking format)
        pruned_messages = [initial_prompt] + recent_messages

        logger.info(
            f"Pruned {pruned_count} messages. "
            f"Kept {len(pruned_messages)} messages "
            f"(~{self._estimate_message_tokens(pruned_messages)} tokens)"
        )

        return pruned_messages

    def _extract_summary_from_response(self, response_text: str, year: int, ticker: str = None) -> str:
        """
        Extract the summary section from agent's response.

        Handles both formats:
        - Current year: ===== AAPL CURRENT YEAR (2024) ANALYSIS SUMMARY =====
        - Prior years: === 2023 ANNUAL REPORT SUMMARY ===

        Args:
            response_text: Full agent response
            year: Year to extract
            ticker: Stock ticker (optional, for current year format)

        Returns:
            Extracted summary text
        """
        import re

        # Try current year format first (if ticker provided and year is 2024+)
        if ticker and year >= 2024:
            # Format: ===== AAPL CURRENT YEAR (2024) ANALYSIS SUMMARY =====
            pattern = rf"=+\s*{re.escape(ticker.upper())}\s+CURRENT\s+YEAR\s+\({year}\)\s+ANALYSIS\s+SUMMARY\s*=+\s*(.*?)(?:=+\s*END\s+CURRENT\s+YEAR\s+SUMMARY\s*=+|\Z)"
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

            if match:
                summary = match.group(1).strip()
                logger.info(f"Extracted current year summary for {ticker} ({year}): {len(summary)} characters")
                return summary

            # Try alternative ending marker
            pattern = rf"=+\s*{re.escape(ticker.upper())}\s+CURRENT\s+YEAR\s+\({year}\)\s+ANALYSIS\s+SUMMARY\s*=+\s*(.*?)(?:=+\s*END|$)"
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

            if match:
                summary = match.group(1).strip()
                logger.info(f"Extracted current year summary (alt format) for {ticker} ({year}): {len(summary)} characters")
                return summary

        # Try prior year format
        # Format: === 2023 ANNUAL REPORT SUMMARY ===
        pattern = rf"=+\s*{year}\s+ANNUAL\s+REPORT\s+SUMMARY\s*=+\s*(.*?)(?:=+\s*END\s+{year}\s+SUMMARY\s*=+|\Z)"
        match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

        if match:
            summary = match.group(1).strip()
            logger.info(f"Extracted prior year summary for {year}: {len(summary)} characters")
            return summary

        # Try alternative prior year ending
        pattern = rf"=+\s*{year}\s+ANNUAL\s+REPORT\s+SUMMARY\s*=+\s*(.*?)(?:=+\s*END|$)"
        match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

        if match:
            summary = match.group(1).strip()
            logger.info(f"Extracted prior year summary (alt format) for {year}: {len(summary)} characters")
            return summary

        # Fallback: return full response
        logger.warning(
            f"Could not find summary markers for {ticker or ''} {year}, "
            f"using full response ({len(response_text)} characters)"
        )
        return response_text

    def _extract_metrics_from_summary(self, summary: str) -> Dict[str, Any]:
        """
        Extract key financial metrics from summary text.

        Uses regex to find metrics like:
        - Revenue: $123.4B
        - ROIC: 25.3%
        - Debt/Equity: 1.2

        Args:
            summary: Summary text

        Returns:
            dict of extracted metrics
        """
        import re

        metrics = {}

        # Revenue
        revenue_match = re.search(r'Revenue:\s*\$?(\d+\.?\d*)\s*([BM])', summary, re.IGNORECASE)
        if revenue_match:
            value = float(revenue_match.group(1))
            unit = revenue_match.group(2)
            metrics['revenue_billions'] = value if unit == 'B' else value / 1000

        # ROIC
        roic_match = re.search(r'ROIC:\s*(\d+\.?\d*)%', summary, re.IGNORECASE)
        if roic_match:
            metrics['roic_percent'] = float(roic_match.group(1))

        # Margin
        margin_match = re.search(r'(?:Operating\s+)?Margin:\s*(\d+\.?\d*)%', summary, re.IGNORECASE)
        if margin_match:
            metrics['margin_percent'] = float(margin_match.group(1))

        # Debt/Equity
        debt_match = re.search(r'Debt/Equity:\s*(\d+\.?\d*)', summary, re.IGNORECASE)
        if debt_match:
            metrics['debt_equity'] = float(debt_match.group(1))

        return metrics

    # ========================================================================
    # REACT LOOP (Smart Provider Detection)
    # ========================================================================

    def _run_analysis_loop(
        self,
        ticker: str,
        initial_message: str
    ) -> Dict[str, Any]:
        """
        Smart ReAct loop that automatically chooses the best implementation.

        - For Claude: Uses native Extended Thinking + Tool Use
        - For other providers: Uses Universal ReAct with JSON tool calling

        This architecture allows future LLM providers (GPT-5, Gemini) to be added
        easily with full tool use capability.

        Args:
            ticker: Stock ticker
            initial_message: Initial prompt to agent

        Returns:
            dict: Analysis results with decision and thesis
        """
        # Check which provider is being used
        provider_info = self.llm.get_provider_info()
        provider_name = provider_info['provider']

        logger.info(f"Using provider: {provider_name}")
        logger.info(f"Model: {provider_info['model_id']}")

        # For Claude: Use native Extended Thinking + Tool Use
        if provider_name == 'Claude' and self.client is not None:
            logger.info("Using Claude-native ReAct loop (Extended Thinking + Tool Use)")
            return self._run_react_loop(ticker, initial_message)

        # For all other providers: Use Universal ReAct Loop
        logger.info(f"Using Universal ReAct loop with JSON tool calling")
        logger.info("This enables future LLM providers to use tools just like Claude!")

        # Create universal ReAct loop
        react_loop = UniversalReActLoop(
            llm_client=self.llm,
            tools=self.tools,
            max_iterations=self.MAX_ITERATIONS
        )

        # Run analysis
        result = react_loop.run(
            initial_prompt=initial_message,
            system_prompt=self.system_prompt
        )

        if result["success"]:
            # Extract analysis content
            content = result["content"]

            # Parse decision from content
            decision = self._parse_decision(ticker, content)
            decision_value = decision.get("decision", "UNKNOWN")

            logger.info(f"Analysis Complete - Decision: {decision_value}")

            return {
                "decision": decision_value,
                "thesis": content,
                "metadata": result["metadata"]
            }
        else:
            logger.error(f"Analysis failed: {result.get('error')}")
            return {
                "decision": "UNKNOWN",
                "thesis": result.get("content", "Analysis incomplete"),
                "metadata": result.get("metadata", {})
            }

    # ========================================================================
    # REACT LOOP (Claude Native - Original Implementation)
    # ========================================================================

    def _run_react_loop(
        self,
        ticker: str,
        initial_message: str
    ) -> Dict[str, Any]:
        """
        Run the ReAct (Reasoning + Acting) loop with Extended Thinking.

        This is the core of the agent's autonomous investigation:
        1. Agent thinks about what information it needs (Reasoning)
        2. Agent uses tools to gather that information (Acting)
        3. Agent reflects on findings and decides next steps
        4. Repeats until confident in investment decision

        Args:
            ticker: Stock ticker
            initial_message: Initial prompt to agent

        Returns:
            dict: Analysis results with decision and thesis
        """
        messages = [{"role": "user", "content": initial_message}]
        tool_calls_made = 0
        iteration = 0

        logger.info(f"Starting ReAct loop (max {self.MAX_ITERATIONS} iterations)")

        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")

            try:
                # Call Claude with extended thinking
                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=self.MAX_TOKENS,
                    system=self.system_prompt,
                    messages=messages,
                    tools=self._get_tool_definitions(),
                    thinking={
                        "type": "enabled",
                        "budget_tokens": self.THINKING_BUDGET
                    }
                )

                # Track token usage for cost calculation
                if not hasattr(self, '_total_input_tokens'):
                    self._total_input_tokens = 0
                    self._total_output_tokens = 0

                self._total_input_tokens += response.usage.input_tokens
                self._total_output_tokens += response.usage.output_tokens

                # Process response blocks
                assistant_content = []
                tool_uses = []

                for block in response.content:
                    if block.type == "thinking":
                        # Extended thinking - agent reasoning internally
                        logger.debug(f"[Thinking] {len(block.thinking)} characters")
                        assistant_content.append(block)

                    elif block.type == "text":
                        # Agent's text output
                        logger.info(f"[Agent] {block.text[:200]}...")
                        assistant_content.append(block)

                    elif block.type == "tool_use":
                        # Agent wants to use a tool
                        tool_uses.append(block)
                        assistant_content.append(block)
                        logger.info(f"[Tool Use] {block.name} with id {block.id}")

                # Add assistant's response to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })

                # If agent used tools, execute them
                if tool_uses:
                    tool_results = []

                    for tool_use in tool_uses:
                        tool_calls_made += 1
                        result = self._execute_tool(
                            tool_use.name,
                            tool_use.input
                        )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(result)
                        })

                    # Add tool results to conversation
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                    # Check context size and prune if approaching limit
                    estimated_tokens = self._estimate_message_tokens(messages)
                    logger.debug(f"Current context: ~{estimated_tokens} tokens")

                    if estimated_tokens > self.CONTEXT_PRUNE_THRESHOLD:
                        logger.warning(
                            f"Context size ({estimated_tokens} tokens) exceeds threshold "
                            f"({self.CONTEXT_PRUNE_THRESHOLD} tokens). Pruning old messages..."
                        )
                        messages = self._prune_old_messages(messages)
                        estimated_tokens = self._estimate_message_tokens(messages)
                        logger.info(f"After pruning: ~{estimated_tokens} tokens")

                    # Continue loop (agent will process results)
                    continue

                # No tool use - agent has finished
                # Extract final thesis from text blocks
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text + "\n\n"

                logger.info(f"Agent finished after {tool_calls_made} tool calls")

                # Parse decision from final text
                decision_data = self._parse_decision(ticker, final_text)

                # Calculate costs
                input_cost = (self._total_input_tokens / 1000) * 0.01
                output_cost = (self._total_output_tokens / 1000) * 0.30
                total_cost = input_cost + output_cost

                decision_data["metadata"] = {
                    "analysis_date": datetime.now().isoformat(),
                    "tool_calls_made": tool_calls_made,
                    "token_usage": {
                        "input_tokens": self._total_input_tokens,
                        "output_tokens": self._total_output_tokens,
                        "input_cost": round(input_cost, 2),
                        "output_cost": round(output_cost, 2),
                        "total_cost": round(total_cost, 2)
                    }
                }

                return decision_data

            except anthropic.RateLimitError as e:
                logger.warning(f"Rate limit hit: {e}")
                # In production, you'd want to implement backoff/retry
                raise

            except anthropic.BadRequestError as e:
                # Handle "prompt is too long" errors
                error_msg = str(e)
                if "prompt is too long" in error_msg.lower() or "too many tokens" in error_msg.lower():
                    logger.error(f"Context window exceeded: {error_msg}")
                    logger.error(f"Current message count: {len(messages)}")
                    estimated_tokens = self._estimate_message_tokens(messages)
                    logger.error(f"Estimated tokens: {estimated_tokens}")

                    # Try aggressive pruning as last resort
                    # Keep only initial + last 2 messages (1 exchange minimum)
                    if len(messages) > 3:
                        logger.warning("Attempting aggressive context pruning (keeping only 1 exchange)...")
                        initial_prompt = messages[0]
                        last_two = messages[-2:]  # Last user + assistant exchange
                        messages = [initial_prompt] + last_two
                        logger.info(f"After aggressive pruning: {len(messages)} messages, ~{self._estimate_message_tokens(messages)} tokens")
                        # Retry this iteration
                        continue
                    else:
                        logger.error("Cannot prune further. Analysis too complex for available context window.")
                        raise
                else:
                    logger.error(f"Bad request error: {e}")
                    raise

            except anthropic.APIError as e:
                logger.error(f"Anthropic API error: {e}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error in ReAct loop: {e}", exc_info=True)
                raise

        # Max iterations reached
        logger.warning(f"Max iterations ({self.MAX_ITERATIONS}) reached")
        return {
            "ticker": ticker,
            "decision": "ERROR",
            "conviction": "NONE",
            "thesis": "Analysis did not complete within reasonable time (max iterations reached).",
            "intrinsic_value": None,
            "current_price": None,
            "margin_of_safety": None,
            "analysis_summary": {},
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "tool_calls_made": tool_calls_made,
                "error": "Max iterations reached"
            }
        }

    def _execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of tool to execute
            tool_input: Parameters for tool

        Returns:
            dict: Tool execution result
        """
        # Map tool names to tool instances
        tool_map = {
            "gurufocus_tool": "gurufocus",
            "sec_filing_tool": "sec_filing",
            "web_search_tool": "web_search",
            "calculator_tool": "calculator"
        }

        tool_key = tool_map.get(tool_name)
        if not tool_key:
            logger.error(f"Unknown tool: {tool_name}")
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "data": None
            }

        tool = self.tools[tool_key]

        logger.info(f"Executing {tool_name}")
        logger.debug(f"Parameters: {tool_input}")

        try:
            result = tool.execute(**tool_input)
            logger.info(f"{tool_name} {'succeeded' if result.get('success') else 'failed'}")

            if not result.get("success"):
                logger.warning(f"Tool error: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Tool execution exception: {str(e)}",
                "data": None
            }

    def _parse_decision(
        self,
        ticker: str,
        final_text: str
    ) -> Dict[str, Any]:
        """
        Parse investment decision from agent's final response.

        Extracts:
        - Decision: BUY/WATCH/AVOID
        - Conviction: HIGH/MODERATE/LOW
        - Intrinsic value estimate
        - Current price
        - Margin of safety
        - Full thesis text

        Args:
            ticker: Stock ticker
            final_text: Agent's final output text

        Returns:
            dict: Parsed decision data
        """
        decision_data = {
            "ticker": ticker,
            "decision": "UNKNOWN",
            "conviction": "UNKNOWN",
            "thesis": final_text,
            "intrinsic_value": None,
            "current_price": None,
            "margin_of_safety": None,
            "analysis_summary": self._extract_analysis_summary(final_text)
        }

        # Extract decision (BUY, WATCH, AVOID)
        decision_patterns = [
            r'\*\*DECISION:\s*(BUY|WATCH|AVOID)\*\*',  # Bold markdown format
            r'\b(DECISION|RECOMMENDATION|VERDICT)\s*:\s*(BUY|WATCH|AVOID)\b',
            r'\b(STRONG BUY|BUY RECOMMENDATION)\b',
            r'\b(WATCHING|WATCH LIST|WAIT FOR BETTER PRICE)\b',
            r'\b(AVOIDING|PASS ON THIS|TAKING A PASS)\b',
            r"I'm\s+(backing up the truck|buying|investing)",
            r"I'm\s+(passing|avoiding|taking a pass)",
            r"I'm\s+(watching|waiting for a better price)",
        ]

        for pattern in decision_patterns:
            match = re.search(pattern, final_text, re.IGNORECASE)
            if match:
                matched_text = match.group(0).upper()
                if any(word in matched_text for word in ["BUY", "BACKING", "INVESTING"]):
                    decision_data["decision"] = "BUY"
                    break
                elif any(word in matched_text for word in ["WATCH", "WAIT", "WAITING"]):
                    decision_data["decision"] = "WATCH"
                    break
                elif any(word in matched_text for word in ["AVOID", "PASS"]):
                    decision_data["decision"] = "AVOID"
                    break

        # Extract conviction (HIGH, MODERATE, LOW)
        conviction_patterns = [
            r'\*\*CONVICTION:\s*(HIGH|MODERATE|LOW)\*\*',  # Bold markdown format
            r'\b(CONVICTION|CONFIDENCE)\s*:\s*(HIGH|MODERATE|LOW)\b',
            r'\b(HIGH|STRONG|EXCEPTIONAL)\s+(CONVICTION|CONFIDENCE)\b',
            r'\b(MODERATE|REASONABLE|GOOD)\s+(CONVICTION|CONFIDENCE)\b',
            r'\b(LOW|WEAK|LIMITED)\s+(CONVICTION|CONFIDENCE)\b',
        ]

        for pattern in conviction_patterns:
            match = re.search(pattern, final_text, re.IGNORECASE)
            if match:
                matched_text = match.group(0).upper()
                if any(word in matched_text for word in ["HIGH", "STRONG", "EXCEPTIONAL"]):
                    decision_data["conviction"] = "HIGH"
                    break
                elif any(word in matched_text for word in ["MODERATE", "REASONABLE", "GOOD"]):
                    decision_data["conviction"] = "MODERATE"
                    break
                elif any(word in matched_text for word in ["LOW", "WEAK", "LIMITED"]):
                    decision_data["conviction"] = "LOW"
                    break

        # Extract numerical values
        decision_data.update(self._extract_numerical_values(final_text))

        return decision_data

    def _extract_analysis_summary(self, text: str) -> Dict[str, str]:
        """
        Extract analysis summary sections from thesis text.

        Args:
            text: Full thesis text

        Returns:
            dict: Summary of each analysis dimension
        """
        summary = {
            "circle_of_competence": "",
            "economic_moat": "",
            "management_quality": "",
            "financial_strength": "",
            "valuation": "",
            "risks": ""
        }

        # Try to extract each section based on keywords
        sections = {
            "circle_of_competence": [
                r"(?:circle of competence|business understanding|business model)(?:.*?)(?=\n\n|\Z)",
                r"(?:I understand this business|I don't understand)(?:.*?)(?=\n\n|\Z)"
            ],
            "economic_moat": [
                r"(?:economic moat|competitive advantage|moat assessment)(?:.*?)(?=\n\n|\Z)",
                r"(?:brand power|network effects|switching costs)(?:.*?)(?=\n\n|\Z)"
            ],
            "management_quality": [
                r"(?:management quality|management team|CEO)(?:.*?)(?=\n\n|\Z)",
                r"(?:capital allocation|insider ownership)(?:.*?)(?=\n\n|\Z)"
            ],
            "financial_strength": [
                r"(?:financial strength|owner earnings|ROIC)(?:.*?)(?=\n\n|\Z)",
                r"(?:debt levels|cash flow|balance sheet)(?:.*?)(?=\n\n|\Z)"
            ],
            "valuation": [
                r"(?:valuation|intrinsic value|margin of safety)(?:.*?)(?=\n\n|\Z)",
                r"(?:DCF|discounted cash flow|fair value)(?:.*?)(?=\n\n|\Z)"
            ],
            "risks": [
                r"(?:risks|risk factors|concerns)(?:.*?)(?=\n\n|\Z)",
                r"(?:could permanently impair|biggest risk)(?:.*?)(?=\n\n|\Z)"
            ]
        }

        for key, patterns in sections.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    summary[key] = match.group(0)[:500].strip()  # First 500 chars
                    break

        return summary

    def _extract_numerical_values(self, text: str) -> Dict[str, Optional[float]]:
        """
        Extract numerical values (intrinsic value, price, margin of safety) from text.

        Args:
            text: Text to parse

        Returns:
            dict: Extracted numerical values
        """
        values = {
            "intrinsic_value": None,
            "current_price": None,
            "margin_of_safety": None
        }

        # Intrinsic value patterns
        iv_patterns = [
            r'\*\*INTRINSIC\s+VALUE:\s*\$?\s*([\d,]+\.?\d*)\*\*',  # Bold markdown
            r'intrinsic\s+value.*?\$?\s*([\d,]+\.?\d*)\s*(?:per\s+share)?',
            r'fair\s+value.*?\$?\s*([\d,]+\.?\d*)',
            r'worth.*?\$?\s*([\d,]+\.?\d*)\s*(?:per\s+share)?'
        ]

        for pattern in iv_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    values["intrinsic_value"] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue

        # Current price patterns
        price_patterns = [
            r'\*\*CURRENT\s+PRICE:\s*\$?\s*([\d,]+\.?\d*)\*\*',  # Bold markdown
            r'current\s+price.*?\$?\s*([\d,]+\.?\d*)',
            r'trading\s+at.*?\$?\s*([\d,]+\.?\d*)',
            r'stock\s+price.*?\$?\s*([\d,]+\.?\d*)'
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    values["current_price"] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue

        # Margin of safety patterns
        mos_patterns = [
            r'\*\*MARGIN\s+OF\s+SAFETY:\s*([\d]+\.?\d*)%\*\*',  # Bold markdown
            r'margin\s+of\s+safety.*?([\d]+\.?\d*)%',
            r'margin\s+of\s+safety.*?(\d+)%',
            r'discount.*?([\d]+)%'
        ]

        for pattern in mos_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    values["margin_of_safety"] = float(match.group(1)) / 100.0
                    break
                except ValueError:
                    continue

        return values

    def batch_analyze(
        self,
        tickers: List[str],
        deep_dive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple companies in batch.

        Useful for screening a watchlist or comparing multiple companies.

        Args:
            tickers: List of stock ticker symbols
            deep_dive: If True, performs deep analysis on each
                      If False, quick screen only

        Returns:
            List of analysis results (one per ticker)
        """
        results = []

        logger.info(f"Starting batch analysis of {len(tickers)} companies")

        for i, ticker in enumerate(tickers, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Batch Analysis {i}/{len(tickers)}: {ticker}")
            logger.info(f"{'='*80}")

            try:
                result = self.analyze_company(ticker, deep_dive=deep_dive)
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to analyze {ticker}: {e}")
                results.append({
                    "ticker": ticker,
                    "decision": "ERROR",
                    "conviction": "NONE",
                    "thesis": f"Analysis failed: {str(e)}",
                    "error": str(e)
                })

        logger.info(f"\nBatch analysis complete: {len(results)} results")

        # Summary
        decisions = {}
        for result in results:
            decision = result.get("decision", "UNKNOWN")
            decisions[decision] = decisions.get(decision, 0) + 1

        logger.info(f"Decisions: {decisions}")

        return results

    def compare_companies(
        self,
        tickers: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple companies side-by-side.

        Useful for evaluating competitors or choosing between alternatives.

        Args:
            tickers: List of stock tickers to compare (2-5 recommended)

        Returns:
            {
                "companies": List[Dict],  # Individual analyses
                "comparison": str,  # Comparative analysis in Buffett's voice
                "recommendation": str  # Which company (if any) to invest in
            }
        """
        logger.info(f"Starting comparative analysis of {tickers}")

        # Analyze each company
        analyses = self.batch_analyze(tickers, deep_dive=True)

        # Generate comparison prompt
        comparison_prompt = f"""I've analyzed these companies:

{self._format_analyses_for_comparison(analyses)}

Now, as Warren Buffett, please compare these companies and tell me:

1. Which has the widest moat?
2. Which has the best management?
3. Which has the best financial strength?
4. Which offers the best value (margin of safety)?
5. If you could only invest in one, which would it be and why?

Be specific and use your folksy style. It's okay to say "none of these"
if none meet your standards.
"""

        # Get comparative analysis from agent
        messages = [{"role": "user", "content": comparison_prompt}]

        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                system=self.system_prompt,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 5000
                }
            )

            # Extract comparison text
            comparison_text = ""
            for block in response.content:
                if block.type == "text":
                    comparison_text += block.text

            # Extract recommendation
            recommendation = self._extract_comparison_recommendation(comparison_text)

            return {
                "companies": analyses,
                "comparison": comparison_text,
                "recommendation": recommendation,
                "metadata": {
                    "comparison_date": datetime.now().isoformat(),
                    "companies_compared": len(tickers)
                }
            }

        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {
                "companies": analyses,
                "comparison": f"Comparison failed: {str(e)}",
                "recommendation": "ERROR",
                "error": str(e)
            }

    def _format_analyses_for_comparison(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Format individual analyses for comparison prompt.

        Args:
            analyses: List of analysis results

        Returns:
            str: Formatted summary
        """
        formatted = []

        for analysis in analyses:
            summary = f"""
**{analysis['ticker']}**
Decision: {analysis['decision']}
Conviction: {analysis.get('conviction', 'UNKNOWN')}
Intrinsic Value: ${analysis.get('intrinsic_value', 'N/A')}
Current Price: ${analysis.get('current_price', 'N/A')}
Margin of Safety: {analysis.get('margin_of_safety', 'N/A') * 100 if analysis.get('margin_of_safety') else 'N/A'}%

Key Points:
{analysis.get('thesis', '')[:1000]}
"""
            formatted.append(summary)

        return "\n\n---\n\n".join(formatted)

    def _extract_comparison_recommendation(self, text: str) -> str:
        """
        Extract final recommendation from comparison text.

        Args:
            text: Comparison text

        Returns:
            str: Recommended ticker or "NONE"
        """
        # Look for patterns like "I would invest in AAPL" or "I'd choose Microsoft"
        patterns = [
            r'(?:I would|I\'d)\s+(?:invest in|choose|pick|select)\s+([A-Z]{1,5})',
            r'(?:recommendation|pick)\s*:\s*([A-Z]{1,5})',
            r'(?:best choice|winner)\s+(?:is|:)\s*([A-Z]{1,5})'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        # Look for "none of these"
        if re.search(r'\b(?:none|neither)\b', text, re.IGNORECASE):
            return "NONE"

        return "UNCLEAR"


__all__ = ["WarrenBuffettAgent"]
