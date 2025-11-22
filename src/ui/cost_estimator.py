"""
Provider-Aware Cost Estimation

This module provides cost estimates for all analysis types.
Uses provider-specific token counting when available.
"""

import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)


class CostEstimator:
    """Provides cost estimates using provider-specific methods."""

    # Pricing per 1K tokens by provider
    PROVIDER_COSTS = {
        "claude": {
            "input": 0.01,  # $0.01 per 1K input tokens (Claude Sonnet 4.5)
            "output": 0.30   # $0.30 per 1K output tokens
        },
        "kimi": {
            "input": 0.006,  # Estimated ~60% cheaper than Claude
            "output": 0.18   # Estimated ~60% cheaper than Claude
        }
    }

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
        """Initialize cost estimator with provider-specific clients."""
        # Initialize Anthropic client if available (for Claude token counting)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
        else:
            self.anthropic_client = None
            logger.warning("ANTHROPIC_API_KEY not found - Claude token counting unavailable")

    def _get_provider_name(self, agent) -> str:
        """Get provider name from agent."""
        provider_info = agent.llm.get_provider_info()
        provider = provider_info.get('provider', '').lower()
        return provider

    def _get_provider_costs(self, provider: str) -> Dict[str, float]:
        """Get cost per 1K tokens for provider."""
        return self.PROVIDER_COSTS.get(provider, self.PROVIDER_COSTS["claude"])

    def estimate_quick_screen_cost(
        self,
        ticker: str,
        agent
    ) -> Dict[str, Any]:
        """
        Get cost estimate for Quick Screen analysis.

        Args:
            ticker: Stock ticker symbol
            agent: WarrenBuffettAgent instance

        Returns:
            Dict with cost breakdown and token counts
        """
        provider = self._get_provider_name(agent)
        costs = self._get_provider_costs(provider)

        try:
            # Build the message structure that will be used
            system_prompt = agent.system_prompt

            # Build initial user message
            initial_message = f"""Analyze {ticker} stock using Warren Buffett's investment principles.

This is a Quick Screen analysis (1 year of data). Provide a focused analysis with:
1. Key metrics evaluation
2. Competitive advantages assessment
3. Deep Dive recommendation (should this be investigated further?)

Focus on quality over quantity. Be concise but thorough."""

            # Count tokens (Claude-specific)
            if provider == "claude" and self.anthropic_client:
                response = self.anthropic_client.messages.count_tokens(
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
            else:
                # For Kimi or when Claude token counting unavailable, use estimation
                # Rough estimate: ~4 chars per token
                total_chars = len(system_prompt) + len(initial_message)
                input_tokens = total_chars // 4
                logger.info(f"Using character-based token estimation for {provider}")

            # Add empirical estimate for tool responses
            estimated_total_input_tokens = input_tokens + self.QUICK_SCREEN_TOOL_TOKENS
            estimated_output_tokens = self.QUICK_SCREEN_OUTPUT_TOKENS

            # Calculate costs using provider-specific pricing
            input_cost = (estimated_total_input_tokens / 1000) * costs["input"]
            output_cost = (estimated_output_tokens / 1000) * costs["output"]
            total_cost = input_cost + output_cost

            logger.info(
                f"Quick Screen cost estimate for {ticker} ({provider}): "
                f"{input_tokens} initial + {self.QUICK_SCREEN_TOOL_TOKENS} tool results = "
                f"{estimated_total_input_tokens} total input tokens, ${total_cost:.2f} total"
            )

            return {
                "success": True,
                "analysis_type": "quick_screen",
                "ticker": ticker,
                "provider": provider,
                "input_tokens": estimated_total_input_tokens,
                "initial_prompt_tokens": input_tokens,
                "tool_response_tokens": self.QUICK_SCREEN_TOOL_TOKENS,
                "estimated_output_tokens": estimated_output_tokens,
                "input_cost": round(input_cost, 2),
                "estimated_output_cost": round(output_cost, 2),
                "total_estimated_cost": round(total_cost, 2),
                "min_cost": round(total_cost * 0.85, 2),
                "max_cost": round(total_cost * 1.15, 2),
                "confidence": "high" if provider == "claude" else "medium"
            }

        except Exception as e:
            logger.error(f"Failed to estimate Quick Screen cost: {e}")
            return self._fallback_estimate("quick_screen", str(e), provider=provider)

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
        Get cost estimate for Sharia Compliance screening.

        Args:
            ticker: Stock ticker symbol
            screener: ShariaScreener instance

        Returns:
            Dict with cost breakdown and token counts
        """
        provider = self._get_provider_name(screener)
        costs = self._get_provider_costs(provider)

        try:
            # Build Sharia screening prompt
            prompt = screener._build_sharia_screening_prompt(ticker)

            # Count tokens (Claude-specific)
            if provider == "claude" and self.anthropic_client:
                # Get provider info to get model ID
                provider_info = screener.llm.get_provider_info()
                model_id = provider_info['model_id']

                response = self.anthropic_client.messages.count_tokens(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    tools=screener._get_tool_definitions(),
                    thinking={
                        "type": "enabled",
                        "budget_tokens": screener.THINKING_BUDGET
                    }
                )
                input_tokens = response.input_tokens
            else:
                # For Kimi or when Claude token counting unavailable, use estimation
                # Rough estimate: ~4 chars per token
                total_chars = len(prompt)
                input_tokens = total_chars // 4
                logger.info(f"Using character-based token estimation for {provider}")

            # Add empirical estimate for tool responses
            estimated_total_input_tokens = input_tokens + self.SHARIA_SCREEN_TOOL_TOKENS
            estimated_output_tokens = self.SHARIA_SCREEN_OUTPUT_TOKENS

            # Calculate costs using provider-specific pricing
            input_cost = (estimated_total_input_tokens / 1000) * costs["input"]
            output_cost = (estimated_output_tokens / 1000) * costs["output"]
            total_cost = input_cost + output_cost

            logger.info(
                f"Sharia Screen cost estimate for {ticker} ({provider}): "
                f"{input_tokens} initial + {self.SHARIA_SCREEN_TOOL_TOKENS} tool results = "
                f"{estimated_total_input_tokens} total input tokens, ${total_cost:.2f} total"
            )

            return {
                "success": True,
                "analysis_type": "sharia_compliance",
                "ticker": ticker,
                "provider": provider,
                "input_tokens": estimated_total_input_tokens,
                "initial_prompt_tokens": input_tokens,
                "tool_response_tokens": self.SHARIA_SCREEN_TOOL_TOKENS,
                "estimated_output_tokens": estimated_output_tokens,
                "input_cost": round(input_cost, 2),
                "estimated_output_cost": round(output_cost, 2),
                "total_estimated_cost": round(total_cost, 2),
                "min_cost": round(total_cost * 0.85, 2),
                "max_cost": round(total_cost * 1.20, 2),
                "confidence": "high" if provider == "claude" else "medium"
            }

        except Exception as e:
            logger.error(f"Failed to estimate Sharia Screen cost: {e}")
            return self._fallback_estimate("sharia_compliance", str(e), provider=provider)

    def _fallback_estimate(
        self,
        analysis_type: str,
        error: str,
        years: int = 1,
        provider: str = "claude"
    ) -> Dict[str, Any]:
        """
        Provide fallback estimate if token counting fails.

        Args:
            analysis_type: Type of analysis
            error: Error message
            years: Number of years (for deep dive)
            provider: LLM provider name

        Returns:
            Dict with rough cost estimate
        """
        logger.warning(f"Using fallback estimate for {provider} due to error: {error}")

        # Adjust costs based on provider (Kimi ~60% of Claude cost)
        cost_multiplier = 0.6 if provider == "kimi" else 1.0

        # Fallback to rough estimates
        if analysis_type == "quick_screen":
            base_cost = 1.25 * cost_multiplier
            return {
                "success": False,
                "error": error,
                "analysis_type": analysis_type,
                "provider": provider,
                "total_estimated_cost": round(base_cost, 2),
                "min_cost": round(base_cost * 0.6, 2),
                "max_cost": round(base_cost * 1.2, 2),
                "confidence": "low",
                "note": f"Token counting unavailable for {provider}, using historical average"
            }
        elif analysis_type == "deep_dive":
            base = 2.50 * cost_multiplier
            total = base + (years - 1) * 0.50 * cost_multiplier
            return {
                "success": False,
                "error": error,
                "analysis_type": analysis_type,
                "provider": provider,
                "years_to_analyze": years,
                "total_estimated_cost": round(total, 2),
                "min_cost": round(total * 0.8, 2),
                "max_cost": round(total * 1.2, 2),
                "confidence": "low",
                "note": f"Token counting unavailable for {provider}, using historical average"
            }
        else:  # sharia_compliance
            base_cost = 5.50 * cost_multiplier
            return {
                "success": False,
                "error": error,
                "analysis_type": analysis_type,
                "provider": provider,
                "total_estimated_cost": round(base_cost, 2),
                "min_cost": round(base_cost * 0.73, 2),
                "max_cost": round(base_cost * 1.27, 2),
                "confidence": "low",
                "note": f"Token counting unavailable for {provider}, using historical average"
            }


__all__ = ["CostEstimator"]
