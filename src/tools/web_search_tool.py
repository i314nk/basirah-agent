"""
Web Search Tool - Provider-Native Implementation

Module: src.tools.web_search_tool
Purpose: Signal providers to use native web search capabilities
Status: Phase 7.6D - Provider-Native Web Search
Updated: 2025-11-15

This tool signals to LLM providers that web search capabilities are needed.
The actual search execution is handled by provider-native implementations:

- Claude: web_search_20250305 ($10/1K searches + tokens)
  * Automatic execution and citations
  * Domain filtering support
  * Localization support

- Kimi: $web_search builtin_function (only token costs ~9K tokens per search)
  * Included in model subscription
  * Kimi executes search internally and returns results
  * No separate search fees

This eliminates the need for external search APIs (Brave Search) and their rate limits.

References:
- Claude Web Search: https://docs.anthropic.com/en/docs/build-with-claude/tool-use/web-search
- Kimi Web Search: https://platform.moonshot.ai/docs/guide/use-web-search
- PROPOSAL_NATIVE_WEB_SEARCH.md (Implementation proposal)
"""

import logging
from typing import Dict, Any, Optional

from src.tools.base import Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """
    Web search proxy tool - signals providers to use native web search.

    This tool doesn't execute searches directly. Instead, it provides the interface
    that LLM providers use to understand that web search is needed. The actual
    search execution is handled by provider-native implementations:

    Claude:
        - Uses web_search_20250305 tool type
        - Automatically executes searches and provides citations
        - Cost: $10 per 1,000 searches + token costs

    Kimi:
        - Uses $web_search builtin_function
        - Kimi executes search internally and returns results in tool arguments
        - Cost: Only token costs (~9K tokens per search, no separate search fees)

    Unknown Providers:
        - Returns a message indicating provider-native handling is expected
        - Should not be called in production (providers should use native search)

    Usage:
        tool = WebSearchTool()
        result = tool.execute(
            query="Novo Nordisk CEO change 2025",
            search_type="news",  # "general", "news", or "recent"
            freshness="month"     # "day", "week", "month", "year"
        )

    Args for execute:
        query (str): Search query
        search_type (str): Type of search - "general", "news", or "recent" (default: "general")
        freshness (str): Time filter - "day", "week", "month", "year" (optional)

    Returns:
        Dict with status message (should not be called in production)
    """

    # Tool metadata
    name = "web_search"
    description = """Search the web for current information beyond knowledge cutoff.

Use for:
- Company news and recent developments
- CEO changes and management transitions
- Current stock prices and market data
- Economic moat research (brand, competitive advantages)
- Risk assessment (litigation, regulatory issues)
- Competitive landscape analysis

Search types:
- "general": Standard web search (evergreen content, background research)
- "news": News articles and press releases (current events, announcements)
- "recent": Last 30 days only (breaking news, latest developments)

Freshness filters (optional):
- "day": Last 24 hours
- "week": Last 7 days
- "month": Last 30 days
- "year": Last 12 months

Returns structured search results with URLs, titles, descriptions, and dates."""

    # JSON Schema parameters for LLM tool calling
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (company name automatically appended if relevant)"
            },
            "search_type": {
                "type": "string",
                "enum": ["general", "news", "recent"],
                "description": "Type of search: 'general' (default), 'news', or 'recent' (last 30 days)",
                "default": "general"
            },
            "freshness": {
                "type": "string",
                "enum": ["day", "week", "month", "year"],
                "description": "Optional time filter: 'day', 'week', 'month', or 'year'"
            }
        },
        "required": ["query"]
    }

    def __init__(self):
        """
        Initialize Web Search Tool.

        No API keys required - providers handle search execution natively.
        """
        logger.info("Initialized Web Search Tool (provider-native)")

    def execute(
        self,
        query: str,
        search_type: str = "general",
        freshness: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Signal that web search is needed (actual search handled by provider).

        This method should NOT be called in production when using Claude or Kimi,
        as they handle searches natively. If this is called, it indicates:
        1. Unknown provider without native search support
        2. Configuration error in tool routing

        Args:
            query: Search query
            search_type: Type of search ("general", "news", "recent")
            freshness: Optional time filter ("day", "week", "month", "year")
            **kwargs: Additional arguments (ignored)

        Returns:
            Dict indicating this should be handled by provider-native search
        """
        logger.warning(f"Web search tool called directly (should use provider-native): '{query}'")
        logger.warning("This indicates either unknown provider or configuration error")

        if freshness:
            logger.info(f"Freshness filter: {freshness}")

        return {
            "status": "provider_native_expected",
            "message": "This tool should be handled by provider-native web search. "
                      "Claude uses web_search_20250305, Kimi uses $web_search builtin. "
                      "If you're seeing this, check provider configuration.",
            "query": query,
            "search_type": search_type,
            "freshness": freshness,
            "note": "For Claude: web_search_20250305 with domain filtering. "
                   "For Kimi: $web_search builtin_function (free, ~9K tokens per search). "
                   "Both providers handle searches automatically."
        }

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert tool to JSON schema format for LLM tool calling.

        Returns:
            Dict with tool schema (name, description, parameters)
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


# Export for easy imports
__all__ = ["WebSearchTool"]
