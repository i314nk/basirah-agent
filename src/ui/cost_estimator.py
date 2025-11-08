"""
Accurate Cost Estimation using Claude Token Counting API

This module provides precise cost estimates for all analysis types
using Anthropic's token counting endpoint.
"""

import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)


class CostEstimator:
    """Provides accurate cost estimates using token counting API."""

    # Pricing per 1K tokens (Claude Sonnet 4.5)
    INPUT_COST_PER_1K = 0.01  # $0.01 per 1K input tokens
    OUTPUT_COST_PER_1K = 0.30  # $0.30 per 1K output tokens

    # Conservative output token estimates (based on historical data)
    # These will be refined over time with actual usage data
    QUICK_SCREEN_OUTPUT_TOKENS = 3000  # Typical quick screen thesis
    DEEP_DIVE_OUTPUT_TOKENS = 5000  # Typical deep dive thesis
    SHARIA_SCREEN_OUTPUT_TOKENS = 2500  # Typical Sharia analysis

    # Empirical tool response token estimates
    # These account for SEC filings and tool results added during ReAct loop
    # Deep Dive uses context management: current year full 10-K + prior year summaries (2-3K each)
    QUICK_SCREEN_TOOL_TOKENS = 15000  # Business section (~10-20K) + GuruFocus (~2-5K)
    DEEP_DIVE_BASE_TOKENS = 50000  # Current year full 10-K analysis
    DEEP_DIVE_TOKENS_PER_ADDITIONAL_YEAR = 3000  # Prior year summary (2-3K each, due to summarization)
    SHARIA_SCREEN_TOOL_TOKENS = 18000  # Business section (~10-20K) + GuruFocus calls (~5-8K for multiple metrics)

    def __init__(self):
        """Initialize cost estimator with Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = Anthropic(api_key=api_key)

    def estimate_quick_screen_cost(
        self,
        ticker: str,
        agent
    ) -> Dict[str, Any]:
        """
        Get accurate cost estimate for Quick Screen analysis.

        Args:
            ticker: Stock ticker symbol
            agent: WarrenBuffettAgent instance

        Returns:
            Dict with cost breakdown and token counts
        """
        try:
            # Build the message structure that will be used
            system_prompt = agent.system_prompt  # Quick screen uses standard prompt

            # Build initial user message for 1-year analysis
            initial_message = f"""Analyze {ticker} stock using Warren Buffett's investment principles.

This is a Quick Screen analysis (1 year of data). Provide a focused analysis with:
1. Key metrics evaluation
2. Competitive advantages assessment
3. Deep Dive recommendation (should this be investigated further?)

Focus on quality over quantity. Be concise but thorough."""

            # Count tokens
            response = self.client.messages.count_tokens(
                model=agent.MODEL,
                system=system_prompt,
                messages=[{"role": "user", "content": initial_message}],
                tools=agent._get_tool_definitions(),
                thinking={
                    "type": "enabled",
                    "budget_tokens": agent.THINKING_BUDGET
                }
            )

            input_tokens = response.input_tokens

            # Add empirical estimate for tool responses (SEC business section + GuruFocus data)
            estimated_total_input_tokens = input_tokens + self.QUICK_SCREEN_TOOL_TOKENS
            estimated_output_tokens = self.QUICK_SCREEN_OUTPUT_TOKENS

            # Calculate costs
            input_cost = (estimated_total_input_tokens / 1000) * self.INPUT_COST_PER_1K
            output_cost = (estimated_output_tokens / 1000) * self.OUTPUT_COST_PER_1K
            total_cost = input_cost + output_cost

            logger.info(
                f"Quick Screen cost estimate for {ticker}: "
                f"{input_tokens} initial + {self.QUICK_SCREEN_TOOL_TOKENS} tool results = "
                f"{estimated_total_input_tokens} total input tokens, ${total_cost:.2f} total"
            )

            return {
                "success": True,
                "analysis_type": "quick_screen",
                "ticker": ticker,
                "input_tokens": estimated_total_input_tokens,
                "initial_prompt_tokens": input_tokens,
                "tool_response_tokens": self.QUICK_SCREEN_TOOL_TOKENS,
                "estimated_output_tokens": estimated_output_tokens,
                "input_cost": round(input_cost, 2),
                "estimated_output_cost": round(output_cost, 2),
                "total_estimated_cost": round(total_cost, 2),
                "min_cost": round(total_cost * 0.85, 2),  # -15% variance (tool sizes vary)
                "max_cost": round(total_cost * 1.15, 2),  # +15% variance
                "confidence": "high"  # Token counting + empirical tool estimates
            }

        except Exception as e:
            logger.error(f"Failed to estimate Quick Screen cost: {e}")
            return self._fallback_estimate("quick_screen", str(e))

    def estimate_deep_dive_cost(
        self,
        ticker: str,
        years_to_analyze: int,
        agent
    ) -> Dict[str, Any]:
        """
        Get accurate cost estimate for Deep Dive analysis.

        Args:
            ticker: Stock ticker symbol
            years_to_analyze: Number of years to analyze (1-10)
            agent: WarrenBuffettAgent instance

        Returns:
            Dict with cost breakdown and token counts
        """
        try:
            # Build multi-year analysis prompt (this is complex)
            # Note: Actual deep dive builds prompts dynamically with filing data,
            # but we can estimate based on the system prompt + tool definitions

            system_prompt = agent.system_prompt

            initial_message = f"""Perform a comprehensive {years_to_analyze}-year Deep Dive analysis on {ticker}.

Analyze fiscal years and provide a complete Warren Buffett-style investment thesis covering:
1. Business Quality Assessment
2. Competitive Advantages (Moat Analysis)
3. Management Quality
4. Financial Analysis
5. Valuation
6. Risk Assessment
7. Circle of Competence
8. Investment Decision

Use all available tools to gather data."""

            # Count tokens
            response = self.client.messages.count_tokens(
                model=agent.MODEL,
                system=system_prompt,
                messages=[{"role": "user", "content": initial_message}],
                tools=agent._get_tool_definitions(),
                thinking={
                    "type": "enabled",
                    "budget_tokens": agent.THINKING_BUDGET
                }
            )

            input_tokens = response.input_tokens

            # Add empirical estimate for tool responses
            # Context management: current year full 10-K + prior year summaries (2-3K each)
            tool_tokens = self.DEEP_DIVE_BASE_TOKENS + (years_to_analyze - 1) * self.DEEP_DIVE_TOKENS_PER_ADDITIONAL_YEAR
            estimated_total_input_tokens = input_tokens + tool_tokens

            # Deep dive output scales with years (more data = longer thesis)
            estimated_output_tokens = self.DEEP_DIVE_OUTPUT_TOKENS + (years_to_analyze - 1) * 500

            # Calculate costs
            input_cost = (estimated_total_input_tokens / 1000) * self.INPUT_COST_PER_1K
            output_cost = (estimated_output_tokens / 1000) * self.OUTPUT_COST_PER_1K
            total_cost = input_cost + output_cost

            logger.info(
                f"Deep Dive cost estimate for {ticker} ({years_to_analyze} years): "
                f"{input_tokens} initial + {tool_tokens} tool results = "
                f"{estimated_total_input_tokens} total input tokens, ${total_cost:.2f} total"
            )

            return {
                "success": True,
                "analysis_type": "deep_dive",
                "ticker": ticker,
                "years_to_analyze": years_to_analyze,
                "input_tokens": estimated_total_input_tokens,
                "initial_prompt_tokens": input_tokens,
                "tool_response_tokens": tool_tokens,
                "estimated_output_tokens": estimated_output_tokens,
                "input_cost": round(input_cost, 2),
                "estimated_output_cost": round(output_cost, 2),
                "total_estimated_cost": round(total_cost, 2),
                "min_cost": round(total_cost * 0.80, 2),  # -20% variance (filing sizes vary)
                "max_cost": round(total_cost * 1.20, 2),  # +20% variance
                "confidence": "medium"  # Empirical estimates for tool responses
            }

        except Exception as e:
            logger.error(f"Failed to estimate Deep Dive cost: {e}")
            return self._fallback_estimate("deep_dive", str(e), years_to_analyze)

    def estimate_sharia_screen_cost(
        self,
        ticker: str,
        screener
    ) -> Dict[str, Any]:
        """
        Get accurate cost estimate for Sharia Compliance screening.

        Args:
            ticker: Stock ticker symbol
            screener: ShariaScreener instance

        Returns:
            Dict with cost breakdown and token counts
        """
        try:
            # Build Sharia screening prompt
            prompt = screener._build_sharia_screening_prompt(ticker)

            # Count tokens
            response = self.client.messages.count_tokens(
                model=screener.MODEL,
                messages=[{"role": "user", "content": prompt}],
                tools=screener._get_tool_definitions(),
                thinking={
                    "type": "enabled",
                    "budget_tokens": screener.THINKING_BUDGET
                }
            )

            input_tokens = response.input_tokens

            # Add empirical estimate for tool responses (full 10-K + GuruFocus calls)
            estimated_total_input_tokens = input_tokens + self.SHARIA_SCREEN_TOOL_TOKENS
            estimated_output_tokens = self.SHARIA_SCREEN_OUTPUT_TOKENS

            # Calculate costs
            input_cost = (estimated_total_input_tokens / 1000) * self.INPUT_COST_PER_1K
            output_cost = (estimated_output_tokens / 1000) * self.OUTPUT_COST_PER_1K
            total_cost = input_cost + output_cost

            logger.info(
                f"Sharia Screen cost estimate for {ticker}: "
                f"{input_tokens} initial + {self.SHARIA_SCREEN_TOOL_TOKENS} tool results = "
                f"{estimated_total_input_tokens} total input tokens, ${total_cost:.2f} total"
            )

            return {
                "success": True,
                "analysis_type": "sharia_compliance",
                "ticker": ticker,
                "input_tokens": estimated_total_input_tokens,
                "initial_prompt_tokens": input_tokens,
                "tool_response_tokens": self.SHARIA_SCREEN_TOOL_TOKENS,
                "estimated_output_tokens": estimated_output_tokens,
                "input_cost": round(input_cost, 2),
                "estimated_output_cost": round(output_cost, 2),
                "total_estimated_cost": round(total_cost, 2),
                "min_cost": round(total_cost * 0.85, 2),  # -15% variance (filing sizes vary)
                "max_cost": round(total_cost * 1.20, 2),  # +20% variance
                "confidence": "high"  # Token counting + empirical tool estimates
            }

        except Exception as e:
            logger.error(f"Failed to estimate Sharia Screen cost: {e}")
            return self._fallback_estimate("sharia_compliance", str(e))

    def _fallback_estimate(
        self,
        analysis_type: str,
        error: str,
        years: int = 1
    ) -> Dict[str, Any]:
        """
        Provide fallback estimate if token counting fails.

        Args:
            analysis_type: Type of analysis
            error: Error message
            years: Number of years (for deep dive)

        Returns:
            Dict with rough cost estimate
        """
        logger.warning(f"Using fallback estimate due to error: {error}")

        # Fallback to rough estimates
        if analysis_type == "quick_screen":
            return {
                "success": False,
                "error": error,
                "analysis_type": analysis_type,
                "total_estimated_cost": 1.25,
                "min_cost": 0.75,
                "max_cost": 1.50,
                "confidence": "low",
                "note": "Token counting unavailable, using historical average"
            }
        elif analysis_type == "deep_dive":
            base = 2.50
            total = base + (years - 1) * 0.50
            return {
                "success": False,
                "error": error,
                "analysis_type": analysis_type,
                "years_to_analyze": years,
                "total_estimated_cost": total,
                "min_cost": total * 0.8,
                "max_cost": total * 1.2,
                "confidence": "low",
                "note": "Token counting unavailable, using historical average"
            }
        else:  # sharia_compliance
            return {
                "success": False,
                "error": error,
                "analysis_type": analysis_type,
                "total_estimated_cost": 5.50,
                "min_cost": 4.00,
                "max_cost": 7.00,
                "confidence": "low",
                "note": "Token counting unavailable, using historical average"
            }


__all__ = ["CostEstimator"]
