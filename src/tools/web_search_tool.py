"""
Web Search Tool

Module: src.tools.web_search_tool
Purpose: Enable qualitative research using Brave Search API for Warren Buffett-style analysis
Status: Complete - Sprint 3, Phase 3
Created: 2025-10-30

This tool provides web search capabilities for the basīrah investment agent:
- Company news and recent developments
- Economic moat indicators (brand, network effects, switching costs)
- Management quality research (CEO background, controversies)
- Risk assessment (litigation, regulatory issues, red flags)
- Competitive landscape analysis

The tool implements Buffett-style qualitative research patterns to complement
GuruFocus's quantitative financial data.

References:
- web_search_tool_spec.md (Complete specification)
- brave_search_api.md (API documentation)
- BUFFETT_PRINCIPLES.md (Economic moats, management quality)
"""

import os
import time
import logging
import re
from html import unescape
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests

from src.tools.base import Tool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """
    Web search tool using Brave Search API for qualitative investment research.

    Provides 3 search types:
    1. General - Standard web search (evergreen content, background research)
    2. News - News-focused search (current events, announcements)
    3. Recent - Last 30 days only (breaking news, latest developments)

    Key Features:
    - RAG-optimized snippets (extra_snippets) for AI agent context
    - Company context addition (automatically append company name)
    - Freshness filtering (day, week, month, year)
    - HTML cleaning and text normalization
    - Date parsing ("X days ago" → ISO format)
    - Domain extraction from URLs
    - Error handling with exponential backoff
    - Integration with GuruFocus for company context

    Search Types:
    - "general": Standard web search (default)
    - "news": News articles and press releases
    - "recent": Last 30 days only

    Freshness Filters:
    - "day": Last 24 hours
    - "week": Last 7 days
    - "month": Last 30 days
    - "year": Last 12 months
    """

    # API Configuration
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"
    TIMEOUT = 30  # seconds
    MAX_RETRIES = 3  # maximum retry attempts

    # Valid parameters
    VALID_SEARCH_TYPES = ["general", "news", "recent"]
    VALID_FRESHNESS = ["day", "week", "month", "year"]

    # Freshness mapping to Brave API format
    FRESHNESS_MAP = {
        "day": "pd",    # past day
        "week": "pw",   # past week
        "month": "pm",  # past month
        "year": "py"    # past year
    }

    def __init__(self):
        """
        Initialize Web Search Tool.

        Raises:
            ValueError: If BRAVE_SEARCH_API_KEY environment variable is not set
        """
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "BRAVE_SEARCH_API_KEY environment variable not set. "
                "Add to .env file: BRAVE_SEARCH_API_KEY=your_key_here"
            )

        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': self.api_key
        })

        logger.info("Web Search Tool initialized")

    @property
    def name(self) -> str:
        """Tool name for agent to reference"""
        return "web_search_tool"

    @property
    def description(self) -> str:
        """What this tool does (for agent decision-making)"""
        return (
            "Searches the web using Brave Search API for qualitative investment research: "
            "company news, management quality, economic moats, competitive landscape, "
            "and risk factors. Returns RAG-optimized snippets for AI analysis."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for tool parameters"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (1-400 characters)",
                    "minLength": 1,
                    "maxLength": 400
                },
                "company": {
                    "type": "string",
                    "description": "Company name for context (optional, auto-appended to query)"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (1-20, default: 10)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 10
                },
                "search_type": {
                    "type": "string",
                    "enum": self.VALID_SEARCH_TYPES,
                    "default": "general",
                    "description": "Type of search: general (evergreen), news (current), recent (30 days)"
                },
                "freshness": {
                    "type": "string",
                    "enum": self.VALID_FRESHNESS,
                    "description": "Filter by recency: day, week, month, year (optional)"
                }
            },
            "required": ["query"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute web search.

        Args:
            query: Search query string (required)
            company: Company name for context (optional)
            count: Number of results (optional, default: 10)
            search_type: Type of search (optional, default: "general")
            freshness: Freshness filter (optional): day, week, month, year

        Returns:
            Dict containing:
                - success: bool (whether search succeeded)
                - data: dict with:
                    - query: str (actual query sent to API)
                    - results: list of search results with:
                        - title: str
                        - url: str
                        - description: str
                        - age: str (e.g., "2 days ago")
                        - published_date: str (ISO format if parseable)
                        - source: str (domain name)
                        - extra_snippets: list (RAG-optimized snippets)
                    - total_results: int
                    - metadata: dict (source, search_type, timestamp, latency)
                - error: str or None

        Reference:
            web_search_tool_spec.md Section 3
            brave_search_api.md (API documentation)
        """
        start_time = time.time()

        # Extract and validate parameters
        query = kwargs.get("query", "").strip()
        company = kwargs.get("company")
        count = kwargs.get("count", 10)
        search_type = kwargs.get("search_type", "general").lower()
        freshness = kwargs.get("freshness", "").lower() if kwargs.get("freshness") else None

        # Validate query
        if not query:
            return self._error("Query cannot be empty")

        if len(query) > 400:
            return self._error("Query exceeds 400 character limit")

        # Validate count
        if count < 1 or count > 20:
            return self._error("Count must be between 1 and 20")

        # Validate search type
        if search_type not in self.VALID_SEARCH_TYPES:
            valid = ", ".join(self.VALID_SEARCH_TYPES)
            return self._error(f"Invalid search_type: '{search_type}'. Must be one of: {valid}")

        # Validate freshness if provided
        if freshness and freshness not in self.VALID_FRESHNESS:
            valid = ", ".join(self.VALID_FRESHNESS)
            return self._error(f"Invalid freshness: '{freshness}'. Must be one of: {valid}")

        # Construct full query with company context
        full_query = self._construct_query(query, company)

        logger.info(f"Executing {search_type} search: {full_query}")

        # Build API request parameters
        params = {
            "q": full_query,
            "count": count,
            "offset": 0,
            "extra_snippets": True,       # CRITICAL for RAG - enables additional snippets
            "text_decorations": False,    # No HTML in results
            "search_lang": "en",          # English results
            "country": "US",              # Default to US (can be customized later)
            "safesearch": "moderate"      # Content filtering
        }

        # Apply freshness filter
        if freshness:
            params["freshness"] = self.FRESHNESS_MAP[freshness]
        elif search_type == "recent":
            params["freshness"] = "pm"  # Default recent to past month

        # Apply search type filters
        if search_type == "news":
            params["result_filter"] = "news"

        # Execute search with retry logic
        try:
            api_data = self._execute_with_retry(params)
        except Exception as e:
            return self._error(f"Search failed: {str(e)}")

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Process results
        try:
            return self._process_response(api_data, full_query, search_type, latency_ms)
        except Exception as e:
            logger.error(f"Error processing search results: {str(e)}")
            return self._error(f"Error processing results: {str(e)}")

    # =========================================================================
    # QUERY CONSTRUCTION
    # =========================================================================

    def _construct_query(self, query: str, company: Optional[str]) -> str:
        """
        Construct effective search query with company context.

        Automatically appends company name to query for context if:
        - Company parameter is provided
        - Company name not already in query

        Args:
            query: Base search query
            company: Company name (optional)

        Returns:
            Full query string

        Reference:
            web_search_tool_spec.md Section 4.3 (Query Construction)
        """
        query = query.strip()

        # Add company for context if provided and not already present
        if company:
            company_lower = company.lower()
            query_lower = query.lower()

            # Check if company (or core part of company name) already in query
            # Handle cases like "Apple Inc" in query should match "Apple" company param
            company_core = company_lower.split()[0]  # Get first word of company name

            if company_lower not in query_lower and company_core not in query_lower:
                query = f"{query} {company}"
                logger.debug(f"Added company context: {company}")

        return query

    # =========================================================================
    # HTTP REQUEST HANDLING
    # =========================================================================

    def _execute_with_retry(
        self,
        params: Dict[str, Any],
        max_retries: int = MAX_RETRIES
    ) -> Dict[str, Any]:
        """
        Execute search with exponential backoff retry logic.

        Handles:
        - Network timeouts (retry up to 3 times)
        - Server errors (500/502/503, retry)
        - Rate limit errors (429, don't retry - it won't help)
        - Auth errors (401, don't retry)

        Args:
            params: Request parameters
            max_retries: Maximum number of retry attempts

        Returns:
            Dict: Parsed JSON response

        Raises:
            Exception: If all retries exhausted or unrecoverable error

        Reference:
            web_search_tool_spec.md Section 5 (Error Handling)
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.TIMEOUT
                )

                # Handle HTTP status codes
                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 401:
                    raise ValueError(
                        "Invalid Brave Search API key. Check BRAVE_SEARCH_API_KEY environment variable. "
                        "Get your key from: https://brave.com/search/api/"
                    )

                elif response.status_code == 429:
                    # Rate limit exceeded - don't retry
                    raise Exception(
                        "Rate limit exceeded. Check your Brave Search API plan. "
                        "Free tier: 2,000 calls/month. Consider upgrading to Pro AI ($25/month, 50K calls)."
                    )

                elif response.status_code >= 500:
                    # Server error - retry with exponential backoff
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning(
                            f"Server error ({response.status_code}). "
                            f"Retry {attempt + 1}/{max_retries} in {wait_time}s"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(
                            f"Brave Search API server error: {response.status_code}. "
                            "All retries exhausted."
                        )

                # Other HTTP errors
                raise Exception(f"Brave Search API error: {response.status_code} - {response.text[:200]}")

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request timeout. "
                        f"Retry {attempt + 1}/{max_retries} in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(
                        f"Request timeout after {self.TIMEOUT}s. All retries exhausted."
                    )

            except requests.exceptions.RequestException as e:
                # Network error - retry
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Network error: {str(e)}. "
                        f"Retry {attempt + 1}/{max_retries} in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Network error: {str(e)}. All retries exhausted.")

        raise Exception("Failed to fetch data after all retries")

    # =========================================================================
    # RESPONSE PROCESSING
    # =========================================================================

    def _process_response(
        self,
        api_data: Dict[str, Any],
        query: str,
        search_type: str,
        latency_ms: int
    ) -> Dict[str, Any]:
        """
        Process Brave Search API response into standardized format.

        Extracts web results, cleans HTML, parses dates, extracts domains,
        and organizes RAG-optimized snippets.

        Args:
            api_data: Raw API response from Brave Search
            query: Query that was executed
            search_type: Type of search performed
            latency_ms: API response latency

        Returns:
            Dict with standardized response format

        Reference:
            web_search_tool_spec.md Section 3 (Output Format)
        """
        # Extract web results
        web_results = api_data.get("web", {}).get("results", [])

        # Process each result
        processed_results = []
        for result in web_results:
            processed_result = {
                "title": self._clean_text(result.get("title", "")),
                "url": result.get("url", ""),
                "description": self._clean_text(result.get("description", "")),
                "age": result.get("age", ""),
                "published_date": self._parse_date(result.get("age", "")),
                "source": self._extract_domain(result.get("url", "")),
                "extra_snippets": [
                    self._clean_text(snippet)
                    for snippet in result.get("extra_snippets", [])
                ]
            }
            processed_results.append(processed_result)

        # Build standardized response
        return {
            "success": True,
            "data": {
                "query": query,
                "results": processed_results,
                "total_results": len(processed_results),
                "metadata": {
                    "source": "brave_search",
                    "search_type": search_type,
                    "timestamp": datetime.now().isoformat(),
                    "api_latency_ms": latency_ms
                }
            },
            "error": None
        }

    # =========================================================================
    # TEXT CLEANING
    # =========================================================================

    def _clean_text(self, text: str) -> str:
        """
        Clean HTML entities and normalize text.

        Handles:
        - HTML entity unescaping (&#39; → ', &amp; → &)
        - HTML tag removal (defensive, shouldn't be present with text_decorations=False)
        - Whitespace normalization

        Args:
            text: Raw text from API

        Returns:
            Cleaned text

        Reference:
            web_search_tool_spec.md Section 4.4 (HTML Cleaning)
        """
        if not text:
            return ""

        # Unescape HTML entities
        text = unescape(text)  # &#39; → ', &amp; → &, &quot; → "

        # Remove HTML tags (shouldn't be present, but defensive)
        text = re.sub(r'<[^>]+>', '', text)

        # Normalize whitespace (multiple spaces → single space)
        text = re.sub(r'\s+', ' ', text)

        # Trim leading/trailing whitespace
        return text.strip()

    # =========================================================================
    # DATE PARSING
    # =========================================================================

    def _parse_date(self, age_str: str) -> Optional[str]:
        """
        Convert relative date ("X days ago") to ISO format (YYYY-MM-DD).

        Brave Search returns relative dates like:
        - "2 hours ago"
        - "5 days ago"
        - "3 weeks ago"
        - "2 months ago"
        - "1 year ago"

        This method converts to ISO date format for standardization.

        Args:
            age_str: Relative age string from Brave Search

        Returns:
            ISO formatted date (YYYY-MM-DD) or None if unparseable

        Reference:
            web_search_tool_spec.md Section 4.4 (Date Parsing)

        Note:
            Month and year conversions are approximations:
            - 1 month ≈ 30 days
            - 1 year ≈ 365 days
        """
        if not age_str:
            return None

        # Parse "X hours/days/weeks/months/years ago"
        match = re.match(r'(\d+)\s+(hour|day|week|month|year)s?\s+ago', age_str.lower())

        if not match:
            return None

        amount = int(match.group(1))
        unit = match.group(2)

        now = datetime.now()

        # Convert to timedelta
        delta_map = {
            'hour': timedelta(hours=amount),
            'day': timedelta(days=amount),
            'week': timedelta(weeks=amount),
            'month': timedelta(days=amount * 30),    # Approximation
            'year': timedelta(days=amount * 365)     # Approximation
        }

        if unit in delta_map:
            date = now - delta_map[unit]
            return date.strftime('%Y-%m-%d')

        return None

    # =========================================================================
    # DOMAIN EXTRACTION
    # =========================================================================

    def _extract_domain(self, url: str) -> str:
        """
        Extract clean domain name from URL.

        Examples:
        - https://www.apple.com/newsroom/2024/... → apple.com
        - https://bloomberg.com/news/... → bloomberg.com
        - https://www.reuters.com/... → reuters.com

        Args:
            url: Full URL

        Returns:
            Clean domain name (no www. prefix)
        """
        if not url:
            return ""

        try:
            parsed = urlparse(url)
            domain = parsed.netloc

            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]

            return domain

        except Exception:
            return ""

    # =========================================================================
    # ERROR HANDLING
    # =========================================================================

    def _error(self, message: str) -> Dict[str, Any]:
        """
        Return standardized error response.

        Args:
            message: Error message

        Returns:
            Dict with success=False and error message
        """
        logger.error(f"Web Search Tool error: {message}")
        return {
            "success": False,
            "data": None,
            "error": message
        }


# Make tool available for import
__all__ = ["WebSearchTool"]
