"""
GuruFocus Tool

Module: src.tools.gurufocus_tool
Purpose: API integration tool for fetching financial data from GuruFocus Premium API
Status: Complete - Sprint 3, Phase 2
Created: 2025-10-30

This tool provides access to GuruFocus's comprehensive financial data including:
- Company summaries and key metrics
- Financial statements (10 years historical)
- Pre-calculated key ratios (Owner Earnings, ROIC, ROE, etc.)
- Valuation metrics and multiples

The tool implements the hybrid approach: returning both GuruFocus pre-calculated metrics
(for agent to use by default) and raw financial data (for verification via Calculator Tool).

References:
- gurufocus_tool_spec.md (Complete specification)
- gurufocus_api.md (API documentation)
- ARCHITECTURE_DECISION_HYBRID_APPROACH.md (Strategy)
"""

import os
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dotenv import load_dotenv
import requests

from src.tools.base import Tool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuruFocusTool(Tool):
    """
    GuruFocus API integration tool for fetching financial data.

    Provides 4 endpoints:
    1. Summary - Company overview, key metrics, profitability ratios
    2. Financials - Income statement, balance sheet, cash flow (10 years)
    3. Key Ratios - Pre-calculated metrics (Owner Earnings, ROIC, ROE, etc.)
    4. Valuation - Valuation multiples, DCF estimates, growth metrics

    Implements hybrid architecture:
    - Returns GuruFocus pre-calculated metrics (agent uses by default)
    - Also provides raw financial data (for Calculator Tool verification)
    - Detects special values (9999, 10000, 0) per GuruFocus API standards

    Rate limiting: Enforces 1.5 second minimum interval between requests
    """

    # API Configuration
    BASE_URL = "https://api.gurufocus.com/public/user"
    TIMEOUT = 30  # seconds
    MIN_INTERVAL = 1.5  # seconds between requests
    MAX_RETRIES = 3  # maximum retry attempts

    # Special value codes per gurufocus_api.md Section 3.2
    SPECIAL_VALUE_DATA_NA = 9999  # Data not available
    SPECIAL_VALUE_NO_DEBT = 10000  # No debt OR negative equity

    # Valid endpoints
    VALID_ENDPOINTS = ["summary", "financials", "keyratios", "valuation"]
    VALID_PERIODS = ["annual", "quarterly"]

    def __init__(self):
        """
        Initialize GuruFocus Tool.

        Raises:
            ValueError: If GURUFOCUS_API_KEY environment variable is not set
        """
        self.api_key = os.getenv("GURUFOCUS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GURUFOCUS_API_KEY environment variable not set. "
                "Add to .env file: GURUFOCUS_API_KEY=your_key_here"
            )

        # Rate limiting state
        self.last_request_time = 0.0

        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'basirah-agent/1.0'
        })

        logger.info("GuruFocus Tool initialized")

    @property
    def name(self) -> str:
        """Tool name for agent to reference"""
        return "gurufocus_tool"

    @property
    def description(self) -> str:
        """What this tool does (for agent decision-making)"""
        return (
            "Fetches comprehensive financial data from GuruFocus Premium API: "
            "company summaries, financial statements (10 years), "
            "pre-calculated key ratios (Owner Earnings, ROIC, ROE), "
            "and valuation metrics. Returns both pre-calculated metrics "
            "and raw financial data for verification."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for tool parameters"""
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')",
                    "pattern": "^[A-Z]{1,5}$"
                },
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint to fetch data from",
                    "enum": self.VALID_ENDPOINTS
                },
                "period": {
                    "type": "string",
                    "description": "Data period: annual or quarterly (default: annual)",
                    "enum": self.VALID_PERIODS,
                    "default": "annual"
                }
            },
            "required": ["ticker", "endpoint"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute GuruFocus API request.

        Args:
            ticker: Stock ticker symbol (required)
            endpoint: API endpoint (required): summary, financials, keyratios, or valuation
            period: Data period (optional): annual or quarterly (default: annual)

        Returns:
            Dict containing:
                - success: bool (whether request succeeded)
                - data: dict with:
                    - ticker: str
                    - company_name: str
                    - endpoint: str
                    - metrics: dict (pre-calculated GuruFocus metrics)
                    - financials: dict (raw financial data for verification)
                    - valuation: dict (valuation metrics if available)
                    - special_values_detected: list (flagged special values)
                    - metadata: dict (source, timestamp, period)
                - error: str or None

        Reference:
            gurufocus_tool_spec.md Section 3
            gurufocus_api.md (API documentation)
        """
        # Extract and validate parameters
        ticker = kwargs.get("ticker", "").upper()
        endpoint = kwargs.get("endpoint", "").lower()
        period = kwargs.get("period", "annual").lower()

        # Validate ticker
        if not ticker:
            return self._error("Missing required parameter: 'ticker'")
        if not ticker.isalpha() or len(ticker) > 5:
            return self._error(f"Invalid ticker format: '{ticker}'. Must be 1-5 uppercase letters.")

        # Validate endpoint
        if endpoint not in self.VALID_ENDPOINTS:
            valid = ", ".join(self.VALID_ENDPOINTS)
            return self._error(
                f"Invalid endpoint: '{endpoint}'. Must be one of: {valid}"
            )

        # Validate period
        if period not in self.VALID_PERIODS:
            valid = ", ".join(self.VALID_PERIODS)
            return self._error(
                f"Invalid period: '{period}'. Must be one of: {valid}"
            )

        # Enforce rate limiting
        self._enforce_rate_limit()

        # Construct URL
        url = f"{self.BASE_URL}/{self.api_key}/stock/{ticker}/{endpoint}"

        logger.info(f"Fetching {endpoint} data for {ticker}")

        # Make API request with retry logic
        try:
            api_data = self._make_request_with_retry(url, ticker, endpoint)
        except Exception as e:
            return self._error(f"API request failed: {str(e)}")

        # Extract company name
        company_name = self._extract_company_name(api_data, endpoint, ticker)

        # Process data based on endpoint
        try:
            if endpoint == "summary":
                processed_data = self._process_summary(api_data)
            elif endpoint == "financials":
                processed_data = self._process_financials(api_data, period)
            elif endpoint == "keyratios":
                processed_data = self._process_keyratios(api_data)
            elif endpoint == "valuation":
                processed_data = self._process_valuation(api_data)
            else:
                return self._error(f"Unknown endpoint: {endpoint}")
        except Exception as e:
            logger.error(f"Error processing {endpoint} data: {str(e)}")
            return self._error(f"Error processing data: {str(e)}")

        # Detect special values across all data
        special_values = self._detect_special_values(api_data)

        # Build response
        return {
            "success": True,
            "data": {
                "ticker": ticker,
                "company_name": company_name,
                "endpoint": endpoint,
                **processed_data,  # Includes metrics, financials, valuation
                "special_values_detected": special_values,
                "metadata": {
                    "source": "gurufocus",
                    "api_version": "v3",
                    "timestamp": datetime.now().isoformat(),
                    "period": period,
                    "url": url.replace(self.api_key, "***")  # Mask API key
                }
            },
            "error": None
        }

    # =========================================================================
    # RATE LIMITING
    # =========================================================================

    def _enforce_rate_limit(self) -> None:
        """
        Enforce minimum interval between API requests.

        GuruFocus requires 1.5 second minimum between requests to avoid throttling.

        Reference:
            gurufocus_api.md Section 2 (Rate Limits)
            gurufocus_tool_spec.md Section 4 (Rate Limiting)
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.MIN_INTERVAL:
            sleep_time = self.MIN_INTERVAL - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    # =========================================================================
    # HTTP REQUEST HANDLING
    # =========================================================================

    def _make_request_with_retry(self, url: str, ticker: str, endpoint: str) -> Dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry logic.

        Handles:
        - Network timeouts (retry up to 3 times)
        - Rate limit errors (429, exponential backoff: 2s, 4s, 8s)
        - Invalid ticker (404, no retry)
        - Server errors (500, retry)

        Args:
            url: Full API URL
            ticker: Stock ticker (for error messages)
            endpoint: API endpoint (for error messages)

        Returns:
            Dict: Parsed JSON response

        Raises:
            Exception: If all retries exhausted or unrecoverable error

        Reference:
            gurufocus_tool_spec.md Section 5 (Error Handling)
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=self.TIMEOUT)

                # Handle HTTP status codes
                if response.status_code == 404:
                    raise ValueError(
                        f"Ticker '{ticker}' not found in GuruFocus. "
                        "Verify ticker symbol is correct."
                    )

                elif response.status_code == 429:
                    # Rate limit exceeded
                    if attempt < self.MAX_RETRIES - 1:
                        wait_time = 2 ** (attempt + 1)  # 2s, 4s, 8s
                        logger.warning(
                            f"Rate limit exceeded (429). "
                            f"Retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(
                            "Rate limit exceeded. GuruFocus API requires minimum 1.5s between requests. "
                            "All retries exhausted."
                        )

                elif response.status_code == 401:
                    raise ValueError(
                        "Invalid GuruFocus API key. Check GURUFOCUS_API_KEY environment variable. "
                        "Get your key from: https://www.gurufocus.com/api.php"
                    )

                elif response.status_code >= 500:
                    # Server error, retry
                    if attempt < self.MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        logger.warning(
                            f"Server error ({response.status_code}). "
                            f"Retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(
                            f"GuruFocus API server error: {response.status_code}. "
                            "All retries exhausted."
                        )

                # Raise for other bad status codes
                response.raise_for_status()

                # Parse JSON
                data = response.json()

                logger.info(f"Successfully fetched {endpoint} data for {ticker}")
                return data

            except requests.exceptions.Timeout:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request timeout. "
                        f"Retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(
                        f"Request timeout after {self.TIMEOUT}s. All retries exhausted."
                    )

            except requests.exceptions.RequestException as e:
                # Network error, retry
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Network error: {str(e)}. "
                        f"Retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Network error: {str(e)}. All retries exhausted.")

        raise Exception("Failed to fetch data after all retries")

    # =========================================================================
    # DATA PROCESSING: SUMMARY ENDPOINT
    # =========================================================================

    def _process_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process summary endpoint data.

        Extracts:
        - Pre-calculated metrics (ROIC, ROE, ROA, margins)
        - Financial strength scores
        - Valuation ratios
        - Company general information

        Args:
            data: Raw API response from /summary endpoint

        Returns:
            Dict with structured summary data

        Reference:
            gurufocus_api.md Section 3.1 (Stock Summary)
        """
        metrics = {}
        financials = {}
        valuation = {}
        general = {}

        # Extract general company info
        if "general" in data:
            gen = data["general"]
            general = {
                "industry": gen.get("industry"),
                "sector": gen.get("sector"),
                "exchange": gen.get("exchange"),
                "currency": gen.get("currency"),
                "address": gen.get("address")
            }

        # Extract profitability metrics (pre-calculated by GuruFocus)
        if "profitability" in data:
            prof = data["profitability"]
            metrics["operating_margin"] = self._safe_float(prof.get("operating_margin"))
            metrics["net_margin"] = self._safe_float(prof.get("net_margin"))
            metrics["roic"] = self._safe_float(prof.get("roic"))
            metrics["roe"] = self._safe_float(prof.get("roe"))
            metrics["roa"] = self._safe_float(prof.get("roa"))

        # Extract financial strength
        if "financial_strength" in data:
            fs = data["financial_strength"]
            metrics["financial_strength_score"] = self._safe_float(fs.get("score"))
            metrics["cash_to_debt"] = self._safe_float(fs.get("cash_to_debt"))
            metrics["equity_to_asset"] = self._safe_float(fs.get("equity_to_asset"))
            metrics["debt_to_equity"] = self._safe_float(fs.get("debt_to_equity"))

        # Extract valuation ratios
        if "valuation" in data:
            val = data["valuation"]
            valuation = {
                "pe_ratio": self._safe_float(val.get("pe_ratio")),
                "pb_ratio": self._safe_float(val.get("pb_ratio")),
                "ps_ratio": self._safe_float(val.get("ps_ratio")),
                "peg_ratio": self._safe_float(val.get("peg_ratio")),
                "ev_ebitda": self._safe_float(val.get("ev_ebitda"))
            }

        # Extract current price from quote
        if "quote" in data:
            quote = data["quote"]
            valuation["price"] = self._safe_float(quote.get("price"))
            valuation["market_cap"] = self._safe_float(quote.get("market_cap"))
            valuation["volume"] = self._safe_float(quote.get("volume"))

        return {
            "metrics": metrics,
            "financials": financials,  # Empty for summary
            "valuation": valuation,
            "general": general,
            "raw_data": data  # Include full raw data for advanced use
        }

    # =========================================================================
    # DATA PROCESSING: FINANCIALS ENDPOINT
    # =========================================================================

    def _process_financials(self, data: Dict[str, Any], period: str) -> Dict[str, Any]:
        """
        Process financials endpoint data.

        Extracts raw financial statements for Owner Earnings and ROIC calculations:
        - Income statement (Net Income, Operating Income, D&A)
        - Balance sheet (Total Assets, Liabilities, Equity, Cash)
        - Cash flow (CapEx, Free Cash Flow)

        Args:
            data: Raw API response from /financials endpoint
            period: "annual" or "quarterly"

        Returns:
            Dict with structured financial data (10 years historical)

        Reference:
            gurufocus_api.md Section 3.2 (Financials)
            ARCHITECTURE_DECISION_HYBRID_APPROACH.md (Raw data for verification)
        """
        metrics = {}
        financials = {}

        # Navigate to financials data
        if "financials" not in data:
            return {"metrics": metrics, "financials": financials, "valuation": {}}

        fin_data = data["financials"]
        period_data = fin_data.get(period, fin_data.get("annual", {}))

        # Extract most recent year's key components for Owner Earnings
        if period_data:
            # Get fiscal years/quarters
            fiscal_period = period_data.get("Fiscal Year", period_data.get("Fiscal Quarter", []))

            if fiscal_period and len(fiscal_period) > 0:
                # Owner Earnings components (most recent)
                financials["net_income"] = self._safe_float_from_series(period_data.get("Net Income"), 0)
                financials["depreciation_amortization"] = self._safe_float_from_series(
                    period_data.get("Depreciation & Amortization"), 0
                )
                financials["capex"] = self._safe_float_from_series(period_data.get("Capital Expenditure"), 0)
                financials["free_cash_flow"] = self._safe_float_from_series(period_data.get("Free Cash Flow"), 0)

                # ROIC components (most recent)
                financials["operating_income"] = self._safe_float_from_series(period_data.get("Operating Income"), 0)
                financials["total_assets"] = self._safe_float_from_series(period_data.get("Total Assets"), 0)
                financials["total_liabilities"] = self._safe_float_from_series(period_data.get("Total Liabilities"), 0)
                financials["cash_equivalents"] = self._safe_float_from_series(
                    period_data.get("Cash and Cash Equivalents"), 0
                )
                financials["total_debt"] = self._safe_float_from_series(period_data.get("Total Debt"), 0)

                # Additional balance sheet items
                financials["stockholders_equity"] = self._safe_float_from_series(
                    period_data.get("Total Stockholders Equity"), 0
                )
                financials["revenue"] = self._safe_float_from_series(period_data.get("Revenue"), 0)

                # Calculate current liabilities (for ROIC invested capital)
                total_liab = financials.get("total_liabilities")
                total_debt = financials.get("total_debt")
                if total_liab is not None and total_debt is not None:
                    # Approximate: Current Liabilities ≈ Total Liabilities - Long-term Debt
                    # This is a simplification; GuruFocus may not provide exact breakdown
                    financials["current_liabilities"] = total_liab - total_debt

                # Store fiscal periods for reference
                financials["fiscal_periods"] = fiscal_period[:10]  # Up to 10 years

                # 10-year historical data for trends
                financials["historical"] = {
                    "net_income": self._extract_series(period_data.get("Net Income"), 10),
                    "revenue": self._extract_series(period_data.get("Revenue"), 10),
                    "operating_income": self._extract_series(period_data.get("Operating Income"), 10),
                    "free_cash_flow": self._extract_series(period_data.get("Free Cash Flow"), 10)
                }

        return {
            "metrics": metrics,  # Empty for financials endpoint
            "financials": financials,
            "valuation": {},
            "raw_data": period_data  # Include full raw data
        }

    # =========================================================================
    # DATA PROCESSING: KEY RATIOS ENDPOINT
    # =========================================================================

    def _process_keyratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process key ratios endpoint data.

        This is the MOST IMPORTANT endpoint for the hybrid approach.
        Returns GuruFocus's pre-calculated metrics that the agent uses by default.

        Extracts:
        - Pre-calculated ROIC, ROE, ROA (agent uses these)
        - Operating margins, net margins
        - Per-share values (EPS, FCF per share)
        - 10-year historical averages

        Args:
            data: Raw API response from /keyratios endpoint

        Returns:
            Dict with pre-calculated metrics and historical data

        Reference:
            gurufocus_api.md Section 3.3 (Key Ratios)
            ARCHITECTURE_DECISION_HYBRID_APPROACH.md (Primary data source)
        """
        metrics = {}
        financials = {}

        # Extract profitability ratios (pre-calculated by GuruFocus)
        if "profitability_ratios" in data:
            prof = data["profitability_ratios"]

            # Get most recent year (index 0)
            metrics["operating_margin"] = self._safe_float_from_series(prof.get("Operating Margin %"), 0)
            metrics["net_margin"] = self._safe_float_from_series(prof.get("Net Margin %"), 0)
            metrics["roe"] = self._safe_float_from_series(prof.get("ROE %"), 0)
            metrics["roa"] = self._safe_float_from_series(prof.get("ROA %"), 0)
            metrics["roic"] = self._safe_float_from_series(prof.get("ROIC %"), 0)

            # Convert percentages to decimals if needed
            # GuruFocus may return as percentage (25.3) or decimal (0.253)
            if metrics.get("roic") and metrics["roic"] > 1:
                metrics["roic"] = metrics["roic"] / 100
            if metrics.get("roe") and metrics["roe"] > 1:
                metrics["roe"] = metrics["roe"] / 100
            if metrics.get("roa") and metrics["roa"] > 1:
                metrics["roa"] = metrics["roa"] / 100
            if metrics.get("operating_margin") and metrics["operating_margin"] > 1:
                metrics["operating_margin"] = metrics["operating_margin"] / 100
            if metrics.get("net_margin") and metrics["net_margin"] > 1:
                metrics["net_margin"] = metrics["net_margin"] / 100

            # Calculate 10-year averages
            roic_series = self._extract_series(prof.get("ROIC %"), 10)
            roe_series = self._extract_series(prof.get("ROE %"), 10)
            if roic_series:
                # Convert to decimals if percentages
                roic_series = [r/100 if r > 1 else r for r in roic_series if r is not None]
                metrics["roic_10y_avg"] = sum(roic_series) / len(roic_series) if roic_series else None
            if roe_series:
                roe_series = [r/100 if r > 1 else r for r in roe_series if r is not None]
                metrics["roe_10y_avg"] = sum(roe_series) / len(roe_series) if roe_series else None

        # Extract per-share values
        if "keyratios_per_share" in data:
            ps = data["keyratios_per_share"]
            metrics["eps"] = self._safe_float_from_series(ps.get("Earnings per Share"), 0)
            metrics["revenue_per_share"] = self._safe_float_from_series(ps.get("Revenue per Share"), 0)
            metrics["book_value_per_share"] = self._safe_float_from_series(ps.get("Book Value per Share"), 0)
            metrics["fcf_per_share"] = self._safe_float_from_series(ps.get("Free Cash Flow per Share"), 0)
            metrics["dividends_per_share"] = self._safe_float_from_series(ps.get("Dividends per Share"), 0)

            # Calculate 10-year average FCF per share
            fcf_series = self._extract_series(ps.get("Free Cash Flow per Share"), 10)
            if fcf_series:
                fcf_series = [f for f in fcf_series if f is not None]
                metrics["fcf_per_share_10y_avg"] = sum(fcf_series) / len(fcf_series) if fcf_series else None

        # Extract valuation ratios
        valuation = {}
        if "valuation_ratios" in data:
            val = data["valuation_ratios"]
            valuation = {
                "pe_ratio": self._safe_float(val.get("P/E Ratio")),
                "pb_ratio": self._safe_float(val.get("P/B Ratio")),
                "ps_ratio": self._safe_float(val.get("P/S Ratio")),
                "peg_ratio": self._safe_float(val.get("PEG Ratio")),
                "ev_ebitda": self._safe_float(val.get("EV/EBITDA")),
                "price_to_fcf": self._safe_float(val.get("Price to Free Cash Flow"))
            }

        # Extract efficiency ratios
        if "efficiency_ratios" in data:
            eff = data["efficiency_ratios"]
            metrics["asset_turnover"] = self._safe_float(eff.get("Asset Turnover"))
            metrics["inventory_turnover"] = self._safe_float(eff.get("Inventory Turnover"))

        return {
            "metrics": metrics,
            "financials": financials,  # Empty for keyratios
            "valuation": valuation,
            "raw_data": data  # Include full raw data
        }

    # =========================================================================
    # DATA PROCESSING: VALUATION ENDPOINT
    # =========================================================================

    def _process_valuation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process valuation endpoint data.

        Extracts:
        - Valuation multiples (P/E, P/B, EV/EBITDA)
        - GuruFocus proprietary valuations (GF Value, DCF, Graham Number)
        - Growth metrics

        Args:
            data: Raw API response from /valuation endpoint

        Returns:
            Dict with valuation metrics

        Reference:
            gurufocus_api.md Section 3.4 (Valuation)
        """
        metrics = {}
        valuation = {}

        # Extract standard valuation multiples
        if "valuation" in data:
            val = data["valuation"]
            valuation = {
                "market_cap": self._safe_float(val.get("market_cap")),
                "enterprise_value": self._safe_float(val.get("enterprise_value")),
                "pe_ratio": self._safe_float(val.get("pe_ratio")),
                "forward_pe": self._safe_float(val.get("forward_pe")),
                "peg_ratio": self._safe_float(val.get("peg_ratio")),
                "ps_ratio": self._safe_float(val.get("ps_ratio")),
                "pb_ratio": self._safe_float(val.get("pb_ratio")),
                "ev_ebitda": self._safe_float(val.get("ev_ebitda")),
                "ev_sales": self._safe_float(val.get("ev_sales")),
                "price_to_fcf": self._safe_float(val.get("price_to_fcf"))
            }

        # Extract GuruFocus proprietary metrics
        if "gurufocus_metrics" in data:
            gf = data["gurufocus_metrics"]
            valuation["gf_value"] = self._safe_float(gf.get("gf_value"))
            valuation["current_price"] = self._safe_float(gf.get("current_price"))
            valuation["gf_value_rank"] = gf.get("gf_value_rank")
            valuation["graham_number"] = self._safe_float(gf.get("graham_number"))
            valuation["dcf_value"] = self._safe_float(gf.get("dcf_value"))
            valuation["median_ps_value"] = self._safe_float(gf.get("median_ps_value"))
            valuation["peter_lynch_fair_value"] = self._safe_float(gf.get("peter_lynch_fair_value"))

        # Extract growth metrics
        if "growth_metrics" in data:
            growth = data["growth_metrics"]
            metrics["revenue_growth_3y"] = self._safe_float(growth.get("revenue_growth_3y"))
            metrics["revenue_growth_5y"] = self._safe_float(growth.get("revenue_growth_5y"))
            metrics["eps_growth_3y"] = self._safe_float(growth.get("eps_growth_3y"))
            metrics["eps_growth_5y"] = self._safe_float(growth.get("eps_growth_5y"))
            metrics["fcf_growth_3y"] = self._safe_float(growth.get("fcf_growth_3y"))

        return {
            "metrics": metrics,
            "financials": {},  # Empty for valuation
            "valuation": valuation,
            "raw_data": data  # Include full raw data
        }

    # =========================================================================
    # SPECIAL VALUE DETECTION
    # =========================================================================

    def _detect_special_values(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recursively scan data for GuruFocus special value codes.

        Special values per gurufocus_api.md Section 3.2:
        - 9999: Data not available (flag as missing)
        - 10000: No debt OR negative equity (context-dependent interpretation)
        - 0: At loss or zero value (valid value, not flagged)

        Args:
            data: Raw API response data (any structure)

        Returns:
            List of dicts: [{"field": "path.to.field", "value": 9999, "meaning": "..."}]

        Reference:
            gurufocus_api.md Section 3.2 (Special Value Handling)
            gurufocus_tool_spec.md Section 3 (Special Values)
        """
        special_values = []

        def scan(obj: Any, path: str = "") -> None:
            """Recursive scanner for special values"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, (int, float)):
                        if value == self.SPECIAL_VALUE_DATA_NA:
                            special_values.append({
                                "field": new_path,
                                "value": self.SPECIAL_VALUE_DATA_NA,
                                "meaning": "Data not available"
                            })
                        elif value == self.SPECIAL_VALUE_NO_DEBT:
                            # Context-dependent meaning
                            meaning = "No debt" if "debt" in new_path.lower() else "No debt OR negative equity"
                            special_values.append({
                                "field": new_path,
                                "value": self.SPECIAL_VALUE_NO_DEBT,
                                "meaning": meaning
                            })
                    else:
                        scan(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan(item, f"{path}[{i}]")

        scan(data)

        if special_values:
            logger.info(f"Detected {len(special_values)} special values")

        return special_values

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _extract_company_name(self, data: Dict[str, Any], endpoint: str, ticker: str) -> str:
        """
        Extract company name from API response.

        Args:
            data: Raw API response
            endpoint: API endpoint used
            ticker: Stock ticker (fallback)

        Returns:
            Company name or ticker if not found
        """
        try:
            if endpoint == "summary" and "general" in data:
                return data["general"].get("name", ticker)
            elif "general" in data:
                return data["general"].get("name", ticker)
            else:
                return ticker
        except:
            return ticker

    def _safe_float(self, value: Any) -> Optional[float]:
        """
        Safely convert value to float, handling special values and errors.

        Args:
            value: Value to convert (may be str, int, float, None)

        Returns:
            Float value or None if invalid/special value
        """
        if value is None:
            return None

        # Handle string values
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return None

        # Handle special values
        if value == self.SPECIAL_VALUE_DATA_NA or value == self.SPECIAL_VALUE_NO_DEBT:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_float_from_series(self, series: Optional[List], index: int) -> Optional[float]:
        """
        Safely extract float from time series at given index.

        Args:
            series: List of values (time series)
            index: Index to extract (0 = most recent)

        Returns:
            Float value or None if invalid
        """
        if not series or not isinstance(series, list):
            return None
        if index >= len(series):
            return None

        return self._safe_float(series[index])

    def _extract_series(self, series: Optional[List], max_length: int) -> List[Optional[float]]:
        """
        Extract time series data up to max_length.

        Args:
            series: List of values (time series)
            max_length: Maximum number of values to extract

        Returns:
            List of float values (None for invalid values)
        """
        if not series or not isinstance(series, list):
            return []

        return [self._safe_float(v) for v in series[:max_length]]

    def _error(self, message: str) -> Dict[str, Any]:
        """
        Return standardized error response.

        Args:
            message: Error message

        Returns:
            Dict with success=False and error message
        """
        logger.error(f"GuruFocus Tool error: {message}")
        return {
            "success": False,
            "data": None,
            "error": message
        }


# Make tool available for import
__all__ = ["GuruFocusTool"]
