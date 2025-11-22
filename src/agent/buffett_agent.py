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
    get_investment_framework_prompt,
    get_tool_descriptions_for_prompt
)
# UniversalReActLoop removed - providers now implement their own ReAct loops
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
    MAX_TOKENS = 32000  # Response limit (increased for 10-year comprehensive thesis generation)
    THINKING_BUDGET = 12000  # Extended thinking budget (must be < MAX_TOKENS)
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

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_key: Optional[str] = None,
        validator_model_key: Optional[str] = None,
        enable_validation: bool = True,
        max_validation_iterations: int = 1,
        score_threshold: int = 80
    ):
        """
        Initialize Investment Analysis Agent (Phase 9).

        Args:
            api_key: Anthropic API key (deprecated, use LLM_MODEL env var)
            model_key: LLM model to use for analysis (defaults to LLM_MODEL env var)
            validator_model_key: LLM model to use for validation (defaults to VALIDATOR_MODEL_KEY env var, or same as model_key)
            enable_validation: Whether to enable Phase 9 single-pass validation (default: True)
            max_validation_iterations: Always 1 for Phase 9 (single-pass only)
            score_threshold: Validation score threshold (fixed at 80 for Phase 9)

        Raises:
            ValueError: If required configuration is missing
        """
        # Initialize analyst LLM client with plug-and-play model selection
        try:
            self.llm = LLMClient(model_key=model_key)
            logger.info(f"Initialized LLM: {self.llm.get_provider_info()}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise ValueError(f"LLM initialization failed: {e}")

        # Initialize validator LLM client (can be different model for cost optimization)
        try:
            # Use validator_model_key if provided, otherwise fall back to VALIDATOR_MODEL_KEY env var, or same as analyst
            validator_key = validator_model_key or os.getenv("VALIDATOR_MODEL_KEY") or model_key
            self.validator_llm = LLMClient(model_key=validator_key)

            if validator_key != model_key:
                logger.info(f"Initialized Validator LLM: {self.validator_llm.get_provider_info()} (separate from analyst)")
            else:
                logger.info(f"Validator using same model as analyst: {self.validator_llm.get_provider_info()}")
        except Exception as e:
            logger.error(f"Failed to initialize validator LLM client: {e}")
            raise ValueError(f"Validator LLM initialization failed: {e}")

        # Backward compatibility: if api_key provided, ensure it's set
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

        # Keep legacy client for anthropic-specific features (like error handling)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None  # Will use LLM abstraction

        # Phase 9: Single-pass validation configuration
        self.enable_validation = enable_validation
        self.max_validation_iterations = 1  # Phase 9: Always single-pass
        self.score_threshold = score_threshold
        logger.info(
            f"Phase 9 Validation: {'ENABLED' if enable_validation else 'DISABLED'} "
            f"(single-pass, Munger mental models framework)"
        )

        # Phase 7.7: Tool caching to avoid redundant API calls
        self.tool_cache = {
            "gurufocus": {},      # GuruFocus API responses
            "sec": {},            # SEC filing texts
            "web_search": {},     # Web search results
            "calculator": {}      # Calculator outputs
        }
        self.cache_hits = 0       # Track cache efficiency
        self.cache_misses = 0     # Track cache efficiency
        logger.info("Phase 7.7 tool caching enabled")

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
        buffett_prompt = get_investment_framework_prompt()
        tool_descriptions = get_tool_descriptions_for_prompt()

        return f"{buffett_prompt}\n\n{tool_descriptions}"

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Convert basīrah tools to provider-native tool format.

        Uses provider-native web search when available:
        - Claude: web_search_20250305 (automatic citations, $10/1K searches)
        - Kimi: $web_search builtin_function (included in token costs)

        Returns:
            List of tool definitions for provider API
        """
        # Get provider info
        provider_info = self.llm.get_provider_info()
        provider = provider_info.get("provider", "").lower()

        tools = []

        # Add standard tools
        tools.append({
            "name": "gurufocus_tool",
            "description": self.tools["gurufocus"].description,
            "input_schema": self.tools["gurufocus"].parameters
        })
        tools.append({
            "name": "sec_filing_tool",
            "description": self.tools["sec_filing"].description,
            "input_schema": self.tools["sec_filing"].parameters
        })
        tools.append({
            "name": "calculator_tool",
            "description": self.tools["calculator"].description,
            "input_schema": self.tools["calculator"].parameters
        })

        # Add provider-native web search
        if provider == "claude":
            # Use Claude native web search (automatic execution + citations)
            tools.append({
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10,  # Limit to prevent runaway costs
                # Filter to investment research domains
                "allowed_domains": [
                    "sec.gov",
                    "investor.com",
                    "nasdaq.com",
                    "reuters.com",
                    "bloomberg.com",
                    "ft.com",
                    "wsj.com",
                    "marketwatch.com"
                ]
            })
            logger.info("Using Claude native web search (web_search_20250305)")

        elif provider == "kimi":
            # Use Kimi official $web_search builtin function
            # Reference: https://platform.moonshot.ai/docs/guide/use-web-search
            tools.append({
                "type": "builtin_function",
                "function": {
                    "name": "$web_search"
                }
            })
            logger.info("Using Kimi official $web_search builtin function")

        else:
            # Unknown provider - add regular web_search_tool
            logger.warning(f"Unknown provider '{provider}' - using standard web_search_tool")
            tools.append({
                "name": "web_search_tool",
                "description": self.tools["web_search"].description,
                "input_schema": self.tools["web_search"].parameters
            })

        return tools

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

            # Phase 7.6C: Validate analysis with auto-correction if enabled
            # NOTE: Validation only for deep dive (quick analysis doesn't need it)
            if self.enable_validation and deep_dive:
                logger.info("\n" + "=" * 80)
                logger.info("  Phase 7.6C: Quality Validation with Auto-Correction")
                logger.info("=" * 80)
                logger.info("  Single-pass validation with cached data corrections (no refinement loop)")

                try:
                    result = self._validate_with_auto_correction(result, ticker)

                    # Phase 9.2: Append Charlie Munger's critique to thesis
                    munger_critique = self._format_munger_critique(result.get("validation", {}))
                    if munger_critique:
                        logger.info("Appending Charlie Munger's critique to thesis...")
                        result["thesis"] = result.get("thesis", "") + munger_critique

                except Exception as e:
                    logger.error(f"Validation failed with error: {e}", exc_info=True)
                    result["validation"] = {
                        "enabled": True,
                        "approved": False,
                        "score": 0,
                        "error": str(e)
                    }

            else:
                # Validation disabled (either globally disabled or quick analysis)
                if not deep_dive and self.enable_validation:
                    logger.info("  Validation skipped for quick analysis (not needed)")
                result["validation"] = {
                    "enabled": False
                }

            # Phase 7.7: Add cache statistics to metadata
            cache_stats = self._get_cache_stats()
            result["metadata"]["cache_stats"] = cache_stats

            logger.info("=" * 80)
            logger.info(f"  Analysis Complete - Decision: {result['decision']}")
            if self.enable_validation and "score" in result.get("validation", {}):
                logger.info(f"  Validation Score: {result['validation']['score']}/100")

            # Phase 7.7: Log cache performance
            logger.info(f"  Tool Cache Performance:")
            logger.info(f"    - Cache Hits: {cache_stats['cache_hits']}")
            logger.info(f"    - Cache Misses: {cache_stats['cache_misses']}")
            logger.info(f"    - Hit Rate: {cache_stats['hit_rate_percent']}%")
            logger.info(f"    - Cached Items: {cache_stats['total_cached_items']}")
            if cache_stats['hit_rate_percent'] > 0:
                logger.info(f"    - Tool calls saved: {cache_stats['cache_hits']} (from total {cache_stats['total_calls']})")

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
        result = self._run_analysis_loop(ticker, initial_message)

        # Set analysis type for validator (Phase 7.6B)
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"]["analysis_type"] = "quick_screen"

        return result

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

        # Phase 7.8: Pre-fetch verified metrics BEFORE analysis begins
        # This solves the decision consistency problem by ensuring the analyst
        # has access to correct quantitative data from the start
        logger.info("\n[PHASE 7.8] Pre-fetching verified metrics for decision consistency...")
        verified_metrics = self._fetch_verified_metrics(ticker)

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

        # Phase 7.7: Warm cache for synthesis to maximize cache hits
        self._warm_cache_for_synthesis(ticker, current_year=self.most_recent_fiscal_year)

        # =====================================================================
        # DEEP DIVE FIX: Removed Tier 1 decision gate
        # =====================================================================
        # Deep Dive ALWAYS executes all 3 stages (current year, prior years, synthesis)
        # The tiered logic (Quick Screen vs Deep Dive) is handled at the routing level:
        #   - Quick Screen (_analyze_quick_screen) = Tier 1 only
        #   - Deep Dive (_analyze_deep_dive_with_context_management) = Full multi-year analysis
        #
        # When user requests deep_dive=True, they get ALL stages regardless of decision

        logger.info("\n" + "=" * 80)
        logger.info("DEEP DIVE: Proceeding to multi-year analysis")
        logger.info("=" * 80)
        logger.info("Deep Dive includes: Current year + Historical MD&A + Proxy + Multi-year synthesis")

        # Stage 2: MD&A History + Proxy (40-80% progress)
        # Deep Dive always executes this stage (unlike Quick Screen which stops after Stage 1)
        # years_to_analyze includes current year, so subtract 1 for prior years
        num_prior_years = max(0, years_to_analyze - 1)
        logger.info(f"\n[STAGE 2] Analyzing {num_prior_years} years of MD&A for management track record...")

        if num_prior_years > 0:
            self._report_progress(
                stage="prior_years",
                progress=0.4,
                message=f"📚 Stage 2: Analyzing {num_prior_years} years of MD&A..."
            )

        prior_years_summaries, missing_years = self._analyze_mda_history(ticker, num_years=num_prior_years, years_to_analyze=years_to_analyze)
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
                progress=0.75,
                message=f"✅ MD&A Analysis Complete: {num_prior_years} years analyzed"
            )

        # =====================================================================
        # STAGE 2 (continued): PROXY STATEMENT ANALYSIS
        # =====================================================================
        # Fetch latest proxy (DEF 14A) for management compensation analysis
        # This is part of Deep Dive's Stage 2 (required by Charlie Munger fix #8)

        logger.info("\n[STAGE 2] Fetching proxy statement (DEF 14A) for management compensation analysis...")

        proxy_analysis = None
        try:
            proxy_result = self.tools["sec_filing"].execute(
                ticker=ticker,
                filing_type="DEF 14A",
                year=self.most_recent_fiscal_year
            )

            if proxy_result.get("success"):
                logger.info(f"✅ Proxy statement retrieved for {ticker}")
                proxy_analysis = {
                    'year': self.most_recent_fiscal_year,
                    'content': proxy_result.get('data', {}).get('content', ''),
                    'filing_type': 'DEF 14A'
                }
            else:
                logger.warning(f"⚠️ Proxy statement not available: {proxy_result.get('error', 'Unknown error')}")
                proxy_analysis = None

        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch proxy statement: {str(e)}")
            proxy_analysis = None

        self._report_progress(
            stage="prior_years",
            progress=0.8,
            message=f"✅ Stage 2 Complete: MD&A history + Proxy analyzed"
        )

        # Phase 7.7.4: Build structured data BEFORE synthesis to pass to synthesis prompt
        logger.info("\n[PHASE 7.7.4] Building structured metrics and insights for synthesis...")

        # Phase 7.7 Phase 2: Build structured metrics from all years
        structured_metrics = {
            "current_year": {
                "year": current_year_analysis.get('year'),
                "metrics": current_year_analysis.get('metrics', {})
            },
            "prior_years": [
                {
                    "year": prior_year.get('year'),
                    "metrics": prior_year.get('metrics', {})
                }
                for prior_year in prior_years_summaries
            ],
            "all_years": []  # Combined list of all years for easy iteration
        }

        # Build combined all_years list (most recent first)
        structured_metrics["all_years"].append({
            "year": current_year_analysis.get('year'),
            "metrics": current_year_analysis.get('metrics', {})
        })
        for prior_year in prior_years_summaries:
            structured_metrics["all_years"].append({
                "year": prior_year.get('year'),
                "metrics": prior_year.get('metrics', {})
            })

        logger.info(f"[PHASE 7.7] Structured metrics extracted for {len(structured_metrics['all_years'])} years")

        # Phase 7.7 Phase 3: Build structured insights from all years
        structured_insights = {
            "current_year": {
                "year": current_year_analysis.get('year'),
                "insights": current_year_analysis.get('insights', {})
            },
            "prior_years": [
                {
                    "year": prior_year.get('year'),
                    "insights": prior_year.get('insights', {})
                }
                for prior_year in prior_years_summaries
            ],
            "all_years": []  # Combined list of all years for easy iteration
        }

        # Build combined all_years list (most recent first)
        structured_insights["all_years"].append({
            "year": current_year_analysis.get('year'),
            "insights": current_year_analysis.get('insights', {})
        })
        for prior_year in prior_years_summaries:
            structured_insights["all_years"].append({
                "year": prior_year.get('year'),
                "insights": prior_year.get('insights', {})
            })

        logger.info(f"[PHASE 7.7] Structured insights extracted for {len(structured_insights['all_years'])} years")

        # Stage 3: Multi-Year Synthesis (80-100% progress)
        logger.info("\n[STAGE 3] Synthesizing multi-year findings...")
        self._report_progress(
            stage="synthesis",
            progress=0.8,
            message=f"🧠 Stage 3: Synthesizing {years_to_analyze}-year analysis..."
        )

        # Phase 7.7.4: Pass structured data to synthesis for optimization
        # Phase 7.8: Pass verified metrics for decision consistency
        final_thesis = self._synthesize_multi_year_analysis(
            ticker=ticker,
            current_year=current_year_analysis,
            prior_years=prior_years_summaries,
            structured_metrics=structured_metrics,
            structured_insights=structured_insights,
            verified_metrics=verified_metrics
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

        years_analyzed_list = [current_year_analysis.get('year')] + [p['year'] for p in prior_years_summaries]

        final_thesis["metadata"]["context_management"] = {
            "strategy": current_year_strategy,  # 'standard' or 'adaptive_summarization'
            "current_year_tokens": current_year_analysis.get('token_estimate', 0),
            "prior_years_tokens": total_prior_tokens,
            "total_token_estimate": total_token_estimate,
            "years_analyzed": years_analyzed_list,
            "years_requested": years_to_analyze,
            "years_skipped": missing_years if missing_years else None,  # List of years with no 10-K available
            "years_skipped_count": len(missing_years),

            # Additional fields for adaptive strategy
            "adaptive_used": adaptive_used,
            "filing_size": current_year_analysis.get('filing_size'),
            "summary_size": current_year_analysis.get('summary_size'),
            "reduction_percent": current_year_analysis.get('reduction_percent')
        }

        # Add years_analyzed count at top level for database storage
        final_thesis["metadata"]["years_analyzed"] = len(years_analyzed_list)

        # Phase 7.7.4: Add structured data to metadata (already built above)
        final_thesis["metadata"]["structured_metrics"] = structured_metrics
        final_thesis["metadata"]["structured_insights"] = structured_insights

        logger.info(f"\nTotal estimated context: ~{total_token_estimate} tokens")
        logger.info(f"Strategy: {current_year_strategy}" + (f" (adaptive applied to large filing)" if adaptive_used else ""))
        logger.info(f"Years analyzed: {final_thesis['metadata']['context_management']['years_analyzed']}")
        if missing_years:
            logger.info(f"Years skipped (no 10-K available): {sorted(missing_years, reverse=True)}")

        return final_thesis

    # =========================================================================
    # PHASE 9.1: TIER 1 DECISION GATE METHODS
    # =========================================================================

    def _evaluate_tier1_decision(
        self,
        ticker: str,
        current_year_analysis: Dict[str, Any],
        verified_metrics: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Phase 9.1: Evaluate Tier 1 screening to decide if Tier 2 is warranted.

        After Tier 1 (GuruFocus + Latest 10-K + Web search), parse the initial
        analysis to determine if this is a BUY candidate worthy of deep dive.

        Decision Logic:
        - AVOID (40-50%): Fails core criteria (low ROIC, no moat, red flags)
        - WATCH (40-50%): Good business but wrong price or missing criteria
        - BUY candidate (10-20%): All 8 criteria look strong → Proceed to Tier 2

        Args:
            ticker: Stock ticker
            current_year_analysis: Result from Stage 1 (current year analysis)
            verified_metrics: GuruFocus verified metrics

        Returns:
            {
                "decision": "BUY" | "WATCH" | "AVOID",
                "reasoning": "Brief explanation of decision"
            }
        """
        # Extract the thesis from current year analysis
        thesis_text = current_year_analysis.get('full_analysis', '')

        # Parse decision from thesis using existing method
        parsed_decision = self._parse_decision(ticker, thesis_text)
        decision = parsed_decision.get('decision', 'WATCH')

        # Extract key disqualifying factors from verified metrics
        roic_avg = verified_metrics.get('roic_10y_avg')
        debt_equity = verified_metrics.get('debt_equity')

        # Hard disqualifications (automatic AVOID)
        hard_avoid_reasons = []

        if roic_avg and roic_avg < 0.10:  # ROIC < 10%
            hard_avoid_reasons.append(f"ROIC too low ({roic_avg:.1%} < 10%)")

        if debt_equity and debt_equity > 1.5:  # Debt/Equity > 1.5
            hard_avoid_reasons.append(f"Excessive debt (D/E = {debt_equity:.2f})")

        # Check if thesis contains clear AVOID or WATCH signals
        thesis_lower = thesis_text.lower()

        avoid_signals = [
            "outside circle of competence",
            "no moat",
            "eroding moat",
            "poor management",
            "red flag",
            "avoid",
            "pass on this",
            "cannot recommend"
        ]

        watch_signals = [
            "watch",
            "waiting for better price",
            "margin of safety too low",
            "overvalued",
            "fairly valued"
        ]

        has_avoid_signal = any(signal in thesis_lower for signal in avoid_signals)
        has_watch_signal = any(signal in thesis_lower for signal in watch_signals)

        # Decision logic
        if hard_avoid_reasons or has_avoid_signal or decision == "AVOID":
            reasoning = "; ".join(hard_avoid_reasons) if hard_avoid_reasons else "Fails core investment criteria"
            return {
                "decision": "AVOID",
                "reasoning": reasoning
            }

        elif has_watch_signal or decision == "WATCH":
            return {
                "decision": "WATCH",
                "reasoning": "Good business but insufficient margin of safety or missing criteria"
            }

        else:
            # BUY candidate - proceed to Tier 2
            return {
                "decision": "BUY",
                "reasoning": "Strong Tier 1 screening - all 8 criteria look promising. Proceeding to Tier 2 deep dive."
            }

    def _finalize_tier1_result(
        self,
        ticker: str,
        current_year_analysis: Dict[str, Any],
        tier1_decision: Dict[str, str],
        verified_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 9.1: Finalize Tier 1-only result for AVOID/WATCH decisions.

        When Tier 1 screening results in AVOID or WATCH, create final result
        without proceeding to expensive Tier 2 deep dive.

        Args:
            ticker: Stock ticker
            current_year_analysis: Result from Stage 1
            tier1_decision: Decision dict from _evaluate_tier1_decision()
            verified_metrics: GuruFocus verified metrics

        Returns:
            Complete analysis result (same format as full deep dive)
        """
        logger.info(f"[TIER 1 FINALIZATION] Creating Tier 1-only result for {ticker}")

        # Parse decision details from current year analysis
        thesis_text = current_year_analysis.get('full_analysis', '')
        parsed_decision = self._parse_decision(ticker, thesis_text)

        # Create final result matching deep dive format
        final_result = {
            'ticker': ticker,
            'decision': tier1_decision['decision'],
            'conviction': parsed_decision.get('conviction', 'LOW'),
            'thesis': thesis_text,  # Use Tier 1 analysis as thesis
            'intrinsic_value': parsed_decision.get('intrinsic_value'),
            'current_price': parsed_decision.get('current_price'),
            'margin_of_safety': parsed_decision.get('margin_of_safety'),

            # Tier 1 summary
            'analysis_summary': {
                'years_analyzed': [current_year_analysis.get('year')],
                'tier1_only': True,
                'tier2_skipped': f"Decision: {tier1_decision['decision']} - Deep dive not warranted",
                'cost_savings': 'Tier 2 deep dive ($2-4) avoided'
            },

            # Metadata
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'tool_calls_made': current_year_analysis.get('tool_calls_made', 0),
                'tier': 'TIER_1_ONLY',
                'tier1_decision': tier1_decision['decision'],
                'tier1_reasoning': tier1_decision['reasoning'],
                'years_analyzed': 1,
                'context_management': {
                    'strategy': current_year_analysis.get('strategy', 'standard'),
                    'current_year_tokens': current_year_analysis.get('token_estimate', 0),
                    'prior_years_tokens': 0,  # No prior years analyzed
                    'total_token_estimate': current_year_analysis.get('token_estimate', 0),
                    'years_analyzed': [current_year_analysis.get('year')],
                    'years_requested': 1,  # Tier 1 only
                    'tier1_screening': True
                }
            }
        }

        # Add verified metrics to metadata
        final_result['metadata']['verified_metrics'] = verified_metrics

        logger.info(f"[TIER 1 COMPLETE] {ticker}: {tier1_decision['decision']} - {tier1_decision['reasoning']}")

        return final_result

    def _analyze_mda_history(
        self,
        ticker: str,
        num_years: int = 5,
        years_to_analyze: int = 6
    ) -> tuple:
        """
        Phase 9.1: Analyze historical MD&A sections (NOT full 10-Ks).

        This is Tier 2 deep dive for BUY candidates only. Instead of reading
        full prior year 10-Ks, read ONLY MD&A sections to track management's
        strategic thinking and track record.

        Why MD&A only:
        - MD&A is 10-20% of full 10-K → 5 years of MD&A < 1 year of full filing
        - MD&A reveals management thinking: strategy, challenges, decisions
        - All quantitative data comes from GuruFocus (no redundancy)
        - Cost-controlled, context-efficient

        Args:
            ticker: Stock ticker
            num_years: Number of prior years of MD&A to read (default: 5)
            years_to_analyze: Total years being analyzed (for progress calculation)

        Returns:
            Tuple of (summaries, missing_years):
            - summaries: List of MD&A summaries
            - missing_years: List of years where MD&A was not available
        """
        logger.info(f"[TIER 2] Reading {num_years} years of MD&A for management track record")

        summaries = []
        missing_years = []
        most_recent_year = self.most_recent_fiscal_year

        for i in range(num_years):
            year = most_recent_year - 1 - i  # 2024, 2023, 2022, etc.
            year_number = i + 2  # Year 2 of total analysis

            # Calculate progress within Tier 2 (40-80% overall)
            if num_years > 0:
                year_progress_start = 0.4 + (i / num_years) * 0.4
                year_progress_end = 0.4 + ((i + 1) / num_years) * 0.4
            else:
                year_progress_start = 0.4
                year_progress_end = 0.8

            logger.info(f"  Fetching {year} MD&A section (ENFORCED: MD&A only, not full 10-K)...")
            self._report_progress(
                stage="tier2",
                progress=year_progress_start,
                message=f"📅 Year {year_number} of {years_to_analyze}: Reading FY {year} MD&A..."
            )

            # Phase 9.1 FIX: Directly fetch MD&A section (don't let LLM decide)
            # This GUARANTEES we only fetch MD&A, not full 10-K
            try:
                logger.info(f"  [MD&A ENFORCED] Fetching section='mda' for {ticker} {year}")
                mda_result = self.tools["sec_filing"].execute(
                    ticker=ticker,
                    filing_type="10-K",
                    section="mda",  # ENFORCED: Only MD&A section
                    year=year
                )

                if not mda_result.get("success"):
                    logger.warning(f"  Skipping {year}: MD&A fetch failed ({mda_result.get('error', 'unknown error')})")
                    missing_years.append(year)
                    continue

                mda_content = mda_result["data"]["content"]
                mda_length = len(mda_content)
                logger.info(f"  [MD&A FETCHED] {year} MD&A: {mda_length:,} characters")

            except Exception as e:
                logger.warning(f"  Skipping {year}: Unable to fetch MD&A ({str(e)})")
                missing_years.append(year)
                continue

            # Phase 9.1: MD&A-focused prompt for management track record
            # Now we PROVIDE the MD&A content instead of asking LLM to fetch it
            mda_prompt = f"""I'm providing you with {ticker}'s {year} Management Discussion & Analysis (MD&A) section.

**CONTEXT:**

You've already analyzed the most recent fiscal year ({self.most_recent_fiscal_year}) comprehensively.
Now we're examining {year} MD&A to understand management's track record over time.

**MD&A CONTENT FOR {year}:**

{mda_content}

**YOUR TASK:**

Analyze the MD&A above and create a summary focusing on:

1. **Management's Strategic Thinking**:
   - What were management's stated priorities in {year}?
   - What challenges did they identify?
   - What decisions did they make (capital allocation, M&A, product launches)?
   - How did they explain performance?

2. **Track Record Assessment**:
   - Did they deliver on commitments made in prior years?
   - Were they candid about challenges or evasive?
   - Did they make excuses or take accountability?
   - How did they allocate capital (R&D, CapEx, buybacks, dividends, M&A)?

3. **Create MD&A Summary** (2-3K tokens):

   === {year} MD&A ANALYSIS ===

   **Management's Strategic Priorities ({year}):**
   - [What were the top 3-5 priorities mentioned?]
   - [Any notable strategic shifts vs prior year?]

   **Key Quotes from MD&A:**
   - [Quote 1: Revealing management thinking]
   - [Quote 2: Capital allocation philosophy]
   - [Quote 3: How they addressed challenges]

   **Capital Allocation Decisions ({year}):**
   - R&D spending: $X.XB (X% of revenue)
   - CapEx: $X.XB
   - Buybacks: $X.XB
   - Dividends: $X.XB
   - M&A: [Any acquisitions? Integration success?]

   **Challenges Identified:**
   - [Challenge 1: How did management describe it?]
   - [Challenge 2: Did they take ownership or blame externals?]
   - [Challenge 3: Concrete action plans mentioned?]

   **Communication Style:**
   - Candid and transparent? Or evasive and obfuscated?
   - Realistic or overly optimistic?
   - Evidence-based or narrative-driven?

   **Promises vs Delivery:**
   - [Did they deliver on commitments made in prior year MD&A?]
   - [Any missed targets? How did they explain?]
   - [Consistent execution or pattern of excuses?]

   **Management Quality Assessment ({year}):**
   - Honesty & Transparency: [HIGH / MODERATE / LOW]
   - Rational Decision-Making: [HIGH / MODERATE / LOW]
   - Capital Allocation Skill: [HIGH / MODERATE / LOW]
   - Overall: [EXCELLENT / GOOD / ADEQUATE / POOR]

   === END {year} MD&A SUMMARY ===

**CRITICAL:**
- Keep summary under 3,000 tokens
- Focus on MANAGEMENT TRACK RECORD (not quantitative re-extraction)
- All financial numbers are already in GuruFocus - don't recalculate
- Identify patterns: Do they deliver on promises? Honest communication?
- **DO NOT fetch any additional SEC filings** - you have all the MD&A content above
"""

            # Run MD&A analysis (LLM analyzes the provided content, no tool calls needed)
            logger.info(f"  Analyzing {year} MD&A for {ticker}...")
            result = self._run_analysis_loop(ticker, mda_prompt)

            # Extract summary
            summary_text = self._extract_summary_section(
                result.get('thesis', ''),
                year=year,
                ticker=ticker
            )

            # Estimate tokens (summary should be ~2-3K tokens)
            token_estimate = len(summary_text) // 4

            logger.info(f"  {year} MD&A summary complete: {len(summary_text)} chars (~{token_estimate} tokens)")

            summaries.append({
                'year': year,
                'summary': summary_text,
                'tool_calls_made': result.get('metadata', {}).get('tool_calls', 0),
                'token_estimate': token_estimate,
                'type': 'mda_only'  # Phase 9.1 marker
            })

            self._report_progress(
                stage="tier2",
                progress=year_progress_end,
                message=f"✅ Year {year_number}: FY {year} MD&A analyzed"
            )

        return summaries, missing_years

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

**CITATION REQUIREMENTS (MANDATORY FOR ALL DEEP DIVES):**

Every financial metric, business fact, and quantitative claim MUST include a specific source citation.
Deep dive analyses require even more rigorous sourcing than quick screens.

**Citation Format Examples:**
- "Operating Cash Flow $45.2B (10-K FY2024, Consolidated Statements of Cash Flows, page 52, https://www.sec.gov/...)"
- "CapEx $11.3B (10-K FY2024, Cash Flows, page 52)"
- "Owner Earnings = $45.2B - $11.3B = $33.9B (calculated from 10-K FY2024 data)"
- "ROIC 22.3% trailing 5-year average (GuruFocus Historical Data, accessed Nov 11, 2025)"
- "Management owns 15% of shares (DEF 14A Proxy Statement 2024, page 8)"
- "Revenue grew 12% CAGR 2020-2024 (10-K FY2024, MD&A, page 28)"
- "Operates in 47 countries (10-K FY2024, Business section, page 5)"

**What to cite:**
✅ ALL financial statement data (revenue, cash flow, debt, assets, etc.)
✅ ALL calculated metrics (Owner Earnings, ROIC, DCF assumptions, growth rates)
✅ Management quotes and statements (with exact 10-K section and page)
✅ Business facts (locations, employees, customers, products)
✅ Industry and competitive data
✅ Risk factors (cite specific risk from 10-K Risk Factors section)
✅ Valuation assumptions (discount rate, growth rate, etc. with reasoning)

**For calculations, show your work:**
- "Owner Earnings = OCF ($45.2B) - CapEx ($11.3B) = $33.9B (10-K FY2024)"
- "Discount rate: 10% (company WACC ~8% + 2% margin of safety)"
- "Terminal growth: 3% (conservative estimate, below long-term GDP growth)"

**Golden Rule:** If you cannot cite a specific source (with section and page number for 10-K data),
do not include that data point. Deep dives require bulletproof sourcing.

Take your time. Read the full annual reports. Think deeply. Cite everything. And remember -
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

**IMPORTANT QUICK SCREEN LIMITATIONS:**

This is a QUICK SCREEN, not a deep dive analysis. Keep it simple:

✅ **DO USE** these simple screening metrics:
- ROIC (return on invested capital)
- P/E ratio or other simple valuation multiples
- Debt/Equity ratio
- Operating margin and net margin
- Revenue growth trends
- Basic qualitative assessment ("appears undervalued" or "seems expensive")

❌ **DO NOT MENTION** these advanced calculations (reserved for deep dives):
- Owner Earnings (requires OCF - CapEx calculations from cash flow statement)
- DCF Intrinsic Value (requires multi-year projections and WACC calculations)
- Detailed Margin of Safety with precise dollar values
- Complex valuation models

If you find yourself wanting to say "Trading at 33x Owner Earnings" or "DCF value of $XXX",
STOP - those require deep dive analysis. For quick screens, stick to simple statements like
"Trading at 25x earnings, which seems expensive for this growth rate" or "P/E of 15 suggests
potential value."

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
it in 30 seconds. Use clear, direct language.

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

**CITATION REQUIREMENTS (MANDATORY):**

Every financial metric and data point you present MUST include a specific source citation.
This is non-negotiable for quality analysis.

**Citation Format Examples:**
- "Revenue $11.5B (GuruFocus Summary, accessed Nov 11, 2025)"
- "ROIC 22.3% (GuruFocus Key Ratios, accessed Nov 11, 2025)"
- "Operates 500+ retail locations (10-K FY2024, Business section, page 3, https://www.sec.gov/...)"
- "Recent acquisition of CompanyX (10-K FY2024, MD&A section, page 25)"
- "Industry growing at 8% annually (Company 10-K, Industry Overview, page 5)"

**What to cite:**
✅ ALL financial metrics (revenue, margins, ROIC, debt, etc.)
✅ Business facts (number of locations, customer counts, product lines)
✅ Industry data and competitive information
✅ Management statements and strategy
✅ Any quantitative claims

**Unacceptable:**
❌ "Revenue is approximately $10B" (no source = hallucination risk)
❌ "ROIC around 20%" (no source = unreliable)
❌ "Strong market position" (vague, no supporting citation)

**Golden Rule:** If you cannot cite a specific source for a data point, do not include that data point.
It's better to say "Revenue data not available" than to present uncited figures.

---

**CRITICAL REQUIREMENTS:**

1. **Be decisive** - Users need clear guidance on whether to spend $3-4 on deep dive
2. **Be honest** - If ROIC is 8%, say it's below your 15% hurdle and explain why that matters
3. **Be specific** - Use actual numbers with sources, not vague statements
4. **Be concise** - Target 800-1,000 words total (much shorter than deep dive's 3,500)
5. **Be helpful** - Users should walk away with clear understanding of business + recommendation
6. **Use your voice** - Sound like Warren Buffett explaining to a friend over coffee
7. **Cite everything** - Every financial metric must have a source (see Citation Requirements above)

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

        # Phase 7.7 Phase 2: Extract structured metrics from tool cache
        metrics = self._extract_metrics_from_cache(ticker, self.most_recent_fiscal_year)

        # Phase 7.7 Phase 3: Extract structured insights from analysis text
        thesis_text = result.get('thesis', '')
        insights = self._extract_insights_from_analysis(
            ticker,
            self.most_recent_fiscal_year,
            thesis_text
        )

        # Phase 7.7 Phase 3.2: Remove <INSIGHTS> JSON block from user-visible thesis
        import re
        clean_thesis = re.sub(r'<INSIGHTS>.*?</INSIGHTS>', '', thesis_text, flags=re.DOTALL).strip()

        return {
            'year': self.most_recent_fiscal_year,
            'full_analysis': clean_thesis,  # Thesis with JSON block removed
            'metrics': metrics,  # Phase 7.7 Phase 2: Structured quantitative data
            'insights': insights,  # Phase 7.7 Phase 3: Structured qualitative data
            'tool_calls_made': result.get('metadata', {}).get('tool_calls', 0),
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
        summary = self._extract_summary_section(
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

        # Phase 7.7 Phase 2: Extract structured metrics from tool cache
        metrics = self._extract_metrics_from_cache(ticker, self.most_recent_fiscal_year)

        # Phase 7.7 Phase 3: Extract structured insights from analysis text
        insights = self._extract_insights_from_analysis(
            ticker,
            self.most_recent_fiscal_year,
            summary  # Use summary text for extraction
        )

        # Phase 7.7 Phase 3.2: Remove <INSIGHTS> JSON block from user-visible thesis
        import re
        clean_summary = re.sub(r'<INSIGHTS>.*?</INSIGHTS>', '', summary, flags=re.DOTALL).strip()

        return {
            'year': self.most_recent_fiscal_year,
            'full_analysis': clean_summary,  # Summary with JSON block removed
            'metrics': metrics,  # Phase 7.7 Phase 2: Structured quantitative data
            'insights': insights,  # Phase 7.7 Phase 3: Structured qualitative data
            'tool_calls_made': result.get('metadata', {}).get('tool_calls', 0),
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
            summary_text = self._extract_summary_section(
                result.get('thesis', ''),
                year=year
            )

            # Extract key metrics (legacy text-based extraction)
            key_metrics = self._extract_metrics_from_summary(summary_text)

            # Phase 7.7 Phase 2: Extract structured metrics from tool cache
            structured_metrics = self._extract_metrics_from_cache(ticker, year)

            # Phase 7.7 Phase 3: Extract structured insights from summary text
            structured_insights = self._extract_insights_from_analysis(ticker, year, summary_text)

            # Phase 7.7 Phase 3.2: Remove <INSIGHTS> JSON block from user-visible summary
            import re
            clean_summary = re.sub(r'<INSIGHTS>.*?</INSIGHTS>', '', summary_text, flags=re.DOTALL).strip()

            # Estimate tokens
            token_estimate = len(clean_summary) // 4

            summaries.append({
                'year': year,
                'summary': clean_summary,  # Summary with JSON block removed
                'key_metrics': key_metrics,  # Legacy text-based metrics
                'metrics': structured_metrics,  # Phase 7.7 Phase 2: Structured quantitative data
                'insights': structured_insights,  # Phase 7.7 Phase 3: Structured qualitative data
                'token_estimate': token_estimate,
                'tool_calls_made': result.get('metadata', {}).get('tool_calls', 0)
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

    def _build_structured_data_section(
        self,
        ticker: str,
        structured_metrics: Dict[str, Any],
        structured_insights: Dict[str, Any]
    ) -> str:
        """
        Phase 7.7.4: Build structured data summary section for synthesis prompt.

        Creates formatted tables showing quantitative metrics and qualitative insights
        across all years, enabling the LLM to reference exact numbers without parsing text.

        Args:
            ticker: Stock ticker
            structured_metrics: Structured quantitative metrics from all years
            structured_insights: Structured qualitative insights from all years

        Returns:
            Formatted string section with structured data tables
        """
        from src.agent.data_structures import AnalysisMetrics, AnalysisInsights

        if not structured_metrics and not structured_insights:
            return ""

        section = """
**PHASE 7.7.4: STRUCTURED DATA REFERENCE**

The following tables provide VALIDATED quantitative metrics and qualitative assessments
from your analysis. Use these EXACT values in your synthesis to ensure accuracy.

"""

        # Build quantitative metrics table
        if structured_metrics and structured_metrics.get("all_years"):
            section += "**QUANTITATIVE METRICS (Validated via Pydantic):**\n\n"
            section += "```\n"

            all_years = structured_metrics["all_years"]

            # Table header
            section += "Year  | ROIC  | Revenue | OpMargin | D/E  | FCF     | Price | MoS\n"
            section += "------+-------+---------+----------+------+---------+-------+-----\n"

            # Table rows (one per year)
            for year_data in all_years:
                year = year_data.get("year", "N/A")
                metrics_dict = year_data.get("metrics", {})

                # Create AnalysisMetrics object to use Pydantic's validation
                try:
                    metrics = AnalysisMetrics(**metrics_dict) if metrics_dict else AnalysisMetrics()
                except Exception as e:
                    logger.warning(f"[PHASE 7.7.4] Could not validate metrics for {year}: {e}")
                    metrics = AnalysisMetrics()

                # Format each metric with proper units
                roic_str = f"{metrics.roic*100:5.1f}%" if metrics.roic is not None else "  --  "
                revenue_str = f"${metrics.revenue/1000:6.1f}B" if metrics.revenue is not None else "   --   "
                opmargin_str = f"{metrics.operating_margin*100:6.1f}%" if metrics.operating_margin is not None else "   --   "
                de_str = f"{metrics.debt_equity:4.2f}" if metrics.debt_equity is not None else " -- "
                fcf_str = f"${metrics.free_cash_flow/1000:6.1f}B" if metrics.free_cash_flow is not None else "   --   "
                price_str = f"${metrics.current_price:6.2f}" if metrics.current_price is not None else "  --   "
                mos_str = f"{metrics.margin_of_safety*100:4.0f}%" if metrics.margin_of_safety is not None else " -- "

                section += f"{year} | {roic_str} | {revenue_str} | {opmargin_str} | {de_str} | {fcf_str} | {price_str} | {mos_str}\n"

            section += "```\n\n"

            # Add trend indicators
            section += "**Trend Indicators:**\n"
            if len(all_years) >= 2:
                # Calculate CAGR for revenue if available
                first_year_metrics = all_years[-1].get("metrics", {})
                last_year_metrics = all_years[0].get("metrics", {})

                first_revenue = first_year_metrics.get("revenue")
                last_revenue = last_year_metrics.get("revenue")
                first_year_num = all_years[-1].get("year")
                last_year_num = all_years[0].get("year")

                if first_revenue and last_revenue and first_year_num and last_year_num:
                    years_diff = last_year_num - first_year_num
                    if years_diff > 0:
                        revenue_cagr = ((last_revenue / first_revenue) ** (1 / years_diff) - 1) * 100
                        section += f"- Revenue CAGR ({first_year_num}-{last_year_num}): {revenue_cagr:.1f}%\n"

                # ROIC trend
                first_roic = first_year_metrics.get("roic")
                last_roic = last_year_metrics.get("roic")
                if first_roic is not None and last_roic is not None:
                    roic_change = (last_roic - first_roic) * 100  # percentage points
                    trend = "improving" if roic_change > 2 else "declining" if roic_change < -2 else "stable"
                    section += f"- ROIC Trend: {trend} ({first_roic*100:.1f}% -> {last_roic*100:.1f}%, {roic_change:+.1f}pp)\n"

                # Margin trend
                first_opmargin = first_year_metrics.get("operating_margin")
                last_opmargin = last_year_metrics.get("operating_margin")
                if first_opmargin is not None and last_opmargin is not None:
                    margin_change = (last_opmargin - first_opmargin) * 100
                    trend = "expanding" if margin_change > 2 else "compressing" if margin_change < -2 else "stable"
                    section += f"- Operating Margin Trend: {trend} ({first_opmargin*100:.1f}% -> {last_opmargin*100:.1f}%, {margin_change:+.1f}pp)\n"

            section += "\n"

        # Build qualitative insights table
        if structured_insights and structured_insights.get("all_years"):
            section += "**QUALITATIVE INSIGHTS (Validated via Pydantic):**\n\n"
            section += "```\n"

            all_years = structured_insights["all_years"]

            # Table header
            section += "Year  | Decision | Conviction | Moat      | Risk\n"
            section += "------+----------+------------+-----------+----------\n"

            # Table rows
            for year_data in all_years:
                year = year_data.get("year", "N/A")
                insights_dict = year_data.get("insights", {})

                # Create AnalysisInsights object to use Pydantic's validation
                try:
                    insights = AnalysisInsights(**insights_dict) if insights_dict else AnalysisInsights()
                except Exception as e:
                    logger.warning(f"[PHASE 7.7.4] Could not validate insights for {year}: {e}")
                    insights = AnalysisInsights()

                # Format each insight
                decision = insights.decision[:8] if insights.decision else "   --   "
                conviction = insights.conviction[:10] if insights.conviction else "    --    "
                moat = insights.moat_rating[:9] if insights.moat_rating else "   --    "
                risk = insights.risk_rating[:8] if insights.risk_rating else "   --   "

                section += f"{year} | {decision:8} | {conviction:10} | {moat:9} | {risk:8}\n"

            section += "```\n\n"

            # Add evolution indicators
            section += "**Qualitative Evolution:**\n"
            if len(all_years) >= 2:
                first_insights_dict = all_years[-1].get("insights", {})
                last_insights_dict = all_years[0].get("insights", {})

                # Decision consistency
                first_decision = first_insights_dict.get("decision")
                last_decision = last_insights_dict.get("decision")
                if first_decision and last_decision:
                    if first_decision == last_decision:
                        section += f"- Decision Consistency: {last_decision} maintained over period\n"
                    else:
                        section += f"- Decision Evolution: {first_decision} -> {last_decision}\n"

                # Moat evolution
                first_moat = first_insights_dict.get("moat_rating")
                last_moat = last_insights_dict.get("moat_rating")
                moat_order = ["WEAK", "MODERATE", "STRONG", "DOMINANT"]
                if first_moat and last_moat and first_moat in moat_order and last_moat in moat_order:
                    first_idx = moat_order.index(first_moat)
                    last_idx = moat_order.index(last_moat)
                    if last_idx > first_idx:
                        section += f"- Moat Strengthening: {first_moat} -> {last_moat}\n"
                    elif last_idx < first_idx:
                        section += f"- Moat Weakening: {first_moat} -> {last_moat}\n"
                    else:
                        section += f"- Moat Stable: {last_moat} maintained\n"

            section += "\n"

        section += "**IMPORTANT:** Use these validated values in your financial analysis and synthesis. "
        section += "Do NOT re-parse numbers from text - reference these tables for accuracy.\n\n"
        section += "---\n\n"

        return section

    def _get_complete_thesis_prompt(
        self,
        ticker: str,
        current_year: Dict[str, Any],
        prior_years: List[Dict[str, Any]],
        structured_metrics: Dict[str, Any] = None,
        structured_insights: Dict[str, Any] = None,
        verified_metrics: Dict[str, Any] = None
    ) -> str:
        """
        Get synthesis prompt that ensures COMPLETE investment thesis generation.

        Phase 7.7.4: Enhanced with structured metrics and insights for accurate synthesis.
        Phase 7.8: Enhanced with verified GuruFocus metrics for decision consistency.

        This prompt explicitly requires all 10 sections of a Warren Buffett-style
        comprehensive analysis, preventing the agent from generating only conclusions.

        Args:
            ticker: Stock ticker
            current_year: Current year analysis results
            prior_years: Prior years summaries
            structured_metrics: Phase 7.7.4 - Structured quantitative metrics from all years
            structured_insights: Phase 7.7.4 - Structured qualitative insights from all years
            verified_metrics: Phase 7.8 - Verified GuruFocus metrics (ground truth for decisions)

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

        # Phase 7.7.4: Build structured data summary if available
        structured_data_section = self._build_structured_data_section(
            ticker, structured_metrics, structured_insights
        ) if (structured_metrics or structured_insights) else ""

        # Phase 7.8: Build verified metrics section for decision consistency
        verified_metrics_section = ""
        if verified_metrics:
            verified_metrics_section = """
---

**🔒 VERIFIED METRICS (GROUND TRUTH FOR DECISIONS) - Phase 7.8**

**CRITICAL: Use these GuruFocus verified metrics as your GROUND TRUTH for financial analysis and investment decisions.**

These metrics are from GuruFocus (verified external data source) and should be used instead of any LLM-extracted values. Your final decision (BUY/WATCH/AVOID) MUST be based on these verified numbers, not on any values you extracted from 10-Ks.

**Key Verified Metrics (Most Recent FY):**
"""
            # Add metrics if available
            if verified_metrics.get("roic") is not None:
                verified_metrics_section += f"\n- **ROIC**: {verified_metrics['roic']*100:.1f}% (GuruFocus verified)"
            if verified_metrics.get("revenue") is not None:
                verified_metrics_section += f"\n- **Revenue**: ${verified_metrics['revenue']:,.0f}M (GuruFocus verified)"
            if verified_metrics.get("owner_earnings") is not None:
                verified_metrics_section += f"\n- **Owner Earnings**: ${verified_metrics['owner_earnings']:,.0f}M "
                if all(v is not None for v in [verified_metrics.get('net_income'), verified_metrics.get('depreciation_amortization'), verified_metrics.get('capex')]):
                    verified_metrics_section += f"(Calculated from GuruFocus components: NI + D&A - CapEx - ΔWC)"
                else:
                    verified_metrics_section += f"(GuruFocus FCF verified)"
            if verified_metrics.get("operating_margin") is not None:
                verified_metrics_section += f"\n- **Operating Margin**: {verified_metrics['operating_margin']*100:.1f}% (GuruFocus verified)"
            if verified_metrics.get("debt_equity") is not None:
                verified_metrics_section += f"\n- **Debt/Equity**: {verified_metrics['debt_equity']:.2f} (GuruFocus verified)"

            verified_metrics_section += """

**Component Breakdown (for Owner Earnings):**
"""
            if verified_metrics.get("net_income") is not None:
                verified_metrics_section += f"\n- Net Income: ${verified_metrics['net_income']:,.0f}M"
            if verified_metrics.get("depreciation_amortization") is not None:
                verified_metrics_section += f"\n- D&A: +${verified_metrics['depreciation_amortization']:,.0f}M"
            if verified_metrics.get("capex") is not None:
                verified_metrics_section += f"\n- CapEx: -${verified_metrics['capex']:,.0f}M"
            if verified_metrics.get("working_capital_change") is not None and verified_metrics['working_capital_change'] != 0:
                verified_metrics_section += f"\n- Working Capital Change: -${verified_metrics['working_capital_change']:,.0f}M"
            if verified_metrics.get("free_cash_flow") is not None:
                verified_metrics_section += f"\n- Free Cash Flow: ${verified_metrics['free_cash_flow']:,.0f}M (for reference)"

            verified_metrics_section += """

**DECISION CONSISTENCY REQUIREMENT:**

When you write your Final Investment Decision (Section 10), you MUST base it on these verified metrics. If you previously analyzed with different numbers, DISREGARD those extractions and use these verified values instead.

Examples:
- If ROIC < 15% (Buffett's hurdle), this is a serious concern → likely AVOID or WATCH
- If Owner Earnings is negative or declining → likely AVOID
- If Debt/Equity > 2.0 → concerning leverage → likely WATCH or AVOID

Your decision should be CONSISTENT with these verified numbers.

---
"""

        synthesis_prompt = f"""You've completed a thorough multi-year analysis of {ticker}.
Now synthesize your findings into a COMPLETE but CONCISE investment thesis.

**CRITICAL INSTRUCTIONS - READ CAREFULLY:**

1. You MUST write ALL 10 sections listed below in sequential order
2. DO NOT stop writing until you have completed Section 10 (Final Investment Decision)
3. Focus on TRENDS and INSIGHTS, not repeating all data from every year
4. Be CONCISE - you have a 25,000 word limit, so prioritize what matters most
5. An incomplete thesis (missing Section 10 decision) is considered a FAILURE
6. **[Phase 7.8] BASE YOUR DECISION ON VERIFIED METRICS (see below), not LLM extractions**

**WRITING EFFICIENCY GUIDELINES:**

- **DON'T repeat data already in year summaries** - reference it and explain what it MEANS
- **DO focus on 7-year trends** - how has moat/management/financials evolved?
- **DO be selective** - include only the most important examples/numbers
- **DO complete all sections** - especially the decision (Section 10)

You will know you're finished ONLY when you've written your Final Investment
Decision in Section 10. If you're thinking about stopping before that, you're
not done yet - keep writing.

**CURRENT YEAR (2024) - FULL ANALYSIS:**

{current_year['full_analysis']}

---

**PRIOR YEARS - SUMMARIES:**

{prior_years_text}

---
{structured_data_section}{verified_metrics_section}
**YOUR TASK: Write a COMPLETE Investment Thesis**

Write a comprehensive investment thesis for {ticker} applying the 8 core investment
principles framework. Include ALL sections below. This should be a complete analysis
that any investor could read to understand the entire investment case.

**WRITE ALL 10 SECTIONS BELOW IN ORDER - NO EXCEPTIONS:**

**LENGTH REQUIREMENTS - STAY CONCISE:**
- Sections 1-3: 2-3 paragraphs each (business context)
- Section 4: 3-4 paragraphs (financial trends with tables)
- Sections 5-9: 2 paragraphs each (focused insights)
- Section 10: 1 paragraph (clear decision)
- Total target: ~15-20 paragraphs (not 40+!)

## **1. Business Overview** (2-3 paragraphs MAX)

Concisely explain what {ticker} does:
- Core products/services and customers
- Industry and market position
- Geographic footprint

Use simple language but don't repeat details from year summaries.

## **2. Economic Moat Analysis** (2-3 paragraphs MAX)

Identify moat type(s) and provide SPECIFIC EVIDENCE:
- Brand/Network/Switching Costs/Cost Advantage/Intangible Assets?
- Market share trends, retention rates, pricing power examples
- 7-year evolution: Strengthening or weakening?
- Durability: Will it last 10+ years?

Focus on INSIGHTS from the {total_years}-year analysis, not repeating all data.

## **3. Management Quality** (2-3 paragraphs MAX)

Cover these key aspects CONCISELY:
- **Leadership**: Current CEO/CFO (research any recent changes with web_search)
- **Competence**: Track record across {total_years} years (1-2 key examples)
- **Integrity**: Communication style in filings (1 quote showing candor/concern)
- **Capital Allocation**: ROIC trend, buybacks/dividends, M&A (disciplined or wasteful?)
- **Owner Mentality**: Insider ownership %, compensation structure

Focus on TRENDS and KEY EXAMPLES, not exhaustive lists.

## **4. Financial Analysis** (3-4 paragraphs MAX)

Show {total_years}-year TRENDS with concise tables:

**Revenue & ROIC Trends (REQUIRED - use calculator_tool):**
```
Year    Revenue    ROIC    Owner Earnings
2024    $X.XB      XX%     $X.XB
[first] $X.XB      XX%     $X.XB
CAGR:   X%         --      X%

ROIC Calculation (2024): NOPAT / Invested Capital = XX%
Source: calculator_tool output
vs 15% Buffett hurdle: Pass/Fail
```

**Profitability & Balance Sheet:**
```
Margins (2024 vs [first year]):
- Gross:     XX% → XX% (expanding/declining)
- Operating: XX% → XX% (expanding/declining)

Balance Sheet:
- Debt/Equity: X.X (comfortable/concerning)
- Cash: $X.XB vs Debt: $X.XB
```

Explain what these trends tell you about business quality. Be concise.

## **5. Growth Prospects** (2 paragraphs MAX)

- **Growth Drivers**: Where is growth coming from? (market expansion, new products, pricing power)
- **TAM & Market Share**: How big is the opportunity? Room to expand?
- **Your Estimate**: Conservative growth rate (X% annually) based on which factors?

## **6. Competitive Position** (2 paragraphs MAX)

- **Key Competitors**: Who and how does {ticker} compare?
- **Competitive Dynamics**: Rational competition or price wars? Disruption risk?
- **Differentiation**: What makes {ticker} sustainably different?

## **7. Risk Analysis** (2 paragraphs MAX)

**Top 3-5 Risks** (be specific):
1. [Most concerning risk with evidence]
2. [Second risk]
3-5. [Other risks - brief]

**Risk Assessment**: Increasing/decreasing? Most concerning risk? Overall level (Low/Moderate/High)?

## **8. Multi-Year Synthesis** (2 paragraphs MAX)

Across {total_years} years, what patterns emerged?
- **Trends**: Revenue (accelerating/stable/declining?), Margins (expanding/compressing?), ROIC (improving/deteriorating?)
- **Evolution**: Is this a BETTER business today than {total_years} years ago? Why?
- **10-Year Question**: Will it be stronger in 10 years? Comfortable owning forever?

## **9. Valuation & Margin of Safety** (3 paragraphs MAX)

**REQUIRED CALCULATIONS (use calculator_tool):**
```
Owner Earnings = OCF - Maintenance CapEx = $X.XB
(Source: 10-K Cash Flow Statement)

DCF Intrinsic Value (use calculator_tool):
- Base: $X.XB Owner Earnings
- Growth: X% (conservative vs X% historical)
- Discount: 10%
- Terminal: 2.5%
= Intrinsic Value: $XXX per share

Current Price: $XXX (web_search for exact price)
Margin of Safety: [(IV - Price) / IV] = X%
```

**Assessment:**
- Margin required: 15-20% (wide moat) / 25-30% (moderate moat) / 40%+ (weak moat)
- Current margin: X% - Sufficient/Insufficient?
- Valuation context: Opportunity or value trap?

## **10. Final Investment Decision** (1-2 paragraphs MAX)

**Synthesize your decision in Buffett's voice:**
- Business quality + moat + management: [2-3 sentences summary]
- Why BUY/WATCH/AVOID right now? [2-3 sentences rationale]
- Price targets and conviction level

**REQUIRED STRUCTURED OUTPUT:**
```
DECISION: [BUY / WATCH / AVOID]
CONVICTION: [HIGH / MODERATE / LOW]
INTRINSIC VALUE: $XXX
CURRENT PRICE: $XXX
MARGIN OF SAFETY: ±XX%
```

End with a relevant Buffett quote and final thought.

---

**CRITICAL REQUIREMENTS - MUST FOLLOW:**

1. **Include ALL 10 sections above** - DO NOT skip any section
2. **Write sections IN ORDER** - Start with Section 1, end with Section 10
3. **DO NOT stop early** - Stopping before Section 10 is INCOMPLETE and UNACCEPTABLE
4. **CITE ALL SOURCES WITH SPECIFICITY** - Every financial metric, quote, or claim must include detailed citations:
   - **10-K/20-F data**: "Source: 10-K FY20XX, [Section name], page XX" or if page unknown "Source: 10-K FY20XX, [Section name], Item X"
     * Examples: "Source: 10-K FY2024, Consolidated Statements of Cash Flows, page 67"
     * "Source: 20-F FY2023, Management's Discussion and Analysis, Item 5"
   - **GuruFocus data**: "Source: GuruFocus [Summary/Financials/KeyRatios/Ownership], accessed [date]"
     * Example: "Source: GuruFocus Financials, accessed November 13, 2025"
   - **Web search data**: "Source: [Source name], [Article title if available], [date]"
     * Example: "Source: Bloomberg, 'Novo Nordisk CEO Steps Down', May 16, 2025"
   - **Calculated values**: "Calculated from [source A] and [source B]"
     * Example: "Calculated from 10-K FY2024 Income Statement (EBIT) and Balance Sheet (Total Assets)"
   - **Calculator tool outputs**: Reference tool output explicitly
     * Example: "ROIC calculated using calculator_tool: 17.9% (see calculation above)"
5. **SHOW ALL CALCULATION FORMULAS** - For Owner Earnings, ROIC, DCF:
   - Show the actual formula (e.g., "ROIC = NOPAT / Invested Capital")
   - Show all input values with sources
   - Show the arithmetic step-by-step
   - Never just state a result without showing how you got it
6. **Use specific numbers and examples** from the filings you read
7. **Write professionally and clearly** throughout - analytical, evidence-based, rigorous
8. **Make it comprehensive** - target 3,000-5,000 words total
9. **Show your work** - explain reasoning, don't just state conclusions
10. **Use tables and formatting** where helpful for readability
11. **Be honest** about limitations and uncertainties
12. **Connect multi-year insights** - reference trends you observed
13. **Use proper section headers** exactly as shown (## **1. Business Overview**, etc.)
14. **End with structured decision** with all required fields in Section 10

This thesis should be so complete that an investor could read ONLY this document
and fully understand the entire investment case without needing any other analysis.

Remember your principle: "It's far better to buy a wonderful company at a fair
price than a fair company at a wonderful price."

**FINAL REMINDER BEFORE YOU START:**
You are about to write a 10-section investment thesis. Do not stop until you've
completed Section 10 (Final Investment Decision). If you find yourself thinking
"I can just give my recommendation now," STOP and keep writing the remaining sections.
The journey through all 10 sections is as important as the destination.

Now begin writing Section 1 and continue through Section 10 without stopping.
"""

        return synthesis_prompt

    def _synthesize_multi_year_analysis(
        self,
        ticker: str,
        current_year: Dict[str, Any],
        prior_years: List[Dict[str, Any]],
        structured_metrics: Dict[str, Any] = None,
        structured_insights: Dict[str, Any] = None,
        verified_metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Stage 3: Synthesize findings from current year + prior year summaries.

        Phase 7.7.4: Enhanced with structured metrics and insights for accurate synthesis.
        Phase 7.8: Enhanced with verified GuruFocus metrics for decision consistency.

        This is where Warren Buffett's real insight emerges:
        - Identifying trends (improving vs declining)
        - Assessing consistency (ROIC stable over time?)
        - Evaluating management track record
        - Understanding moat durability

        Args:
            ticker: Stock ticker
            current_year: Full analysis of current year
            prior_years: List of prior year summaries
            structured_metrics: Phase 7.7.4 - Structured quantitative metrics from all years
            structured_insights: Phase 7.7.4 - Structured qualitative insights from all years
            verified_metrics: Phase 7.8 - Verified GuruFocus metrics for decision consistency

        Returns:
            Final investment thesis with BUY/WATCH/AVOID decision
        """
        logger.info(f"Synthesizing multi-year analysis for {ticker}")
        if structured_metrics or structured_insights:
            logger.info("[PHASE 7.7.4] Using structured data for synthesis optimization")
        if verified_metrics:
            logger.info("[PHASE 7.8] Using verified metrics for decision consistency")

        # Build complete thesis prompt with explicit 10-section structure
        # Phase 7.7.4: Include structured data for accurate synthesis
        # Phase 7.8: Include verified metrics for decision consistency
        synthesis_prompt = self._get_complete_thesis_prompt(
            ticker, current_year, prior_years,
            structured_metrics=structured_metrics,
            structured_insights=structured_insights,
            verified_metrics=verified_metrics
        )

        # Log synthesis prompt size for monitoring
        prompt_chars = len(synthesis_prompt)
        prompt_tokens_est = prompt_chars // 4  # Rough estimate: 4 chars per token
        logger.info(f"Synthesis prompt size: {prompt_chars:,} characters (~{prompt_tokens_est:,} tokens)")
        logger.info(f"MAX_TOKENS available for response: {self.MAX_TOKENS:,}")

        # Run final synthesis
        result = self._run_analysis_loop(ticker, synthesis_prompt)

        # Parse decision from result
        decision_data = self._parse_decision(ticker, result.get('thesis', ''))

        # Phase 7.7 Phase 3.2: Remove <INSIGHTS> JSON block from final thesis
        import re
        final_thesis_text = result.get('thesis', '')
        clean_final_thesis = re.sub(r'<INSIGHTS>.*?</INSIGHTS>', '', final_thesis_text, flags=re.DOTALL).strip()

        # Build complete result
        final_result = {
            'ticker': ticker,
            'decision': decision_data['decision'],
            'conviction': decision_data['conviction'],
            'thesis': clean_final_thesis,  # Final thesis with JSON block removed
            'intrinsic_value': decision_data.get('intrinsic_value'),
            'current_price': decision_data.get('current_price'),
            'margin_of_safety': decision_data.get('margin_of_safety'),

            # Multi-year context
            'analysis_summary': {
                'years_analyzed': [current_year.get('year')] + [p['year'] for p in prior_years],
                'current_year_calls': current_year.get('tool_calls_made', 0),
                'prior_years_calls': sum(p.get('tool_calls_made', 0) for p in prior_years),
                'synthesis_calls': result.get('metadata', {}).get('tool_calls', 0),
                'total_tool_calls': (
                    current_year.get('tool_calls_made', 0) +
                    sum(p.get('tool_calls_made', 0) for p in prior_years) +
                    result.get('metadata', {}).get('tool_calls', 0)
                )
            },

            # Metadata
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'tool_calls_made': (
                    current_year.get('tool_calls_made', 0) +
                    sum(p.get('tool_calls_made', 0) for p in prior_years) +
                    result.get('metadata', {}).get('tool_calls', 0)
                ),
                'analysis_type': 'deep_dive_multi_year'
            }
        }

        logger.info(f"Synthesis complete: {final_result['decision']} with {final_result['conviction']} conviction")
        logger.info(
            f"Total tool calls: {final_result['metadata']['tool_calls_made']} "
            f"(current: {final_result['analysis_summary']['current_year_calls']}, "
            f"prior years: {final_result['analysis_summary']['prior_years_calls']}, "
            f"synthesis: {final_result['analysis_summary']['synthesis_calls']})"
        )

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

    def _extract_summary_section(self, response_text: str, year: int, ticker: str = None) -> str:
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
        Run provider-agnostic analysis loop.

        Each LLM provider implements its own native ReAct loop:
        - Claude: Extended Thinking + Native Tool Use API
        - Kimi: OpenAI-compatible tool calling
        - Others: Provider-specific implementation

        This makes the system truly plug-and-play - just set LLM_MODEL
        environment variable and basīrah uses the appropriate provider.

        Args:
            ticker: Stock ticker
            initial_message: Initial prompt to agent

        Returns:
            dict: Analysis results with decision and thesis
        """
        provider_info = self.llm.get_provider_info()
        provider_name = provider_info['provider']
        model_id = provider_info['model_id']

        logger.info(f"Using provider: {provider_name}")
        logger.info(f"Model: {model_id}")

        # Get the underlying provider instance
        provider = self.llm.provider

        # Get tool definitions in provider-specific format
        tool_definitions = self._get_tool_definitions()

        # Run provider's native ReAct loop
        logger.info(f"Running {provider_name} native ReAct loop...")

        result = provider.run_react_loop(
            system_prompt=self.system_prompt,
            initial_message=initial_message,
            tools=tool_definitions,
            tool_executor=self._execute_tool,  # Callback for tool execution
            max_iterations=self.MAX_ITERATIONS,
            max_tokens=self.MAX_TOKENS,
            thinking_budget=self.THINKING_BUDGET
        )

        if result["success"]:
            # Extract thesis
            thesis = result["thesis"]

            # Parse decision from thesis
            decision_data = self._parse_decision(ticker, thesis)

            # Merge metadata (ensure metadata key exists)
            if "metadata" not in decision_data:
                decision_data["metadata"] = {}
            decision_data["metadata"].update(result["metadata"])

            # Ensure tool_calls_made exists for backward compatibility
            # Provider returns "tool_calls" but rest of code expects "tool_calls_made"
            if "tool_calls" in decision_data["metadata"] and "tool_calls_made" not in decision_data["metadata"]:
                decision_data["metadata"]["tool_calls_made"] = decision_data["metadata"]["tool_calls"]

            logger.info(f"Analysis Complete - Decision: {decision_data.get('decision', 'UNKNOWN')}")

            return decision_data
        else:
            # Analysis failed
            logger.error(f"Analysis failed: {result['metadata'].get('error', 'Unknown error')}")

            return {
                "ticker": ticker,
                "decision": "ERROR",
                "conviction": "NONE",
                "thesis": result.get("thesis", "Analysis incomplete"),
                "intrinsic_value": None,
                "current_price": None,
                "margin_of_safety": None,
                "analysis_summary": {},
                "metadata": result.get("metadata", {})
            }

    def _execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Phase 7.7: Implements tool caching to avoid redundant API calls.
        Checks cache first, only executes if cache miss.

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

        # Phase 7.7: Check cache first
        cache_key = self._get_cache_key(tool_name, tool_input)
        cached_result = self._get_from_cache(tool_name, cache_key)

        if cached_result is not None:
            self.cache_hits += 1
            logger.info(f"[CACHE HIT] Using cached result for {tool_name} ({self.cache_hits} hits, {self.cache_misses} misses)")
            logger.debug(f"Cache key: {cache_key}")
            return cached_result

        # Cache miss - execute tool
        self.cache_misses += 1
        tool = self.tools[tool_key]

        logger.info(f"[CACHE MISS] Executing {tool_name} ({self.cache_hits} hits, {self.cache_misses} misses)")
        logger.debug(f"Parameters: {tool_input}")

        try:
            result = tool.execute(**tool_input)
            logger.info(f"{tool_name} {'succeeded' if result.get('success') else 'failed'}")

            if not result.get("success"):
                logger.warning(f"Tool error: {result.get('error')}")

            # Phase 7.7: Cache the result (even failures, to avoid retrying)
            self._store_in_cache(tool_name, cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
            error_result = {
                "success": False,
                "error": f"Tool execution exception: {str(e)}",
                "data": None
            }
            # Don't cache exceptions (may be transient)
            return error_result

    def _get_cache_key(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Generate cache key from tool name and parameters.

        Phase 7.7: Creates unique keys for caching tool results.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            str: Cache key

        Examples:
            gurufocus_tool(ticker=AOS, endpoint=summary) -> "AOS_summary"
            sec_filing_tool(ticker=AOS, filing_type=10-K, year=2024) -> "AOS_10-K_2024_full"
        """
        if tool_name == "gurufocus_tool":
            ticker = tool_input.get("ticker", "")
            endpoint = tool_input.get("endpoint", "")
            return f"{ticker}_{endpoint}"

        elif tool_name == "sec_filing_tool":
            ticker = tool_input.get("ticker", "")
            filing_type = tool_input.get("filing_type", "")
            year = tool_input.get("year", "")
            section = tool_input.get("section", "full")
            return f"{ticker}_{filing_type}_{year}_{section}"

        elif tool_name == "calculator_tool":
            # Calculator results depend on input data, so include calculation type
            calc_type = tool_input.get("calculation", "")
            # Use first 50 chars of data as part of key (hash would be better but less readable)
            data_str = str(tool_input.get("data", ""))[:50]
            return f"calc_{calc_type}_{hash(data_str)}"

        elif tool_name == "web_search_tool":
            query = tool_input.get("query", "")
            # Use first 80 chars of query as key
            return f"search_{query[:80]}"

        else:
            # Default: hash of tool name + parameters
            return f"{tool_name}_{hash(str(tool_input))}"

    def _get_from_cache(self, tool_name: str, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached tool result if available.

        Phase 7.7: Checks cache for previously executed tool calls.

        Args:
            tool_name: Name of the tool
            cache_key: Cache key

        Returns:
            Cached result dict or None if not found
        """
        # Map tool names to cache buckets
        cache_bucket_map = {
            "gurufocus_tool": "gurufocus",
            "sec_filing_tool": "sec",
            "web_search_tool": "web_search",
            "calculator_tool": "calculator"
        }

        bucket = cache_bucket_map.get(tool_name)
        if not bucket or bucket not in self.tool_cache:
            return None

        return self.tool_cache[bucket].get(cache_key)

    def _store_in_cache(self, tool_name: str, cache_key: str, result: Dict[str, Any]):
        """
        Store tool result in cache.

        Phase 7.7: Caches tool results to avoid redundant API calls.

        Args:
            tool_name: Name of the tool
            cache_key: Cache key
            result: Tool execution result
        """
        # Map tool names to cache buckets
        cache_bucket_map = {
            "gurufocus_tool": "gurufocus",
            "sec_filing_tool": "sec",
            "web_search_tool": "web_search",
            "calculator_tool": "calculator"
        }

        bucket = cache_bucket_map.get(tool_name)
        if not bucket:
            logger.warning(f"No cache bucket for {tool_name}, creating on-the-fly")
            bucket = tool_name
            if bucket not in self.tool_cache:
                self.tool_cache[bucket] = {}

        self.tool_cache[bucket][cache_key] = result
        logger.debug(f"[CACHE STORE] Cached {tool_name} result with key: {cache_key}")

    def _get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for analysis performance monitoring.

        Phase 7.7: Provides insights into cache efficiency.

        Returns:
            dict: Cache statistics
        """
        total_calls = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_calls * 100) if total_calls > 0 else 0

        # Count cached items per tool
        cached_items = {
            bucket: len(items)
            for bucket, items in self.tool_cache.items()
        }

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_calls": total_calls,
            "hit_rate_percent": round(hit_rate, 1),
            "cached_items_by_tool": cached_items,
            "total_cached_items": sum(cached_items.values())
        }

    def _warm_cache_for_synthesis(self, ticker: str, current_year: int = None) -> None:
        """
        Phase 7.7: Pre-fetch data that synthesis commonly needs to maximize cache hits.

        Based on analysis of synthesis patterns, this pre-warms the cache with:
        - GuruFocus: financials, keyratios, valuation (in addition to summary)
        - SEC: financial_statements section (most commonly requested)

        This significantly improves cache hit rate in synthesis stage from ~17% to ~40%+.

        Args:
            ticker: Stock ticker symbol
            current_year: Current fiscal year (for SEC filing)
        """
        logger.info("[CACHE WARMING] Pre-fetching data for synthesis stage...")
        items_prefetched = 0

        # 1. GuruFocus endpoints (if not already cached)
        gurufocus_endpoints = ["financials", "keyratios", "valuation"]
        for endpoint in gurufocus_endpoints:
            cache_key = f"{ticker}_{endpoint}"
            if self._get_from_cache("gurufocus_tool", cache_key) is None:
                try:
                    tool_input = {"ticker": ticker, "endpoint": endpoint}
                    result = self._execute_tool("gurufocus_tool", tool_input)
                    # Fix: GuruFocus tool returns "success": True, not "status": "success"
                    if result.get("success"):
                        items_prefetched += 1
                        logger.info(f"  [PREFETCH] Cached gurufocus {endpoint}")
                except Exception as e:
                    logger.warning(f"  [PREFETCH] Failed to cache gurufocus {endpoint}: {e}")

        # 2. SEC filing sections (if not already cached)
        if current_year:
            sec_sections = ["financial_statements", "risk_factors", "mda"]
            for section in sec_sections:
                cache_key = f"{ticker}_10-K_{current_year}_{section}"
                if self._get_from_cache("sec_filing_tool", cache_key) is None:
                    try:
                        tool_input = {
                            "ticker": ticker,
                            "filing_type": "10-K",
                            "year": current_year,
                            "section": section
                        }
                        result = self._execute_tool("sec_filing_tool", tool_input)
                        # Fix: SEC tool returns "success": True, not "status": "success"
                        if result.get("success"):
                            items_prefetched += 1
                            logger.info(f"  [PREFETCH] Cached SEC {section} section")
                    except Exception as e:
                        logger.warning(f"  [PREFETCH] Failed to cache SEC {section}: {e}")

        logger.info(f"[CACHE WARMING] Pre-fetched {items_prefetched} items for synthesis")
        logger.info(f"[CACHE WARMING] Total cached items: {sum(len(items) for items in self.tool_cache.values())}")

    def _fetch_verified_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        Phase 7.8: Pre-fetch verified GuruFocus metrics BEFORE analysis begins.

        This solves the decision consistency problem by ensuring the analyst
        has access to verified quantitative data from the start, so decisions
        are based on correct data rather than LLM extractions that get
        corrected later.

        Returns verified metrics including:
        - ROIC (from keyratios)
        - Revenue (from financials)
        - Owner Earnings (calculated from verified components)
        - Operating Margin (from keyratios)
        - Debt/Equity (from keyratios)
        - Net Income, D&A, CapEx, Working Capital Change (for Owner Earnings)

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with verified metrics, or None values if data unavailable
        """
        logger.info(f"[PHASE 7.8] Pre-fetching verified metrics for {ticker}...")

        verified_metrics = {
            "roic": None,
            "revenue": None,
            "owner_earnings": None,
            "operating_margin": None,
            "debt_equity": None,
            "net_income": None,
            "depreciation_amortization": None,
            "capex": None,
            "working_capital_change": None,
            "free_cash_flow": None,
            "source": "GuruFocus (verified external data)"
        }

        try:
            # Fetch GuruFocus data
            logger.info("[VERIFIED METRICS] Fetching GuruFocus financials...")
            financials_result = self._execute_tool("gurufocus_tool", {
                "ticker": ticker,
                "endpoint": "financials"
            })

            logger.info("[VERIFIED METRICS] Fetching GuruFocus keyratios...")
            keyratios_result = self._execute_tool("gurufocus_tool", {
                "ticker": ticker,
                "endpoint": "keyratios"
            })

            # Extract from financials
            # NOTE: GuruFocus tool returns data["financials"] with FLOAT values (already most recent)
            if financials_result and financials_result.get("success"):
                data = financials_result.get("data", {})
                financials = data.get("financials", {})

                # Extract values (these are floats, not arrays!)
                verified_metrics["revenue"] = financials.get("revenue")
                verified_metrics["net_income"] = financials.get("net_income")
                verified_metrics["depreciation_amortization"] = financials.get("depreciation_amortization")
                verified_metrics["free_cash_flow"] = financials.get("free_cash_flow")

                # CapEx (make positive if negative)
                capex = financials.get("capex")
                if capex is not None and capex < 0:
                    capex = abs(capex)
                verified_metrics["capex"] = capex

                # Working capital change
                verified_metrics["working_capital_change"] = financials.get("working_capital_change")

                # Calculate Owner Earnings if components available
                ni = verified_metrics["net_income"]
                da = verified_metrics["depreciation_amortization"]
                cx = verified_metrics["capex"]
                wc = verified_metrics["working_capital_change"] or 0

                if all(v is not None for v in [ni, da, cx]):
                    owner_earnings = ni + da - cx - wc
                    verified_metrics["owner_earnings"] = owner_earnings
                    logger.info(f"[VERIFIED METRICS] Calculated Owner Earnings: ${owner_earnings:,.0f}M")
                elif verified_metrics["free_cash_flow"]:
                    # Fallback to FCF
                    verified_metrics["owner_earnings"] = verified_metrics["free_cash_flow"]
                    logger.info(f"[VERIFIED METRICS] Using FCF as Owner Earnings: ${verified_metrics['free_cash_flow']:,.0f}M")

            # Extract from keyratios
            # NOTE: GuruFocus keyratios endpoint returns data["metrics"], NOT data["keyratios"]!
            if keyratios_result and keyratios_result.get("success"):
                data = keyratios_result.get("data", {})
                metrics = data.get("metrics", {})  # Use "metrics", not "keyratios"!

                # Extract values (these are floats, not arrays!)
                verified_metrics["roic"] = metrics.get("roic")
                verified_metrics["operating_margin"] = metrics.get("operating_margin")
                verified_metrics["debt_equity"] = metrics.get("debt_to_equity")  # May be None

            # Log what we got
            metrics_found = sum(1 for k, v in verified_metrics.items() if v is not None and k != "source")
            logger.info(f"[VERIFIED METRICS] Successfully fetched {metrics_found} metrics from GuruFocus")

            # Log key metrics
            if verified_metrics["roic"]:
                logger.info(f"  ROIC: {verified_metrics['roic']*100:.1f}%")
            if verified_metrics["revenue"]:
                logger.info(f"  Revenue: ${verified_metrics['revenue']:,.0f}M")
            if verified_metrics["owner_earnings"]:
                logger.info(f"  Owner Earnings: ${verified_metrics['owner_earnings']:,.0f}M")
            if verified_metrics["operating_margin"]:
                logger.info(f"  Operating Margin: {verified_metrics['operating_margin']*100:.1f}%")
            if verified_metrics["debt_equity"]:
                logger.info(f"  Debt/Equity: {verified_metrics['debt_equity']:.2f}")

            return verified_metrics

        except Exception as e:
            logger.error(f"[VERIFIED METRICS] Error fetching verified metrics: {e}", exc_info=True)
            return verified_metrics  # Return with None values

    def _extract_year_specific_metrics(
        self,
        gf_financials_result: Dict[str, Any],
        target_year: int
    ) -> Optional[Dict[str, Any]]:
        """
        Extract metrics for a specific year from GuruFocus financials historical data.

        BUGFIX (2025-11-17): Enables year-specific extraction from historical arrays.

        Args:
            gf_financials_result: Cached GuruFocus financials result
            target_year: Year to extract (e.g., 2022)

        Returns:
            Dict with year-specific metrics, or None if year not found
        """
        if not gf_financials_result or not gf_financials_result.get("success"):
            return None

        data = gf_financials_result.get("data", {})
        financials = data.get("financials", {})

        # Check if we have fiscal periods and historical data
        fiscal_periods = financials.get("fiscal_periods", [])
        historical = financials.get("historical", {})

        if not fiscal_periods or not historical:
            logger.warning(f"[METRICS] No historical data available for year {target_year}")
            return None

        # Find year index
        # BUGFIX (2025-11-17): fiscal_periods contain strings like '2023-12'
        # Need to match by year part only
        year_index = None
        for i, period in enumerate(fiscal_periods):
            period_year = int(period.split('-')[0]) if isinstance(period, str) and '-' in period else period
            if period_year == target_year:
                year_index = i
                logger.info(f"[METRICS] Found year {target_year} at index {year_index} (period: {period})")
                break

        if year_index is None:
            logger.warning(f"[METRICS] Year {target_year} not found in fiscal_periods: {fiscal_periods[:3]}...")
            return None

        # Extract values from historical arrays at the year index
        year_metrics = {}
        for key, values_array in historical.items():
            if isinstance(values_array, list) and len(values_array) > year_index:
                year_metrics[key] = values_array[year_index]

        logger.info(f"[METRICS] Extracted {len(year_metrics)} historical metrics for year {target_year}")
        return year_metrics

    def _extract_metrics_from_cache(self, ticker: str, year: int) -> Dict[str, Any]:
        """
        Phase 7.7 Phase 2: Extract structured metrics from tool cache.

        Extracts quantitative metrics from cached tool outputs (GuruFocus, Calculator, SEC)
        and returns them as a structured dictionary.

        Args:
            ticker: Stock ticker
            year: Fiscal year

        Returns:
            Dictionary with extracted metrics (compatible with AnalysisMetrics structure)
        """
        from src.agent.data_extractor import (
            extract_gurufocus_metrics,
            extract_calculator_metrics,
            merge_metrics
        )

        logger.info(f"[METRICS] Extracting structured metrics for {ticker} ({year})")

        # Get GuruFocus data from cache
        gf_summary = self._get_from_cache("gurufocus_tool", f"{ticker}_summary")
        gf_financials = self._get_from_cache("gurufocus_tool", f"{ticker}_financials")
        gf_keyratios = self._get_from_cache("gurufocus_tool", f"{ticker}_keyratios")
        gf_valuation = self._get_from_cache("gurufocus_tool", f"{ticker}_valuation")

        # BUGFIX (2025-11-17): Check if this is a historical year request
        # GuruFocus financials endpoint has 10 years of historical data in arrays
        # For historical years, we need to extract from those arrays instead of scalar values
        is_historical_year = False
        historical_metrics = None

        if gf_financials and gf_financials.get("success"):
            data = gf_financials.get("data", {})
            financials = data.get("financials", {})
            fiscal_periods = financials.get("fiscal_periods", [])

            # DEBUG: Log cache structure
            logger.info(f"[DEBUG] year parameter: {year} (type: {type(year).__name__})")
            logger.info(f"[DEBUG] gf_financials keys: {list(gf_financials.keys()) if gf_financials else 'None'}")
            logger.info(f"[DEBUG] data keys: {list(data.keys()) if data else 'None'}")
            logger.info(f"[DEBUG] financials keys: {list(financials.keys()) if financials else 'None'}")
            logger.info(f"[DEBUG] fiscal_periods (first 3): {fiscal_periods[:3] if len(fiscal_periods) >= 3 else fiscal_periods}")
            logger.info(f"[DEBUG] fiscal_periods (last 3): {fiscal_periods[-3:] if len(fiscal_periods) >= 3 else fiscal_periods}")
            logger.info(f"[DEBUG] fiscal_periods length: {len(fiscal_periods)}")

            # Check if requested year is NOT the most recent year
            if fiscal_periods and len(fiscal_periods) > 0:
                # BUGFIX (2025-11-17): fiscal_periods contain strings like '2024-12'
                # BUGFIX (2025-11-17): List is in ASCENDING order - most recent is LAST element
                # BUGFIX (2025-11-17): Skip 'TTM' (Trailing Twelve Months) entries
                # Need to extract just the year part and convert to int
                most_recent_period = None
                for period in reversed(fiscal_periods):
                    if isinstance(period, str) and period != 'TTM' and '-' in period:
                        most_recent_period = period
                        break

                if not most_recent_period:
                    logger.warning(f"[METRICS] No valid fiscal period found in: {fiscal_periods}")
                else:
                    most_recent_year = int(most_recent_period.split('-')[0])

                    logger.info(f"[DEBUG] most_recent_period: {most_recent_period}, most_recent_year: {most_recent_year} (type: {type(most_recent_year).__name__})")
                    logger.info(f"[DEBUG] Comparison: {year} != {most_recent_year} = {year != most_recent_year}")

                    if year != most_recent_year:
                        is_historical_year = True
                        logger.info(f"[METRICS] Historical year detected: {year} (most recent: {most_recent_year})")
                        historical_metrics = self._extract_year_specific_metrics(gf_financials, year)
                    else:
                        logger.info(f"[METRICS] Current year match: {year} == {most_recent_year}")

        # Extract metrics from GuruFocus data
        # Note: GuruFocus tool already processes data into clean metrics/financials/valuation dicts
        # For current year: aggregate from all endpoints
        # For historical year: use historical arrays from financials endpoint only
        gf_metrics = None
        if any([gf_summary, gf_financials, gf_keyratios, gf_valuation]):
            try:
                from src.agent.data_structures import AnalysisMetrics
                gf_metrics = AnalysisMetrics()
                metrics_count = 0

                # BUGFIX (2025-11-17): Use historical metrics for prior years
                if is_historical_year and historical_metrics:
                    # For historical years, populate from extracted historical arrays
                    logger.info(f"[METRICS] Using historical data for year {year}")
                    for key, value in historical_metrics.items():
                        if value is not None and hasattr(gf_metrics, key):
                            setattr(gf_metrics, key, value)
                            metrics_count += 1
                    logger.info(f"[METRICS] Extracted {metrics_count} historical metrics")
                else:
                    # For current year, aggregate metrics from all GF endpoints
                    logger.info(f"[METRICS] Using current year data from all endpoints")

                    # Aggregate metrics from all GF endpoints
                    for result in [gf_summary, gf_financials, gf_keyratios, gf_valuation]:
                        if result and result.get("success"):
                            data = result.get("data", {})

                            # Extract from processed fields (metrics, financials, valuation)
                            for field_name in ["metrics", "financials", "valuation"]:
                                if field_name in data and data[field_name]:
                                    for key, value in data[field_name].items():
                                        if value is not None and hasattr(gf_metrics, key):
                                            setattr(gf_metrics, key, value)
                                            metrics_count += 1

                            # ALSO extract from raw_data -> company_data (GuruFocus API structure)
                            # This has all the actual metrics like roic, roe, roa, pe, pb, etc.
                            if "raw_data" in data and data["raw_data"]:
                                raw = data["raw_data"]
                                if isinstance(raw, dict) and "company_data" in raw:
                                    company_data = raw["company_data"]
                                    # Map common GuruFocus field names to AnalysisMetrics fields
                                    field_mappings = {
                                        "roic": "roic",
                                        "roe": "roe",
                                        "roa": "roa",
                                        "pe": "pe_ratio",
                                        "pb": "pb_ratio",
                                        "sales": "revenue",
                                        "asset": "total_assets",
                                        "cash": "cash_and_equivalents",
                                        "oprt_margain": "operating_margin",  # Note: typo in GF API
                                        "net_margain": "net_margin",  # Note: typo in GF API
                                        "grossmargin": "gross_margin",
                                        "debt2equity": "debt_equity",
                                        "interest_coverage": "interest_coverage",
                                    }
                                    for gf_key, metrics_key in field_mappings.items():
                                        if gf_key in company_data:
                                            # Safe float conversion
                                            raw_value = company_data[gf_key]
                                            try:
                                                value = float(raw_value) if raw_value not in [None, "", "N/A"] else None
                                            except (ValueError, TypeError):
                                                value = None

                                            if value is not None:
                                                setattr(gf_metrics, metrics_key, value)
                                                metrics_count += 1

                    logger.info(f"[METRICS] Extracted {len([k for k, v in gf_metrics.model_dump(exclude_none=True).items()])} GuruFocus metrics")
            except Exception as e:
                logger.warning(f"[METRICS] Failed to extract GuruFocus metrics: {e}")
                gf_metrics = None

        # Get calculator outputs from cache
        # BUGFIX Phase 7.7 (2025-11-18): Don't assign same result to all calc_types
        # Match calculator results by their actual calculation type
        calc_outputs = {}
        for cache_key, result in self.tool_cache["calculator"].items():
            if not result or not result.get("success"):
                continue

            data = result.get("data", {})
            if not data:
                continue

            # Identify calculation type by distinctive fields
            # Owner Earnings: has 'operating_cash_flow' and 'capex' inputs
            if "operating_cash_flow" in data or "ocf" in data:
                if "owner_earnings" not in calc_outputs:
                    calc_outputs["owner_earnings"] = data

            # ROIC: has 'nopat' or 'invested_capital'
            elif "nopat" in data or "invested_capital" in data:
                if "roic" not in calc_outputs:
                    calc_outputs["roic"] = data

            # DCF: has 'intrinsic_value' and 'growth_rate'
            elif "intrinsic_value" in data and "growth_rate" in data:
                if "dcf" not in calc_outputs:
                    calc_outputs["dcf"] = data

            # Margin of Safety: has 'intrinsic_value' and 'current_price' but NOT 'growth_rate'
            elif "intrinsic_value" in data and "current_price" in data:
                if "margin_of_safety" not in calc_outputs:
                    calc_outputs["margin_of_safety"] = data

        # Extract metrics from calculator data
        calc_metrics = None
        if calc_outputs:
            try:
                calc_metrics = extract_calculator_metrics(calc_outputs)
                logger.info(f"[METRICS] Extracted {len([k for k, v in calc_metrics.model_dump(exclude_none=True).items()])} calculator metrics")
            except Exception as e:
                logger.warning(f"[METRICS] Failed to extract calculator metrics: {e}")
                calc_metrics = None

        # Merge metrics from all sources
        if gf_metrics and calc_metrics:
            combined = merge_metrics(gf_metrics, calc_metrics)
        elif gf_metrics:
            combined = gf_metrics
        elif calc_metrics:
            combined = calc_metrics
        else:
            # Return empty metrics if nothing extracted
            from src.agent.data_structures import AnalysisMetrics
            combined = AnalysisMetrics()

        metrics_dict = combined.model_dump(exclude_none=True)
        logger.info(f"[METRICS] Total metrics extracted: {len(metrics_dict)}")

        return metrics_dict

    def _extract_insights_from_analysis(
        self,
        ticker: str,
        year: int,
        analysis_text: str
    ) -> Dict[str, Any]:
        """
        Extract qualitative insights from analysis text.

        Phase 7.7 Phase 3.2: Tries JSON extraction first, falls back to text parsing.

        Args:
            ticker: Stock ticker symbol
            year: Fiscal year being analyzed
            analysis_text: Full analysis text from LLM

        Returns:
            Dictionary of AnalysisInsights fields
        """
        from src.agent.data_structures import AnalysisInsights
        import re
        import json

        logger.info(f"[INSIGHTS] Extracting structured insights for {ticker} ({year})")

        insights = AnalysisInsights()

        # Phase 7.7 Phase 3.2: Try JSON extraction first
        try:
            # Look for <INSIGHTS>...</INSIGHTS> block
            json_match = re.search(r'<INSIGHTS>\s*(\{.*?\})\s*</INSIGHTS>', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    insights_json = json.loads(json_str)
                    logger.info(f"[INSIGHTS] Successfully extracted JSON insights")

                    # Validate and populate insights from JSON
                    if "decision" in insights_json:
                        insights.decision = insights_json["decision"].upper()
                    if "conviction" in insights_json:
                        insights.conviction = insights_json["conviction"].upper()
                    if "moat_rating" in insights_json:
                        insights.moat_rating = insights_json["moat_rating"].upper()
                    if "risk_rating" in insights_json:
                        insights.risk_rating = insights_json["risk_rating"].upper()
                    if "primary_risks" in insights_json and isinstance(insights_json["primary_risks"], list):
                        # BUGFIX: Pydantic max_length=8, truncate if needed
                        insights.primary_risks = insights_json["primary_risks"][:8]
                    if "moat_sources" in insights_json and isinstance(insights_json["moat_sources"], list):
                        # BUGFIX: Pydantic max_length=10, truncate if needed
                        insights.moat_sources = insights_json["moat_sources"][:10]
                    if "business_model" in insights_json:
                        insights.business_model = insights_json["business_model"]
                    if "management_assessment" in insights_json:
                        insights.management_assessment = insights_json["management_assessment"]
                    if "decision_reasoning" in insights_json:
                        insights.decision_reasoning = insights_json["decision_reasoning"]
                    if "integrity_evidence" in insights_json:
                        # BUGFIX: Pydantic expects List[str], but LLM might return string
                        evidence = insights_json["integrity_evidence"]
                        if isinstance(evidence, str):
                            # Convert string to list (split by common delimiters)
                            insights.integrity_evidence = [evidence] if evidence.strip() else []
                        elif isinstance(evidence, list):
                            insights.integrity_evidence = evidence[:8]  # max_length=8
                    if "red_flags" in insights_json and isinstance(insights_json["red_flags"], list):
                        # BUGFIX: Pydantic max_length=8, truncate if needed
                        insights.red_flags = insights_json["red_flags"][:8]
                    if "discount_rate_reasoning" in insights_json:
                        insights.discount_rate_reasoning = insights_json["discount_rate_reasoning"]

                    # Count extracted insights
                    insights_dict = insights.model_dump(exclude_none=True)
                    insights_count = len([v for v in insights_dict.values() if v])
                    logger.info(f"[INSIGHTS] JSON extraction: {insights_count} insights for {ticker} ({year})")

                    return insights_dict

                except json.JSONDecodeError as e:
                    logger.warning(f"[INSIGHTS] JSON parsing failed: {e}. Falling back to text parsing.")
            else:
                logger.info(f"[INSIGHTS] No <INSIGHTS> JSON block found. Using text parsing.")

        except Exception as e:
            logger.warning(f"[INSIGHTS] JSON extraction error: {e}. Falling back to text parsing.")

        # Phase 7.7 Phase 3.1: Fallback to text parsing
        try:
            # Extract decision (BUY/WATCH/AVOID)
            decision_patterns = [
                r'(?:Decision|Recommendation|Final Decision):\s*(BUY|WATCH|AVOID)',
                r'(?:I recommend|Recommendation is):\s*(BUY|WATCH|AVOID)',
                r'\*\*Decision\*\*:\s*(BUY|WATCH|AVOID)'
            ]
            for pattern in decision_patterns:
                match = re.search(pattern, analysis_text, re.IGNORECASE)
                if match:
                    insights.decision = match.group(1).upper()
                    break

            # Extract conviction (HIGH/MODERATE/LOW)
            conviction_patterns = [
                r'(?:Conviction|Confidence):\s*(HIGH|MODERATE|LOW)',
                r'\*\*Conviction\*\*:\s*(HIGH|MODERATE|LOW)'
            ]
            for pattern in conviction_patterns:
                match = re.search(pattern, analysis_text, re.IGNORECASE)
                if match:
                    insights.conviction = match.group(1).upper()
                    break

            # Extract moat rating (DOMINANT/STRONG/MODERATE/WEAK)
            moat_patterns = [
                r'(?:Economic Moat|Moat Rating|Moat Strength):\s*(DOMINANT|STRONG|MODERATE|WEAK)',
                r'\*\*(?:Economic Moat|Moat)\*\*:\s*(DOMINANT|STRONG|MODERATE|WEAK)'
            ]
            for pattern in moat_patterns:
                match = re.search(pattern, analysis_text, re.IGNORECASE)
                if match:
                    insights.moat_rating = match.group(1).upper()
                    break

            # Extract risk rating (LOW/MODERATE/HIGH)
            risk_patterns = [
                r'(?:Risk Level|Risk Assessment|Risk Rating):\s*(LOW|MODERATE|HIGH)',
                r'\*\*(?:Risk Level|Risk)\*\*:\s*(LOW|MODERATE|HIGH)'
            ]
            for pattern in risk_patterns:
                match = re.search(pattern, analysis_text, re.IGNORECASE)
                if match:
                    insights.risk_rating = match.group(1).upper()
                    break

            # Extract primary risks (list)
            risk_list_headers = [
                r'(?:Key Risks|Primary Risks|Main Risks|Risk Factors):',
                r'\*\*(?:Key Risks|Risks)\*\*:'
            ]
            for header_pattern in risk_list_headers:
                risks = self._extract_bullet_list(analysis_text, header_pattern)
                if risks:
                    insights.primary_risks = risks
                    break

            # Extract moat sources (list)
            moat_list_headers = [
                r'(?:Moat Sources|Sources of Moat|Competitive Advantages):',
                r'\*\*(?:Moat Sources|Competitive Advantages)\*\*:'
            ]
            for header_pattern in moat_list_headers:
                moat_sources = self._extract_bullet_list(analysis_text, header_pattern)
                if moat_sources:
                    insights.moat_sources = moat_sources
                    break

            # Extract business model (first paragraph after header)
            business_model = self._extract_section_text(analysis_text, r'(?:Business Model|How the Business Works):')
            if business_model:
                insights.business_model = business_model

            # Extract management assessment
            mgmt_assessment = self._extract_section_text(analysis_text, r'(?:Management Quality|Management Assessment|Management):')
            if mgmt_assessment:
                insights.management_assessment = mgmt_assessment

            # Extract decision reasoning
            decision_reasoning = self._extract_section_text(analysis_text, r'(?:Decision Rationale|Why|Reasoning):')
            if decision_reasoning:
                insights.decision_reasoning = decision_reasoning

        except Exception as e:
            logger.warning(f"[INSIGHTS] Error during extraction: {e}")

        # Count extracted insights
        insights_dict = insights.model_dump(exclude_none=True)
        insights_count = len([v for v in insights_dict.values() if v])
        logger.info(f"[INSIGHTS] Extracted {insights_count} insights for {ticker} ({year})")

        return insights_dict

    def _extract_bullet_list(self, text: str, header_pattern: str) -> List[str]:
        """
        Extract bulleted list following a header.

        Args:
            text: Full text to search
            header_pattern: Regex pattern for section header

        Returns:
            List of bullet point items
        """
        import re

        # Find header
        header_match = re.search(header_pattern, text, re.IGNORECASE)
        if not header_match:
            return []

        # Extract text after header
        start = header_match.end()

        # Find next section header (typically starts with capital letter after blank line)
        # or end of text
        next_section = re.search(r'\n\n[A-Z#*]', text[start:])
        end = start + next_section.start() if next_section else len(text)
        section_text = text[start:end]

        # Extract bullet points (various formats: -, •, *, 1., etc.)
        bullets = re.findall(r'(?:^|\n)\s*[-•*]\s*(.+?)(?=\n|$)', section_text, re.MULTILINE)

        # Also try numbered lists
        if not bullets:
            bullets = re.findall(r'(?:^|\n)\s*\d+\.\s*(.+?)(?=\n|$)', section_text, re.MULTILINE)

        # Clean up and return
        return [b.strip() for b in bullets if b.strip()]

    def _extract_section_text(self, text: str, header_pattern: str, max_paragraphs: int = 2) -> str:
        """
        Extract text section following a header.

        Args:
            text: Full text to search
            header_pattern: Regex pattern for section header
            max_paragraphs: Maximum number of paragraphs to extract

        Returns:
            Extracted section text (first 1-2 paragraphs)
        """
        import re

        # Find header
        header_match = re.search(header_pattern, text, re.IGNORECASE)
        if not header_match:
            return ""

        # Extract text after header
        start = header_match.end()

        # Find next section header or end of text
        next_section = re.search(r'\n\n[A-Z#*]', text[start:])
        end = start + next_section.start() if next_section else len(text)
        section_text = text[start:end].strip()

        # Get first N paragraphs (split by double newline)
        paragraphs = section_text.split('\n\n')
        selected_paragraphs = paragraphs[:max_paragraphs]

        # Join and clean up
        result = '\n\n'.join(selected_paragraphs).strip()

        # Limit length to ~500 characters for storage
        if len(result) > 500:
            result = result[:497] + "..."

        return result

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
        # CRITICAL FIX: Prioritize explicit **DECISION:** format to avoid ambiguity
        decision_patterns = [
            # PRIORITY 1: Explicit bold markdown format (most reliable)
            (r'\*\*DECISION:\s*(BUY|WATCH|AVOID)\*\*', "explicit"),
            # PRIORITY 2: Standard format with colon
            (r'\b(?:DECISION|RECOMMENDATION|FINAL DECISION)\s*:\s*(BUY|WATCH|AVOID)\b', "standard"),
            # PRIORITY 3: Generic phrases (less reliable - only use if above not found)
            (r'\b(STRONG BUY|BUY RECOMMENDATION)\b', "phrase"),
            (r'\b(WATCHING|WATCH LIST|WAIT FOR BETTER PRICE)\b', "phrase"),
            (r'\b(AVOIDING|PASS ON THIS|TAKING A PASS)\b', "phrase"),
            (r"I'm\s+(backing up the truck|buying|investing)", "phrase"),
            (r"I'm\s+(passing|avoiding|taking a pass)", "phrase"),
            (r"I'm\s+(watching|waiting for a better price)", "phrase"),
        ]

        decision_source = None
        for pattern, source_type in decision_patterns:
            match = re.search(pattern, final_text, re.IGNORECASE)
            if match:
                matched_text = match.group(0).upper()
                # Extract explicit decision if pattern has capture group for BUY/WATCH/AVOID
                if re.search(r'\(BUY\|WATCH\|AVOID\)', pattern):
                    # Pattern has explicit capture group - use it directly
                    decision_value = match.group(1).upper()
                    decision_data["decision"] = decision_value
                    decision_source = source_type
                    logger.info(f"[DECISION PARSE] Extracted decision '{decision_value}' from {source_type} format")
                    break
                # Otherwise infer from matched text
                elif any(word in matched_text for word in ["BUY", "BACKING", "INVESTING"]):
                    decision_data["decision"] = "BUY"
                    decision_source = source_type
                    logger.info(f"[DECISION PARSE] Inferred decision 'BUY' from {source_type} format: '{matched_text[:50]}'")
                    break
                elif any(word in matched_text for word in ["WATCH", "WAIT", "WAITING"]):
                    decision_data["decision"] = "WATCH"
                    decision_source = source_type
                    logger.info(f"[DECISION PARSE] Inferred decision 'WATCH' from {source_type} format: '{matched_text[:50]}'")
                    break
                elif any(word in matched_text for word in ["AVOID", "PASS"]):
                    decision_data["decision"] = "AVOID"
                    decision_source = source_type
                    logger.info(f"[DECISION PARSE] Inferred decision 'AVOID' from {source_type} format: '{matched_text[:50]}'")
                    break

        # Cross-check with JSON insights if available
        json_match = re.search(r'<INSIGHTS>\s*(\{.*?\})\s*</INSIGHTS>', final_text, re.DOTALL)
        if json_match:
            try:
                import json
                insights_json = json.loads(json_match.group(1))
                json_decision = insights_json.get("decision", "").upper()
                if json_decision and json_decision != decision_data["decision"]:
                    logger.warning(f"[DECISION CONFLICT] Text decision '{decision_data['decision']}' (from {decision_source}) "
                                   f"differs from JSON decision '{json_decision}'. Using text decision (higher priority).")
            except json.JSONDecodeError:
                pass  # JSON parsing failed, ignore

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
        Extract numerical values (intrinsic value, price, margin of safety, owner earnings, roic) from text.

        Args:
            text: Text to parse

        Returns:
            dict: Extracted numerical values
        """
        values = {
            "intrinsic_value": None,
            "current_price": None,
            "margin_of_safety": None,
            "owner_earnings": None,
            "roic": None
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

        # Owner earnings patterns (in millions)
        oe_patterns = [
            r'\*\*OWNER\s+EARNINGS:\s*\$?\s*([\d,]+\.?\d*)\s*M\*\*',  # Bold markdown
            r'owner\s+earnings.*?\$?\s*([\d,]+\.?\d*)\s*(?:M|million)',
            r'owner\s+earnings.*?=\s*\$?\s*([\d,]+\.?\d*)\s*(?:M|million)',
            r'FCF.*?\$?\s*([\d,]+\.?\d*)\s*(?:M|million)',
            r'free\s+cash\s+flow.*?\$?\s*([\d,]+\.?\d*)\s*(?:M|million)'
        ]

        for pattern in oe_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    values["owner_earnings"] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue

        # ROIC patterns (as percentage)
        roic_patterns = [
            r'\*\*ROIC:\s*([\d]+\.?\d*)%\*\*',  # Bold markdown
            r'ROIC.*?([\d]+\.?\d*)%',
            r'return\s+on\s+invested\s+capital.*?([\d]+\.?\d*)%',
            r'ROIC\s*=\s*([\d]+\.?\d*)%'
        ]

        for pattern in roic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    values["roic"] = float(match.group(1)) / 100.0
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

Using the 8 core investment principles framework, please compare these companies:

1. Which has the widest moat?
2. Which has the best management?
3. Which has the best financial strength?
4. Which offers the best value (margin of safety)?
5. If you could only invest in one, which would it be and why?

Be specific and systematic in your analysis. It's okay to say "none of these"
if none meet the investment criteria.
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

    # =========================================================================
    # Phase 7.6B/C: Validation Methods
    # =========================================================================

    def _validate_with_auto_correction(
        self,
        result: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Validate analysis with single-pass auto-correction using cached data.

        Phase 7.7.8: Simplified validation - no iterative refinement loop.
        Just validate once and auto-correct using cached trusted data.

        Args:
            result: Analysis result to validate
            ticker: Stock ticker

        Returns:
            Analysis with validation results and auto-corrections applied
        """
        logger.info("Running single-pass validation with auto-correction...")

        # Step 1: Validate analysis
        critique = self._validate_analysis(result, iteration=0)
        score = critique.get("score", 0)
        issues = critique.get("issues", [])

        logger.info(f"Validation score: {score}/100")
        logger.info(f"Issues found: {len(issues)}")

        # Step 2: Apply auto-corrections using cached data
        if issues:
            logger.info("Applying auto-corrections using cached trusted data...")

            from src.agent.validator_corrections import apply_cached_corrections

            try:
                # Auto-correct using cached GuruFocus/SEC data
                result = apply_cached_corrections(
                    analysis=result,
                    validator_issues=issues,
                    tool_cache=self.tool_cache
                )

                corrections = result.get('metadata', {}).get('auto_corrections', {})
                total_corrections = corrections.get('total_corrections', 0)

                if total_corrections > 0:
                    logger.info(f"✅ Applied {total_corrections} auto-corrections")
                else:
                    logger.info("No auto-corrections applied (no cached data available)")

            except Exception as e:
                logger.error(f"Auto-correction failed: {e}", exc_info=True)

        # Step 3: Attach validation results
        result["validation"] = {
            "enabled": True,
            "approved": critique.get("approved", False),
            "score": score,
            "overall_assessment": critique.get("overall_assessment", ""),
            "strengths": critique.get("strengths", []),
            "issues": issues,
            "recommendation": critique.get("recommendation", "unknown")
        }

        # Log final status
        if critique.get("approved", False):
            logger.info(f"✅ Validation PASSED - Score: {score}/100")
        else:
            logger.warning(f"⚠️  Validation score: {score}/100 (threshold: {self.score_threshold})")
            logger.warning(f"   Issues remaining: {len(issues)}")

        return result

    def _format_munger_critique(self, validation: Dict[str, Any]) -> str:
        """
        Format validator critique as narrative "Charlie Munger's Critique" section.

        Phase 9.2: Present validation feedback using Munger's mental models framework
        as a visible narrative section at the end of the thesis.

        Args:
            validation: Validation results dict with score, issues, strengths, etc.

        Returns:
            Formatted markdown critique section
        """
        if not validation or not validation.get("enabled"):
            return ""

        critique_parts = []
        critique_parts.append("\n---\n")
        critique_parts.append("\n## Charlie Munger's Critique\n")
        critique_parts.append("\n*Applied systematic skepticism using mental models framework*\n")

        # Overall assessment
        overall = validation.get("overall_assessment", "")
        if overall:
            critique_parts.append(f"\n### Overall Assessment\n\n{overall}\n")

        # Validation score
        score = validation.get("score", 0)
        approved = validation.get("approved", False)
        status = "✅ **Approved**" if approved else "⚠️ **Needs Improvement**"
        critique_parts.append(f"\n### Validation Score: {score}/100 {status}\n")

        # Strengths (what the analysis did well)
        strengths = validation.get("strengths", [])
        if strengths:
            critique_parts.append("\n### Strengths\n")
            for i, strength in enumerate(strengths, 1):
                critique_parts.append(f"{i}. {strength}\n")

        # Issues identified (using Munger's mental models)
        issues = validation.get("issues", [])
        if issues:
            critique_parts.append("\n### Issues Identified (Mental Models Applied)\n")

            # Group issues by severity
            critical_issues = [i for i in issues if i.get("severity") == "critical"]
            important_issues = [i for i in issues if i.get("severity") == "important"]
            minor_issues = [i for i in issues if i.get("severity") == "minor"]

            if critical_issues:
                critique_parts.append("\n**Critical Issues:**\n")
                for i, issue in enumerate(critical_issues, 1):
                    desc = issue.get("description", "")
                    fix = issue.get("suggested_fix", "")
                    mental_model = issue.get("mental_model", issue.get("category", ""))

                    critique_parts.append(f"\n{i}. **{mental_model.title()}**: {desc}\n")
                    if fix:
                        critique_parts.append(f"   - *Recommended fix*: {fix}\n")

            if important_issues:
                critique_parts.append("\n**Important Issues:**\n")
                for i, issue in enumerate(important_issues, 1):
                    desc = issue.get("description", "")
                    fix = issue.get("suggested_fix", "")
                    mental_model = issue.get("mental_model", issue.get("category", ""))

                    critique_parts.append(f"\n{i}. **{mental_model.title()}**: {desc}\n")
                    if fix:
                        critique_parts.append(f"   - *Recommended fix*: {fix}\n")

            if minor_issues:
                critique_parts.append("\n**Minor Issues:**\n")
                for i, issue in enumerate(minor_issues, 1):
                    desc = issue.get("description", "")
                    mental_model = issue.get("mental_model", issue.get("category", ""))
                    critique_parts.append(f"{i}. **{mental_model.title()}**: {desc}\n")

        # Recommendation
        recommendation = validation.get("recommendation", "")
        if recommendation:
            critique_parts.append(f"\n### Recommendation\n\n{recommendation}\n")

        critique_parts.append("\n---\n")
        critique_parts.append("*This critique applies Charlie Munger's mental models: Inversion, Second-Order Thinking, ")
        critique_parts.append("Incentive-Caused Bias, Psychological Biases, Circle of Competence, and Margin of Safety.*\n")

        return "".join(critique_parts)

    def _validate_with_refinement_OLD_DEPRECATED(
        self,
        result: Dict[str, Any],
        ticker: str,
        max_refinements: int = 2,
        score_threshold: int = 80
    ) -> Dict[str, Any]:
        """
        OLD DEPRECATED METHOD - Iterative refinement approach.

        This method is no longer used. Kept for reference only.
        Use _validate_with_auto_correction instead.
        """
        refinement_history = []

        for iteration in range(max_refinements + 1):
            # Validate current analysis
            critique = self._validate_analysis(result, iteration)

            # Track validation attempt
            score = critique.get("score", 0)
            issues = critique.get("issues", [])

            if iteration == 0:
                logger.info(f"Initial validation score: {score}/100")
            else:
                logger.info(f"Refinement {iteration} validation score: {score}/100")

            # Store refinement history
            refinement_history.append({
                "iteration": iteration,
                "score": score,
                "issues_count": len(issues),
                "approved": critique.get("approved", False)
            })

            # Check if refinement needed
            if score >= score_threshold:
                logger.info(f"✅ Score {score}/100 meets threshold ({score_threshold}+)")
                break

            if iteration >= max_refinements:
                logger.warning(f"⚠️  Max refinements ({max_refinements}) reached at score {score}/100")
                break

            # Filter to fixable issues
            fixable_issues = self._filter_fixable_issues(issues)

            if not fixable_issues:
                logger.info(f"No fixable issues remaining (score: {score}/100)")
                break

            # Refine analysis - choose approach based on configuration
            use_validator_driven = os.getenv("USE_VALIDATOR_DRIVEN_REFINEMENT", "true").lower() == "true"

            if use_validator_driven:
                logger.info(f"🔧 Using validator-driven refinement to fix {len(fixable_issues)} issues...")

                try:
                    # NEW: Validator identifies AND fixes issues directly using tools
                    result = self._validator_driven_refinement(ticker, result, critique, iteration)

                except Exception as e:
                    logger.error(f"Validator-driven refinement {iteration} failed: {e}", exc_info=True)
                    logger.warning("Falling back to old refinement approach...")
                    try:
                        result = self._refine_analysis(result, critique, fixable_issues, ticker, iteration)
                    except Exception as e2:
                        logger.error(f"Fallback refinement also failed: {e2}", exc_info=True)
                        break
            else:
                logger.info(f"🔄 Using classic refinement approach (analyst-driven)")

                try:
                    # OLD: Analyst writes refinements, complex section merging
                    result = self._refine_analysis(result, critique, fixable_issues, ticker, iteration)

                except Exception as e:
                    logger.error(f"Refinement {iteration} failed: {e}", exc_info=True)
                    break

        # Attach final validation and refinement history
        result["validation"] = {
            "enabled": True,
            "approved": critique.get("approved", False),
            "score": critique.get("score", 0),
            "overall_assessment": critique.get("overall_assessment", ""),
            "strengths": critique.get("strengths", []),
            "issues": critique.get("issues", []),
            "recommendation": critique.get("recommendation", "unknown"),
            "refinements": len(refinement_history) - 1,  # Don't count initial validation
            "refinement_history": refinement_history
        }

        # Log final status
        final_score = critique.get("score", 0)
        if critique.get("approved", False):
            logger.info(f"✅ Validation PASSED - Final Score: {final_score}/100")
        else:
            logger.warning(f"⚠️  Validation FAILED - Final Score: {final_score}/100")
            logger.warning(f"   Issues remaining: {len(critique.get('issues', []))}")

            # Log critical issues
            for issue in critique.get('issues', []):
                if issue.get('severity') == 'critical':
                    logger.error(
                        f"   [CRITICAL] {issue.get('category', 'unknown')}: "
                        f"{issue.get('description', '')}"
                    )

        return result

    def _filter_fixable_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter issues to those that can be fixed through refinement.

        Fixable issues are those that can be addressed by:
        - Using tools (calculator, web_search, sec_filing)
        - Adding more detail or specificity
        - Showing calculation methodology
        - Better sourcing/citations

        Unfixable issues (skip these):
        - Data not available in sources
        - Fundamental business quality problems
        - Issues requiring external data not accessible

        Args:
            issues: List of validation issues

        Returns:
            List of fixable issues
        """
        fixable = []

        unfixable_keywords = [
            "data not available",
            "filing does not contain",
            "information not disclosed",
            "company does not report",
            "no public data",
            "fundamental business",
            "industry in decline"
        ]

        for issue in issues:
            description = issue.get("description", "").lower()
            category = issue.get("category", "").lower()

            # Check if issue is explicitly unfixable
            is_unfixable = any(keyword in description for keyword in unfixable_keywords)

            if is_unfixable:
                logger.debug(f"Skipping unfixable issue: {issue.get('issue', 'Unknown')}")
                continue

            # Prioritize critical and important issues
            if issue.get("severity") in ["critical", "important"]:
                fixable.append(issue)
            elif issue.get("severity") == "minor" and len(fixable) < 3:
                # Include minor issues if not too many critical/important ones
                fixable.append(issue)

        logger.info(f"Filtered {len(issues)} issues → {len(fixable)} fixable")
        return fixable

    def _extract_section_names(self, thesis: str) -> List[str]:
        """
        Extract section names from thesis for standardized refinement merging.

        Finds all major section headers in the thesis so the refinement agent
        can use EXACT names to ensure proper section replacement.

        Args:
            thesis: The investment thesis text

        Returns:
            List of section names found in the thesis
        """
        import re

        section_names = []

        # Pattern 1: Markdown headers (## Section Name)
        markdown_sections = re.findall(r'^##\s+(.+?)(?:\n|$)', thesis, re.MULTILINE)
        section_names.extend(markdown_sections)

        # Pattern 2: Bold headers (**Section Name:** or **Section Name**)
        bold_sections = re.findall(r'\*\*([^*]+?)(?::|(?:\*\*))', thesis)
        section_names.extend(bold_sections)

        # Clean and deduplicate
        cleaned = []
        seen = set()
        for name in section_names:
            clean_name = name.strip()
            # Filter out very short names (likely not section headers)
            if len(clean_name) > 3 and clean_name.lower() not in seen:
                cleaned.append(clean_name)
                seen.add(clean_name.lower())

        return cleaned

    def _refine_analysis(
        self,
        result: Dict[str, Any],
        critique: Dict[str, Any],
        fixable_issues: List[Dict[str, Any]],
        ticker: str,
        iteration: int
    ) -> Dict[str, Any]:
        """
        Refine analysis to address validator issues.

        Creates a targeted refinement prompt that:
        1. Shows the specific issues to fix
        2. Provides the current analysis context
        3. Gives access to tools for verification
        4. Instructs analyst to make surgical fixes

        Args:
            result: Current analysis result
            critique: Validation critique
            fixable_issues: Issues to address
            ticker: Stock ticker
            iteration: Current refinement iteration

        Returns:
            Refined analysis result
        """
        # Format issues for refinement prompt
        issues_text = self._format_issues_for_refinement(fixable_issues)

        # Get analysis context (truncate if too long)
        thesis = result.get("thesis", "")
        if len(thesis) > 15000:
            thesis_preview = thesis[:7500] + "\n\n[...middle section truncated...]\n\n" + thesis[-7500:]
        else:
            thesis_preview = thesis

        # Extract section names for standardized merging
        section_names = self._extract_section_names(thesis)
        section_list = "\n".join([f"   - {name}" for name in section_names])

        # Build refinement prompt
        refinement_prompt = f"""
**REFINEMENT TASK - Iteration {iteration}**

Your previous {ticker} analysis received a validation score of {critique['score']}/100.

The validator identified {len(fixable_issues)} issues that need to be addressed:

{issues_text}

**CURRENT ANALYSIS (for reference):**
```
{thesis_preview}
```

**YOUR TASK:**

Fix ONLY the specific issues listed above. For each issue:

1. **Use tools as needed:**
   - calculator_tool: For calculations (ROIC, DCF, Owner Earnings, Margin of Safety)
   - web_search_tool: For current prices, CEO changes, recent events
   - sec_filing_tool: For specific page numbers or sections
   - gurufocus_tool: For supplemental data

2. **Show your work:**
   - If adding calculations: Show formula, inputs, sources, step-by-step math
   - If adding citations: Include page numbers or specific sections
   - If researching CEO changes: Name both departing and replacement CEOs
   - If getting current price: Exact price with date, not ranges

3. **Output format - CRITICAL:**

   **SECTION NAMES FROM ORIGINAL ANALYSIS:**
{section_list}

   For each section you're fixing, use the EXACT section name from the list above.
   Use this format:

   **[Exact Section Name] - REFINEMENT:**
   [Complete replacement content for that section]

   ⚠️ IMPORTANT: Use the EXACT section name - do NOT add words like "Analysis", "Overview", etc.

   Example - If original has "Current Leadership", use:
   **[Current Leadership] - REFINEMENT:**  ← EXACT match
   NOT: **[Current Leadership Analysis] - REFINEMENT:**  ← Will fail to merge!

   Content:
   - CEO: Maziar Mike Doustdar (since August 7, 2025)
   - Previous CEO: Lars Jørgensen (stepped down May 2025 after 9 years)
   - Reason for change: Board decision following competitive pressure from Eli Lilly
   - New CEO background: Former EVP International Operations (2017-2025), strong emerging markets track record

   This will REPLACE the "Current Leadership" section in the original analysis.

4. **Important:**
   - Include the COMPLETE replacement section (not just what changed)
   - Use the EXACT section name from the list above (copy-paste to ensure match)
   - Fix ONLY the sections related to issues (don't rewrite everything)
   - Maintain Warren Buffett's voice and analytical style

**CRITICAL:**
- Address ALL {len(fixable_issues)} issues listed above
- Use tools to verify - don't just add text without data
- Show calculation methodology (formulas + inputs + sources)
- Be specific (exact prices, page numbers, names, dates)

Begin your refinement now:
"""

        logger.info(f"Running refinement iteration {iteration} for {ticker}")

        # Run refinement through analysis loop
        refinement_result = self._run_analysis_loop(ticker, refinement_prompt)

        # Merge refinement with original analysis
        # The refinement contains targeted fixes that need to replace corresponding sections

        refined_thesis = refinement_result.get("thesis", "")

        # Parse refinement into sections
        import re

        # Extract refinement sections (look for **[Section Name] - REFINEMENT:** pattern)
        refinement_pattern = r'\*\*\[(.*?)\]\s*-\s*REFINEMENT:\*\*\s*(.*?)(?=\*\*\[|$)'
        refinement_sections = re.findall(refinement_pattern, refined_thesis, re.DOTALL)

        if refinement_sections:
            # Section-level merge: Replace specific sections with refinements
            merged_thesis = thesis

            for section_name, section_content in refinement_sections:
                section_name_clean = section_name.strip()
                logger.info(f"Merging refinement for section: {section_name_clean}")

                # Find this section in original thesis and replace it
                # Look for section headers like **Current Leadership** or ## Management Quality
                section_patterns = [
                    rf'\*\*{re.escape(section_name_clean)}[:\s].*?\n(.*?)(?=\n\*\*[A-Z]|\n##|$)',
                    rf'##\s*{re.escape(section_name_clean)}.*?\n(.*?)(?=\n##|$)',
                    rf'{re.escape(section_name_clean)}[:\s].*?\n(.*?)(?=\n[A-Z]{{2,}}|$)'
                ]

                replaced = False
                for pattern in section_patterns:
                    if re.search(pattern, merged_thesis, re.DOTALL | re.IGNORECASE):
                        # Replace this section with refinement
                        merged_thesis = re.sub(
                            pattern,
                            f"**{section_name_clean}:**\n{section_content.strip()}\n",
                            merged_thesis,
                            count=1,
                            flags=re.DOTALL | re.IGNORECASE
                        )
                        replaced = True
                        logger.info(f"✓ Replaced section: {section_name_clean}")
                        break

                if not replaced:
                    # Section not found - append at end
                    logger.warning(f"⚠ Section '{section_name_clean}' not found in original - appending")
                    merged_thesis += f"\n\n**{section_name_clean} (ADDED):**\n{section_content.strip()}\n"

        elif "## REFINED ANALYSIS" in refined_thesis:
            # Fallback: Agent provided full rewrite - replace entire thesis
            logger.warning("⚠ Refinement is full rewrite (not section-based) - replacing entire thesis")
            merged_thesis = refined_thesis
        else:
            # No clear structure - keep original and note refinement attempt
            logger.warning("⚠ Refinement format unclear - keeping original thesis")
            merged_thesis = thesis + "\n\n---\n**Note:** Refinement attempted but format unclear.\n"

        # Update result with refined content
        result["thesis"] = merged_thesis

        # CRITICAL FIX: Re-parse decision from merged thesis instead of using refinement result
        # The refinement only outputs section-level fixes, not a complete decision
        # So we need to extract the decision from the merged thesis
        merged_decision_data = self._parse_decision(ticker, merged_thesis)

        # Only update decision/conviction if they were successfully extracted from merged thesis
        if merged_decision_data.get("decision") != "UNKNOWN":
            result["decision"] = merged_decision_data["decision"]
            logger.info(f"✓ Re-parsed decision from merged thesis: {result['decision']}")
        if merged_decision_data.get("conviction") != "UNKNOWN":
            result["conviction"] = merged_decision_data["conviction"]
            logger.info(f"✓ Re-parsed conviction from merged thesis: {result['conviction']}")

        # CRITICAL: Update numeric fields from refinement ONLY if they have non-None values
        # The validator checks consistency between narrative text and JSON metadata
        # Don't overwrite good values with None from section-level refinements
        numeric_fields = [
            "intrinsic_value",
            "margin_of_safety",
            "current_price",
            "roic",
            "owner_earnings",
            "debt_to_equity",
            "fcf_yield",
            "peg_ratio"
        ]

        for field in numeric_fields:
            # Check refinement result first (if it calculated new values)
            if field in refinement_result and refinement_result[field] is not None:
                old_value = result.get(field)
                new_value = refinement_result[field]
                if old_value != new_value:
                    logger.info(f"Updating {field} from refinement: {old_value} → {new_value}")
                    result[field] = new_value
            # Otherwise check merged thesis parsing (might have updated values in text)
            elif field in merged_decision_data and merged_decision_data[field] is not None:
                old_value = result.get(field)
                new_value = merged_decision_data[field]
                # Only update if it's different and not worse (None)
                if old_value != new_value and new_value is not None:
                    logger.info(f"Updating {field} from merged thesis: {old_value} → {new_value}")
                    result[field] = new_value
            # Otherwise preserve original value (don't set to None)

        # Update metadata
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["refinement_iteration"] = iteration
        result["metadata"]["issues_addressed"] = len(fixable_issues)

        # Merge tool call counts
        if "metadata" in refinement_result:
            result["metadata"]["refinement_tool_calls"] = result["metadata"].get("refinement_tool_calls", 0) + \
                                                           refinement_result["metadata"].get("tool_calls_made", 0)

        logger.info(f"Refinement iteration {iteration} complete")

        return result

    def _format_issues_for_refinement(self, issues: List[Dict[str, Any]]) -> str:
        """
        Format validation issues into refinement prompt text.

        Args:
            issues: List of issues to format

        Returns:
            Formatted issues text
        """
        formatted = []

        for i, issue in enumerate(issues, 1):
            severity = issue.get("severity", "unknown").upper()
            category = issue.get("category", "unknown")
            description = issue.get("description", "")
            suggestion = issue.get("suggestion", "")

            issue_text = f"""
**Issue {i} [{severity} - {category}]:**
Problem: {description}
"""
            if suggestion:
                issue_text += f"Suggested Fix: {suggestion}\n"

            formatted.append(issue_text)

        return "\n".join(formatted)

    def _validator_driven_refinement(
        self,
        ticker: str,
        result: Dict[str, Any],
        critique: Dict[str, Any],
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        NEW APPROACH: Validator identifies issues AND fixes them directly using tools.

        This is simpler and more deterministic than the old approach:
        - Old: Analyst writes → Validator critiques → Analyst refines → Complex merge
        - New: Analyst writes → Validator critiques AND fixes using tools → Done

        The validator has:
        - Access to calculator_tool for verifying math
        - Access to web_search for current data
        - Access to gurufocus_tool for financial metrics
        - The complete original thesis in context
        - Knowledge of exact issues to fix

        This produces higher quality, more deterministic output.

        Args:
            ticker: Stock ticker
            result: Original analysis result
            critique: Validator critique with issues
            iteration: Refinement iteration number

        Returns:
            Fixed analysis result
        """
        thesis = result.get("thesis", "")
        issues = critique.get("issues", [])

        # Filter to fixable issues only
        fixable_categories = ["calculations", "data", "sources", "methodology"]
        fixable_issues = [
            issue for issue in issues
            if issue.get("category") in fixable_categories
        ]

        if not fixable_issues:
            logger.info("No fixable issues found - returning original analysis")
            return result

        logger.info(f"🔧 Validator will fix {len(fixable_issues)} issues directly using tools...")

        # Build validator-fixer prompt
        issues_text = self._format_issues_for_refinement(fixable_issues)

        validator_prompt = f"""
**VALIDATOR-DRIVEN REFINEMENT**

You identified {len(fixable_issues)} issues in the {ticker} analysis. Now FIX them directly.

**YOUR TASK:**

For each issue below:

1. **Use tools to verify correct data (in order of preference):**

   a. **gurufocus_tool FIRST** - For all financial metrics:
      - Revenue, margins, ROIC, debt/equity, cash flow
      - Fast, concise, pre-computed metrics
      - Example: gurufocus_tool({{ticker: "{ticker}", data_type: "financials"}})

   b. **calculator_tool** - For all calculations:
      - ROIC, DCF, Owner Earnings, margin of safety formulas
      - Show formula + inputs + result
      - Example: calculator_tool({{operation: "roic", nopat: 10.5, invested_capital: 50.0}})

   c. **web_search** - For current data beyond knowledge cutoff:
      - Current stock price, recent CEO changes, news
      - Example: web_search({{query: "{ticker} current stock price 2025"}})

   d. **sec_filing_tool SPARINGLY** - ONLY when absolutely necessary:
      - Use ONLY to verify specific quotes or page citations
      - Request specific sections (NOT "full" filing - too large!)
      - DO NOT use to re-verify data already in GuruFocus
      - Example GOOD: sec_filing_tool({{ticker: "{ticker}", filing_type: "10-K", section: "risk_factors"}})
      - Example BAD: sec_filing_tool({{ticker: "{ticker}", filing_type: "10-K", section: "full"}}) ← TOO BIG!

2. **Find the exact text that needs fixing** in the ORIGINAL ANALYSIS below

3. **CRITICAL: Copy text EXACTLY** - Use Ctrl+C, Ctrl+V to copy the exact text from the ORIGINAL ANALYSIS.
   - DO NOT rephrase, paraphrase, or modify the text in any way
   - DO NOT change "Owner Earnings:" to "Owner Earnings Calculation:"
   - DO NOT add or remove spaces, newlines, or punctuation
   - The <FIND> block must match CHARACTER-FOR-CHARACTER what appears in the ORIGINAL ANALYSIS
   - If you can't find the exact text, search for a smaller substring that matches exactly

4. **Output a structured fix:**
   ```
   <FIX>
   <FIND>EXACT TEXT COPIED CHARACTER-FOR-CHARACTER FROM ORIGINAL ANALYSIS - NO CHANGES ALLOWED</FIND>
   <REPLACE>corrected text with tool-verified sources and calculations</REPLACE>
   <VERIFIED_WITH>tool_name: specific result from tool output</VERIFIED_WITH>
   </FIX>
   ```

**ISSUES TO FIX:**

{issues_text}

**ORIGINAL ANALYSIS (for reference):**
```
{thesis}
```

**CRITICAL RULES:**

1. **EXACT TEXT MATCHING IS MANDATORY** - The #1 cause of fix failures is paraphrasing the FIND text. Copy it EXACTLY from ORIGINAL ANALYSIS above.
2. **Use tools before fixing** - Don't just add text, verify with tools first
3. **Follow tool priority** - gurufocus first → calculator → web_search → sec_filing (only if absolutely needed)
4. **Show your work** - Include formulas, sources, page numbers in replacements
5. **Be surgical** - Fix only what's broken, don't rewrite entire sections
6. **Keep Buffett's voice** - Maintain the analytical, straightforward tone

**OUTPUT FORMAT:**

Output multiple <FIX> blocks, one for each issue.

At the very end, output:

**FINAL DECISION: [BUY|WATCH|AVOID]**
**FINAL CONVICTION: [HIGH|MODERATE|LOW]**

This ensures decision is properly captured.

Begin your validation and fixes now:
"""

        logger.info("Running validator with tool access to fix issues...")

        # Get validator tools
        validator_tools = self._get_validator_tool_definitions()

        # Run validator with tools (using validator's model)
        # Allow thinking for thinking models - generating fixes requires reasoning
        thinking_budget = 10000 if "thinking" in self.validator_llm.model_key.lower() else 0
        logger.info(f"Validator thinking budget: {thinking_budget} tokens (model: {self.validator_llm.model_key})")

        validator_result = self.validator_llm.provider.run_react_loop(
            system_prompt="You are a validator who fixes investment analysis issues using tools for verification. Be surgical and precise.",
            initial_message=validator_prompt,
            tools=validator_tools,
            tool_executor=self._execute_validator_tool,
            max_iterations=15,  # Allow multiple tool calls
            max_tokens=16000,
            thinking_budget=thinking_budget  # Allow thinking for thinking models
        )

        if not validator_result["success"]:
            logger.error("Validator-driven refinement failed - returning original")
            return result

        validator_output = validator_result["thesis"]

        # DEBUG: Log first 2000 chars of validator output to diagnose fix generation
        logger.debug(f"Validator output (first 2000 chars):\n{validator_output[:2000]}")

        # Parse fixes from validator output
        fixes = self._parse_validator_fixes(validator_output)

        logger.info(f"Validator generated {len(fixes)} fixes")

        # DEBUG: If no fixes found, log more details
        if len(fixes) == 0:
            logger.warning(f"No <FIX> blocks found in validator output ({len(validator_output)} chars)")
            if "<FIX>" in validator_output:
                logger.warning("Found '<FIX>' string but regex didn't match - check formatting")
            else:
                logger.warning("No '<FIX>' string found in output - validator didn't generate fix blocks")

        # Apply fixes to thesis
        fixed_thesis = thesis
        fixes_applied = 0

        for fix in fixes:
            find_text = fix.get("find", "")
            replace_text = fix.get("replace", "")
            verified_with = fix.get("verified_with", "")

            if find_text and replace_text:
                if find_text in fixed_thesis:
                    fixed_thesis = fixed_thesis.replace(find_text, replace_text, 1)
                    fixes_applied += 1
                    logger.info(f"✓ Applied fix (verified with: {verified_with})")
                else:
                    logger.warning(f"⚠ Could not find text to fix: {find_text[:100]}...")

        logger.info(f"Applied {fixes_applied}/{len(fixes)} fixes successfully")

        # Update result with fixed thesis
        result["thesis"] = fixed_thesis

        # Re-parse decision and metrics from fixed thesis
        fixed_decision_data = self._parse_decision(ticker, fixed_thesis)

        # Update decision/conviction from validator output
        if "FINAL DECISION:" in validator_output:
            import re
            decision_match = re.search(r'\*\*FINAL DECISION:\s*(BUY|WATCH|AVOID)\*\*', validator_output, re.IGNORECASE)
            if decision_match:
                result["decision"] = decision_match.group(1).upper()
                logger.info(f"✓ Extracted final decision from validator: {result['decision']}")

        # Fallback: re-parse from fixed thesis
        if result.get("decision") == "UNKNOWN" and fixed_decision_data.get("decision") != "UNKNOWN":
            result["decision"] = fixed_decision_data["decision"]
            logger.info(f"✓ Re-parsed decision from fixed thesis: {result['decision']}")

        if "FINAL CONVICTION:" in validator_output:
            import re
            conviction_match = re.search(r'\*\*FINAL CONVICTION:\s*(HIGH|MODERATE|LOW)\*\*', validator_output, re.IGNORECASE)
            if conviction_match:
                result["conviction"] = conviction_match.group(1).upper()
                logger.info(f"✓ Extracted final conviction from validator: {result['conviction']}")

        # Fallback: re-parse from fixed thesis
        if result.get("conviction") == "UNKNOWN" and fixed_decision_data.get("conviction") != "UNKNOWN":
            result["conviction"] = fixed_decision_data["conviction"]
            logger.info(f"✓ Re-parsed conviction from fixed thesis: {result['conviction']}")

        # Update numeric fields from fixed thesis (only if not None)
        numeric_fields = ["intrinsic_value", "margin_of_safety", "current_price", "roic", "owner_earnings"]
        for field in numeric_fields:
            if fixed_decision_data.get(field) is not None:
                old_value = result.get(field)
                new_value = fixed_decision_data[field]
                if old_value != new_value:
                    logger.info(f"Updated {field}: {old_value} → {new_value}")
                    result[field] = new_value

        # Update metadata
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"]["validator_fixes_applied"] = fixes_applied
        result["metadata"]["validator_tool_calls"] = validator_result["metadata"].get("tool_calls", 0)

        return result

    def _parse_validator_fixes(self, validator_output: str) -> List[Dict[str, str]]:
        """
        Parse structured fixes from validator output.

        Looks for <FIX>...</FIX> blocks containing:
        - <FIND>text to replace</FIND>
        - <REPLACE>replacement text</REPLACE>
        - <VERIFIED_WITH>tool used</VERIFIED_WITH>

        Args:
            validator_output: Validator's output text

        Returns:
            List of fix dicts with find, replace, verified_with keys
        """
        import re

        fixes = []

        # Pattern to match <FIX>...</FIX> blocks
        fix_pattern = r'<FIX>(.*?)</FIX>'
        fix_blocks = re.findall(fix_pattern, validator_output, re.DOTALL)

        for block in fix_blocks:
            # Extract FIND, REPLACE, VERIFIED_WITH
            find_match = re.search(r'<FIND>(.*?)</FIND>', block, re.DOTALL)
            replace_match = re.search(r'<REPLACE>(.*?)</REPLACE>', block, re.DOTALL)
            verified_match = re.search(r'<VERIFIED_WITH>(.*?)</VERIFIED_WITH>', block, re.DOTALL)

            if find_match and replace_match:
                fix = {
                    "find": find_match.group(1).strip(),
                    "replace": replace_match.group(1).strip(),
                    "verified_with": verified_match.group(1).strip() if verified_match else "unknown"
                }
                fixes.append(fix)

        return fixes

    def _validate_analysis(
        self,
        analysis_result: Dict[str, Any],
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        Validate analysis using Validator Agent.

        Phase 7.6B: Validator Agent reviews analysis for quality, methodology,
        and completeness, providing detailed critique.

        Args:
            analysis_result: Analysis dict from Warren Agent
            iteration: Current iteration number (0-based)

        Returns:
            Validator critique dict with:
                - approved: bool
                - score: int (0-100)
                - overall_assessment: str
                - strengths: List[str]
                - issues: List[Dict]
                - recommendation: str ("approve"|"revise"|"reject")
        """
        from src.agent.prompts import get_validator_prompt
        from src.agent.validator_checks import run_all_validations

        logger.info(f"[VALIDATOR] Reviewing analysis (iteration {iteration + 1})")

        # Phase 7.7: Run structured data validation FIRST
        structured_validation = run_all_validations(analysis_result)

        # Build validator prompt (include structured validation results)
        prompt = get_validator_prompt(analysis_result, iteration, structured_validation)

        # Call validator LLM with tools for verification
        try:
            # Get validator tools (web_search and calculator for verification)
            validator_tools = self._get_validator_tool_definitions()

            # Use validator's provider native ReAct loop for validation
            response = self.validator_llm.provider.run_react_loop(
                system_prompt="You are a validator reviewing investment analysis. Use tools to verify claims before flagging issues.",
                initial_message=prompt,
                tools=validator_tools,
                tool_executor=self._execute_validator_tool,
                max_iterations=10,  # Allow validator to call tools
                max_tokens=8000,
                thinking_budget=0  # Deterministic validation, no extended thinking needed
            )

            # Parse JSON response from validator's final output
            critique = self._parse_json_response(response.get("thesis", ""), "validation")

            # Log validation results
            score = critique.get('score', 0)
            approved = critique.get('approved', False)
            issues_count = len(critique.get('issues', []))

            logger.info(f"[VALIDATOR] Score: {score}/100, Approved: {approved}, Issues: {issues_count}")

            if not approved:
                # Log issues for visibility
                for issue in critique.get('issues', []):
                    severity = issue.get('severity', 'unknown').upper()
                    category = issue.get('category', 'unknown')
                    description = issue.get('description', '')
                    logger.warning(f"[{severity}] {category}: {description}")

            return critique

        except Exception as e:
            logger.error(f"Validator failed: {e}", exc_info=True)
            # Return a failed validation instead of crashing
            return {
                "approved": False,
                "score": 0,
                "overall_assessment": f"Validator error: {str(e)}",
                "strengths": [],
                "issues": [{
                    "severity": "critical",
                    "category": "validation",
                    "description": f"Validator failed: {str(e)}",
                    "how_to_fix": "Check validator configuration and LLM availability"
                }],
                "recommendation": "reject",
                "error": str(e)
            }

    def _get_validator_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for validator (web_search, calculator, gurufocus, and sec_filing).

        Validator needs limited tools to verify claims:
        - web_search: Verify recent events beyond knowledge cutoff (CEO changes, current price)
        - calculator: Verify DCF, ROIC, Owner Earnings calculations
        - gurufocus: Verify financial metrics (revenue, margins, ratios)
        - sec_filing: Verify specific quotes, page citations (USE SPARINGLY - request specific sections only)

        Returns:
            List of tool definitions in provider-specific format
        """
        # Only expose web_search, calculator, gurufocus, and sec_filing to validator
        # Note: sec_filing should be used SPARINGLY to verify specific quotes/citations only
        validator_tool_names = ["web_search", "calculator", "gurufocus", "sec_filing"]

        all_tools = self._get_tool_definitions()

        # Filter to only validator tools (handle both standard and builtin_function formats)
        validator_tools = []
        for tool in all_tools:
            # Extract tool name (handle different formats)
            if tool.get("type") == "builtin_function":
                # Kimi builtin function (e.g., $web_search)
                tool_name = tool.get("function", {}).get("name", "")
            else:
                # Standard tool (Claude format or converted OpenAI format)
                tool_name = tool.get("name", "")

            # Check if this tool should be available to validator
            if any(name in tool_name.lower().replace("$", "") for name in validator_tool_names):
                validator_tools.append(tool)

        logger.info(f"Validator tools available: {len(validator_tools)} tools")
        for tool in validator_tools:
            if tool.get("type") == "builtin_function":
                logger.info(f"  - {tool.get('function', {}).get('name', 'unknown')} (builtin)")
            else:
                logger.info(f"  - {tool.get('name', 'unknown')}")

        return validator_tools

    def _execute_validator_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool for validator with logging.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool parameters

        Returns:
            Tool execution result
        """
        logger.info(f"[VALIDATOR] Executing {tool_name}")

        # Find the tool
        tool = self.tools.get(tool_name)
        if not tool:
            # Try to find by partial match (e.g., "calculator_tool" -> "calculator")
            for name, t in self.tools.items():
                if name.lower() in tool_name.lower():
                    tool = t
                    break

        if not tool:
            logger.warning(f"[VALIDATOR] Tool '{tool_name}' not found")
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not available to validator"
            }

        try:
            # Execute tool
            result = tool.execute(**tool_input)

            # Log success/failure
            if result.get("success"):
                logger.info(f"[VALIDATOR] {tool_name} succeeded")
            else:
                logger.warning(f"[VALIDATOR] {tool_name} failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"[VALIDATOR] {tool_name} error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_json_response(self, text: str, context: str) -> Dict:
        """
        Parse JSON response from LLM (validator or analyst).

        Handles cases where JSON is wrapped in markdown code blocks or
        mixed with explanatory text.

        Args:
            text: Response text from LLM
            context: Context string for error messages

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If no valid JSON found
        """
        import json
        import re

        # Try to find JSON between ```json and ``` or just find {...}
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find raw JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                logger.error(f"No JSON found in {context} response")
                logger.error(f"Response text: {text[:500]}...")
                raise ValueError(f"No JSON found in {context} response")

        # Parse JSON
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing error for {context}: {e}")
            logger.warning(f"Text: {json_text[:500]}...")

            # Fallback: Extract key fields with regex for partial validation results
            if context == "validation":
                logger.info("Attempting fallback parsing for validation critique...")

                # Extract score
                score_match = re.search(r'"score"\s*:\s*(\d+)', json_text)
                score = int(score_match.group(1)) if score_match else 0

                # Extract approved
                approved_match = re.search(r'"approved"\s*:\s*(true|false)', json_text, re.IGNORECASE)
                approved = approved_match.group(1).lower() == 'true' if approved_match else False

                # Extract overall_assessment
                assessment_match = re.search(r'"overall_assessment"\s*:\s*"([^"]*)"', json_text)
                assessment = assessment_match.group(1) if assessment_match else f"JSON parse error: {str(e)}"

                logger.info(f"Fallback parsing extracted: score={score}, approved={approved}")

                return {
                    "approved": approved,
                    "score": score,
                    "overall_assessment": assessment,
                    "strengths": [],
                    "issues": [{
                        "severity": "minor",
                        "category": "validation",
                        "description": f"Validator JSON was malformed (parse error at char {e.pos}), using fallback parsing. Score and approval extracted successfully.",
                        "how_to_fix": "N/A - technical issue, not analysis issue"
                    }],
                    "methodology_correct": score >= 70,
                    "calculations_complete": score >= 70,
                    "sources_adequate": score >= 70,
                    "buffett_principles_followed": score >= 70,
                    "recommendation": "approve" if approved else "revise"
                }
            else:
                # For non-validation contexts, raise the error
                raise ValueError(f"Invalid JSON in {context} response: {e}")

    def _check_validation_progress(
        self,
        previous_critique: Dict,
        current_critique: Dict
    ) -> bool:
        """
        Check if analysis improved between validation iterations.

        Progress is indicated by:
        - Higher validation score, OR
        - Fewer issues identified

        Args:
            previous_critique: Validator critique from previous iteration
            current_critique: Validator critique from current iteration

        Returns:
            bool: True if analysis improved, False otherwise
        """
        prev_score = previous_critique.get('score', 0)
        curr_score = current_critique.get('score', 0)
        prev_issues = len(previous_critique.get('issues', []))
        curr_issues = len(current_critique.get('issues', []))

        # Improved if score increased OR issues decreased
        score_improved = curr_score > prev_score
        issues_decreased = curr_issues < prev_issues

        improved = score_improved or issues_decreased

        if improved:
            logger.info(
                f"[PROGRESS] Score {prev_score}→{curr_score}, "
                f"Issues {prev_issues}→{curr_issues} ✅"
            )
        else:
            logger.warning(
                f"[PROGRESS] Score {prev_score}→{curr_score}, "
                f"Issues {prev_issues}→{curr_issues} ⚠️ No improvement"
            )

        return improved


class ValidationError(Exception):
    """Raised when analysis fails validation after max iterations."""
    pass


__all__ = ["WarrenBuffettAgent", "ValidationError"]
