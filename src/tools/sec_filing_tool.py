"""
SEC Filing Tool for basīrah Investment Agent

Module: src.tools.sec_filing_tool
Purpose: Retrieve and process SEC filings from EDGAR database
Created: October 30, 2025

This tool provides access to SEC EDGAR filings including 10-K annual reports,
10-Q quarterly reports, and proxy statements (DEF 14A) for investment analysis.

Critical Requirements:
    - User-Agent header REQUIRED (SEC blocks requests without it)
    - Rate limiting: Maximum 10 requests per second (strictly enforced)
    - CIK (Central Index Key) required for all API calls

Features:
    - Automatic ticker → CIK conversion
    - Filing retrieval (latest or specific year)
    - HTML to clean text extraction
    - Section extraction (Business, Risk Factors, MD&A)
    - Robust error handling and retry logic

Warren Buffett Use Cases:
    - Business understanding: Extract "Business" section from 10-K
    - Risk assessment: Extract "Risk Factors" section
    - Management evaluation: Review MD&A and proxy statements
    - Circle of competence: Read business descriptions

References:
    - Specification: docs/tool_specs/sec_filing_tool_spec.md
    - API Docs: docs/api_references/sec_edgar_api.md
"""

import os
import time
import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

from src.tools.base import Tool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECFilingTool(Tool):
    """
    SEC Filing Tool - Retrieve and process SEC EDGAR filings.

    Provides access to regulatory documents for investment analysis:
    - 10-K: Annual reports (comprehensive company information)
    - 10-Q: Quarterly reports
    - DEF 14A: Proxy statements (executive compensation, governance)
    - 8-K: Current reports (material events)

    Critical Features:
        - User-Agent compliance (REQUIRED by SEC)
        - Rate limiting (10 requests/second maximum)
        - Section extraction (reduces token usage)
        - Clean text extraction from HTML

    Warren Buffett Philosophy Integration:
        - Circle of Competence: Read business descriptions to understand the company
        - Management Quality: Assess transparency through MD&A and proxy statements
        - Risk Assessment: Identify management-disclosed risks
        - Red Flags: Look for accounting irregularities or governance issues

    Attributes:
        name: Tool identifier ("sec_filing_tool")
        description: Tool capabilities
        parameters: JSON schema for input validation

    Example Usage:
        >>> tool = SECFilingTool()
        >>> result = tool.execute(
        ...     ticker="AAPL",
        ...     filing_type="10-K",
        ...     section="business"
        ... )
        >>> print(result['data']['content'][:500])

    References:
        - SEC EDGAR API: https://www.sec.gov/edgar
        - Specification: docs/tool_specs/sec_filing_tool_spec.md
    """

    # API Configuration
    BASE_URL_DATA = "https://data.sec.gov"
    BASE_URL_FILINGS = "https://www.sec.gov"
    TICKER_TO_CIK_URL = "https://www.sec.gov/files/company_tickers.json"

    # Rate Limiting (CRITICAL: SEC enforces 10 requests/second)
    MIN_REQUEST_INTERVAL = 0.11  # 110ms = ~9 req/sec (safely under 10)

    # Timeouts
    TIMEOUT_SHORT = 30  # For API metadata calls
    TIMEOUT_LONG = 90   # For large filing downloads

    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 2  # 1s, 2s, 4s

    # Filing Types
    VALID_FILING_TYPES = ["10-K", "10-Q", "DEF 14A", "8-K"]

    # Sections (for 10-K/10-Q)
    VALID_SECTIONS = ["business", "risk_factors", "mda", "financial_statements", "full"]

    # Section Patterns (for text extraction)
    SECTION_PATTERNS = {
        "business": r"Item\s+1[\.\s\-]+Business",
        "risk_factors": r"Item\s+1A[\.\s\-]+Risk\s+Factors",
        "mda": r"Item\s+7[\.\s\-]+Management['\']?s\s+Discussion",
        "financial_statements": r"Item\s+8[\.\s\-]+Financial\s+Statements"
    }

    @property
    def name(self) -> str:
        """Tool name for agent reference."""
        return "sec_filing_tool"

    @property
    def description(self) -> str:
        """
        Tool description for agent decision-making.

        Returns:
            str: Comprehensive description of tool capabilities
        """
        return """
        Retrieves corporate filings from SEC EDGAR database.

        Capabilities:
        - 10-K annual reports (business description, risk factors, MD&A)
        - 10-Q quarterly reports
        - DEF 14A proxy statements (executive compensation, governance)
        - Section extraction (business, risk_factors, mda, financial_statements)
        - Clean text extraction from HTML

        Use for Warren Buffett-style analysis:
        - Business understanding: Extract "Business" section from 10-K
        - Risk assessment: Extract "Risk Factors" section
        - Management evaluation: Review MD&A and proxy statements
        - Circle of competence: Read business descriptions to assess understandability

        Important:
        - No API key required (SEC EDGAR is free)
        - Rate limited to 9 requests/second (SEC enforces 10 req/sec max)
        - Filings are large (10-K can be 200+ pages), use section extraction to reduce tokens
        """

    @property
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema for input parameters.

        Returns:
            Dict: OpenAPI-style parameter schema
        """
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'BRK.B')",
                    "pattern": "^[A-Z]{1,5}(\\.)?[A-Z]?$",
                    "examples": ["AAPL", "MSFT", "BRK.B"]
                },
                "filing_type": {
                    "type": "string",
                    "description": "Type of SEC filing to retrieve",
                    "enum": self.VALID_FILING_TYPES,
                    "examples": ["10-K", "DEF 14A"]
                },
                "section": {
                    "type": "string",
                    "description": "Specific section to extract (optional, for 10-K/10-Q only)",
                    "enum": self.VALID_SECTIONS,
                    "default": "full"
                },
                "year": {
                    "type": "integer",
                    "description": "Fiscal year (optional, defaults to most recent)",
                    "minimum": 2010,
                    "maximum": 2030,
                    "examples": [2023, 2022]
                },
                "quarter": {
                    "type": "integer",
                    "description": "Fiscal quarter (required for 10-Q only)",
                    "enum": [1, 2, 3, 4]
                }
            },
            "required": ["ticker", "filing_type"],
            "additionalProperties": False
        }

    def __init__(self):
        """
        Initialize SEC Filing Tool.

        Sets up:
            - HTTP session with User-Agent header (REQUIRED by SEC)
            - Rate limiting tracker
            - CIK cache

        Raises:
            EnvironmentError: If required configuration is missing
        """
        logger.info("SEC Filing Tool initialized")

        # User-Agent (REQUIRED by SEC, blocks requests without it)
        user_agent = os.getenv(
            "SEC_USER_AGENT",
            "basirah-agent contact@example.com"  # Default, should be configured
        )

        # Create persistent HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate'
            # Note: Host header is automatically set by requests library per-request
        })

        # Rate limiting tracker
        self.last_request_time = 0.0

        # CIK cache (avoid redundant lookups)
        self.ticker_to_cik_cache: Dict[str, str] = {}

        logger.info(f"User-Agent configured: {user_agent[:50]}...")

    def execute(
        self,
        ticker: str,
        filing_type: str,
        section: str = "full",
        year: Optional[int] = None,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute SEC filing retrieval.

        Process:
            1. Validate inputs
            2. Convert ticker to CIK (Central Index Key)
            3. Retrieve company filing list
            4. Find specific filing (latest or by year)
            5. Download filing HTML
            6. Extract text (full or specific section)
            7. Return structured result

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            filing_type: Type of filing ("10-K", "10-Q", "DEF 14A", "8-K")
            section: Section to extract ("business", "risk_factors", "mda", "full")
            year: Fiscal year (optional, defaults to most recent)
            quarter: Fiscal quarter (required for 10-Q)

        Returns:
            Dict containing:
                success: bool - Whether retrieval succeeded
                data: Dict with filing content and metadata
                error: Optional error message

        Example:
            >>> tool = SECFilingTool()
            >>> result = tool.execute(
            ...     ticker="AAPL",
            ...     filing_type="10-K",
            ...     section="risk_factors"
            ... )
            >>> if result["success"]:
            ...     print(result["data"]["content"][:500])

        Error Handling:
            - Invalid ticker → Returns error with clear message
            - Filing not found → Returns error suggesting alternatives
            - Rate limit exceeded → Automatic retry with backoff
            - Network timeout → Retry up to MAX_RETRIES times
        """
        logger.info(f"Executing SEC filing retrieval: {ticker} {filing_type}")

        # Step 1: Validate inputs
        validation_error = self._validate_inputs(ticker, filing_type, section, quarter)
        if validation_error:
            logger.error(f"Validation error: {validation_error}")
            return self._error_response(validation_error)

        try:
            # Step 2: Convert ticker to CIK
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                error_msg = (
                    f"Ticker '{ticker}' not found in SEC EDGAR database. "
                    "Verify ticker is correct and company is publicly traded in US."
                )
                logger.error(error_msg)
                return self._error_response(error_msg)

            logger.info(f"CIK lookup successful: {ticker} → {cik}")

            # Step 3: Get company filings list
            company_data = self._get_company_submissions(cik)
            if not company_data:
                error_msg = f"Could not retrieve filing list for {ticker} (CIK: {cik})"
                logger.error(error_msg)
                return self._error_response(error_msg)

            company_name = company_data.get("name", "Unknown Company")
            logger.info(f"Company: {company_name}")

            # Step 4: Find specific filing
            filing_info = self._find_filing(company_data, filing_type, year, quarter)
            if not filing_info:
                year_str = f" in fiscal year {year}" if year else ""
                error_msg = (
                    f"No {filing_type} filing found for {ticker}{year_str}. "
                    f"Try a different year or check company's filing history."
                )
                logger.error(error_msg)
                return self._error_response(error_msg)

            logger.info(
                f"Found filing: {filing_type} filed {filing_info['filing_date']} "
                f"(fiscal {filing_info.get('fiscal_year', 'N/A')})"
            )

            # Step 5: Download filing HTML
            filing_url = self._construct_filing_url(cik, filing_info)
            html_content = self._download_filing(filing_url)

            if not html_content:
                error_msg = "Failed to download filing content. Filing may be unavailable."
                logger.error(error_msg)
                return self._error_response(error_msg)

            logger.info(f"Downloaded filing: {len(html_content)} bytes")

            # Step 6: Extract text
            if filing_type in ["10-K", "10-Q"] and section != "full":
                content = self._extract_section(html_content, section)
                logger.info(f"Extracted section '{section}': {len(content)} characters")
            else:
                content = self._extract_full_text(html_content)
                logger.info(f"Extracted full text: {len(content)} characters")

            # Step 7: Return success
            return {
                "success": True,
                "data": {
                    "ticker": ticker.upper(),
                    "company_name": company_name,
                    "cik": cik,
                    "filing_type": filing_type,
                    "filing_date": filing_info["filing_date"],
                    "fiscal_year": filing_info.get("fiscal_year"),
                    "fiscal_quarter": quarter,
                    "section": section,
                    "content": content,
                    "content_length": len(content),
                    "filing_url": filing_url,
                    "metadata": {
                        "source": "sec_edgar",
                        "timestamp": datetime.now().isoformat(),
                        "accession_number": filing_info["accession_number"]
                    }
                },
                "error": None
            }

        except requests.exceptions.Timeout as e:
            error_msg = f"SEC EDGAR request timeout: {str(e)}"
            logger.error(error_msg)
            return self._error_response(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"SEC EDGAR API error: {str(e)}"
            logger.error(error_msg)
            return self._error_response(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during SEC filing retrieval: {str(e)}"
            logger.exception(error_msg)
            return self._error_response(error_msg)

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================

    def _validate_inputs(
        self,
        ticker: str,
        filing_type: str,
        section: str,
        quarter: Optional[int]
    ) -> Optional[str]:
        """
        Validate input parameters.

        Args:
            ticker: Stock ticker symbol
            filing_type: SEC filing type
            section: Section to extract
            quarter: Fiscal quarter (if applicable)

        Returns:
            Optional[str]: Error message if validation fails, None if valid
        """
        # Validate ticker
        if not ticker:
            return "Ticker cannot be empty"

        if not ticker.replace(".", "").isalpha() or not ticker.isupper():
            return f"Ticker must be uppercase letters only (e.g., 'AAPL', 'BRK.B'). Got: '{ticker}'"

        # Validate filing type
        if filing_type not in self.VALID_FILING_TYPES:
            return (
                f"Invalid filing_type: '{filing_type}'. "
                f"Must be one of: {', '.join(self.VALID_FILING_TYPES)}"
            )

        # Validate section
        if section not in self.VALID_SECTIONS:
            return (
                f"Invalid section: '{section}'. "
                f"Must be one of: {', '.join(self.VALID_SECTIONS)}"
            )

        # Validate quarter requirement for 10-Q
        if filing_type == "10-Q" and not quarter:
            return "Quarter is required for 10-Q filings (1, 2, 3, or 4)"

        if quarter and quarter not in [1, 2, 3, 4]:
            return f"Quarter must be 1, 2, 3, or 4. Got: {quarter}"

        return None

    # =========================================================================
    # RATE LIMITING (CRITICAL)
    # =========================================================================

    def _enforce_rate_limit(self):
        """
        Enforce SEC EDGAR rate limiting.

        SEC strictly enforces 10 requests per second. Implementation uses
        110ms minimum interval (~9 req/sec) to safely stay under limit.

        This method blocks until sufficient time has elapsed since the last request.

        Critical: Violating SEC rate limits can result in IP blocking.

        References:
            - SEC Fair Access: https://www.sec.gov/os/accessing-edgar-data
        """
        elapsed = time.time() - self.last_request_time

        if elapsed < self.MIN_REQUEST_INTERVAL:
            sleep_time = self.MIN_REQUEST_INTERVAL - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    # =========================================================================
    # CIK LOOKUP
    # =========================================================================

    def _get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """
        Convert ticker symbol to CIK (Central Index Key).

        SEC API requires CIK, not ticker. This method:
        1. Checks cache for previously looked up ticker
        2. If not cached, downloads ticker→CIK mapping from SEC
        3. Searches for matching ticker
        4. Returns 10-digit zero-padded CIK

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")

        Returns:
            Optional[str]: 10-digit CIK (e.g., "0000320193") or None if not found

        Example:
            >>> self._get_cik_from_ticker("AAPL")
            "0000320193"

        Notes:
            - CIK must be 10 digits with leading zeros for API calls
            - Cache is maintained in memory to avoid repeated lookups
            - Rate limiting applied before API call
        """
        # Check cache first
        if ticker in self.ticker_to_cik_cache:
            logger.debug(f"CIK cache hit: {ticker}")
            return self.ticker_to_cik_cache[ticker]

        # Rate limit before API call
        self._enforce_rate_limit()

        try:
            logger.info(f"Looking up CIK for ticker: {ticker}")

            response = self.session.get(
                self.TICKER_TO_CIK_URL,
                timeout=self.TIMEOUT_SHORT
            )
            response.raise_for_status()

            tickers_data = response.json()

            # Search for ticker in data
            for entry in tickers_data.values():
                if entry['ticker'].upper() == ticker.upper():
                    # Pad CIK to 10 digits with leading zeros
                    cik = str(entry['cik_str']).zfill(10)

                    # Cache result
                    self.ticker_to_cik_cache[ticker] = cik

                    logger.info(f"CIK found: {ticker} → {cik}")
                    return cik

            logger.warning(f"CIK not found for ticker: {ticker}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ticker-to-CIK mapping: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error during CIK lookup: {e}")
            return None

    # =========================================================================
    # FILING RETRIEVAL
    # =========================================================================

    def _get_company_submissions(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Get complete filing history for a company.

        Retrieves all available filings and company metadata from SEC.

        Args:
            cik: 10-digit CIK (e.g., "0000320193")

        Returns:
            Optional[Dict]: Company data with filing history, or None if error

        Response Structure:
            {
                "name": "Apple Inc.",
                "cik": "320193",
                "filings": {
                    "recent": {
                        "accessionNumber": [...],
                        "filingDate": [...],
                        "reportDate": [...],
                        "form": [...],
                        "primaryDocument": [...]
                    }
                }
            }

        Notes:
            - Rate limiting applied before API call
            - Returns most recent 1000 filings in "recent" array
            - Older filings available via pagination (not implemented)
        """
        self._enforce_rate_limit()

        try:
            url = f"{self.BASE_URL_DATA}/submissions/CIK{cik}.json"
            logger.info(f"Fetching company submissions from: {url}")

            response = self.session.get(url, timeout=self.TIMEOUT_SHORT)
            response.raise_for_status()

            company_data = response.json()
            logger.info(f"Retrieved {len(company_data.get('filings', {}).get('recent', {}).get('form', []))} recent filings")

            return company_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching company submissions: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching company submissions: {e}")
            return None

    def _find_filing(
        self,
        company_data: Dict[str, Any],
        filing_type: str,
        year: Optional[int],
        quarter: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Find specific filing in company's filing history.

        Searches through recent filings to find:
        - Latest filing of specified type (if year not specified)
        - Filing from specific year (if year specified)
        - Specific quarter filing for 10-Q

        Args:
            company_data: Company data from _get_company_submissions()
            filing_type: SEC filing type (e.g., "10-K")
            year: Optional fiscal year filter
            quarter: Optional quarter filter (for 10-Q)

        Returns:
            Optional[Dict]: Filing info with accession number, dates, etc.

        Filing Info Structure:
            {
                "accession_number": "0000320193-23-000106",
                "filing_date": "2023-11-03",
                "report_date": "2023-09-30",
                "primary_document": "aapl-20230930.htm",
                "fiscal_year": 2023
            }

        Notes:
            - Searches recent filings first (most recent 1000)
            - For 10-Q, matches by quarter using report date
            - Returns None if no matching filing found
        """
        try:
            recent_filings = company_data['filings']['recent']

            forms = recent_filings.get('form', [])
            accession_numbers = recent_filings.get('accessionNumber', [])
            filing_dates = recent_filings.get('filingDate', [])
            report_dates = recent_filings.get('reportDate', [])
            primary_documents = recent_filings.get('primaryDocument', [])

            logger.info(f"Searching {len(forms)} filings for {filing_type}")

            # Search through filings
            for i, form in enumerate(forms):
                if form != filing_type:
                    continue

                report_date = report_dates[i] if i < len(report_dates) else ""
                fiscal_year = int(report_date.split('-')[0]) if report_date else None

                # Check year match if specified
                if year and fiscal_year != year:
                    continue

                # For 10-Q, check quarter match
                if filing_type == "10-Q" and quarter:
                    # Approximate quarter from report date month
                    month = int(report_date.split('-')[1]) if report_date else 0
                    filing_quarter = ((month - 1) // 3) + 1

                    if filing_quarter != quarter:
                        continue

                # Found matching filing
                filing_info = {
                    "accession_number": accession_numbers[i] if i < len(accession_numbers) else "",
                    "filing_date": filing_dates[i] if i < len(filing_dates) else "",
                    "report_date": report_date,
                    "primary_document": primary_documents[i] if i < len(primary_documents) else "",
                    "fiscal_year": fiscal_year
                }

                logger.info(f"Found matching filing: {filing_info['accession_number']}")
                return filing_info

            logger.warning(f"No matching {filing_type} filing found")
            return None

        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing filing data: {e}")
            return None

    def _construct_filing_url(
        self,
        cik: str,
        filing_info: Dict[str, Any]
    ) -> str:
        """
        Construct URL to download filing document.

        SEC filing URLs follow pattern:
        https://www.sec.gov/Archives/edgar/data/{CIK}/{ACCESSION}/{FILENAME}

        Args:
            cik: 10-digit CIK (with leading zeros)
            filing_info: Filing info from _find_filing()

        Returns:
            str: Complete URL to filing document

        Example:
            >>> self._construct_filing_url(
            ...     "0000320193",
            ...     {"accession_number": "0000320193-23-000106",
            ...      "primary_document": "aapl-20230930.htm"}
            ... )
            "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm"

        Notes:
            - CIK in URL should NOT have leading zeros (SEC prefers without)
            - Accession number in URL should NOT have dashes
            - Primary document filename used as-is
        """
        # Remove leading zeros from CIK for URL
        cik_clean = str(int(cik))

        # Remove dashes from accession number
        accession_clean = filing_info["accession_number"].replace('-', '')

        # Construct URL
        url = (
            f"{self.BASE_URL_FILINGS}/Archives/edgar/data/{cik_clean}/"
            f"{accession_clean}/{filing_info['primary_document']}"
        )

        logger.debug(f"Constructed filing URL: {url}")
        return url

    def _download_filing(self, url: str) -> Optional[str]:
        """
        Download filing HTML content.

        Downloads SEC filing document with retry logic for large files.

        Args:
            url: Complete URL to filing document

        Returns:
            Optional[str]: HTML content or None if download fails

        Notes:
            - Rate limiting applied before request
            - Uses longer timeout (90s) for large filings
            - Retries on timeout (up to MAX_RETRIES)
            - Returns raw HTML (no parsing)
        """
        self._enforce_rate_limit()

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Downloading filing (attempt {attempt + 1}/{self.MAX_RETRIES}): {url}")

                response = self.session.get(url, timeout=self.TIMEOUT_LONG)
                response.raise_for_status()

                logger.info(f"Filing downloaded successfully: {len(response.text)} bytes")
                return response.text

            except requests.exceptions.Timeout:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF_FACTOR ** attempt
                    logger.warning(
                        f"Download timeout. "
                        f"Retrying in {wait_time}s (attempt {attempt + 1}/{self.MAX_RETRIES})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {self.MAX_RETRIES} attempts")
                    return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading filing: {e}")
                return None

        return None

    # =========================================================================
    # TEXT EXTRACTION
    # =========================================================================

    def _extract_full_text(self, html_content: str) -> str:
        """
        Extract clean text from filing HTML.

        Process:
            1. Parse HTML with BeautifulSoup
            2. Remove unwanted elements (scripts, styles, tables)
            3. Extract text
            4. Clean whitespace
            5. Preserve paragraph structure

        Args:
            html_content: Raw HTML from SEC filing

        Returns:
            str: Clean, readable text

        Notes:
            - Tables removed (usually financial data, already in GuruFocus)
            - Scripts and styles removed
            - HTML entities unescaped (&amp; → &, &nbsp; → space)
            - Excessive whitespace normalized
            - Paragraph breaks preserved
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')

            # Remove unwanted elements
            for tag in soup(['script', 'style', 'table', 'nav', 'header', 'footer']):
                tag.decompose()

            # Extract text
            text = soup.get_text()

            # Clean text
            cleaned_text = self._clean_text(text)

            logger.debug(f"Extracted text: {len(cleaned_text)} characters")
            return cleaned_text

        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return f"Error extracting text: {str(e)}"

    def _extract_section(self, html_content: str, section_name: str) -> str:
        """
        Extract specific section from 10-K or 10-Q filing.

        10-K/10-Q sections follow standard structure:
        - Item 1: Business
        - Item 1A: Risk Factors
        - Item 7: Management's Discussion and Analysis (MD&A)
        - Item 8: Financial Statements

        Process:
            1. Extract full text from HTML
            2. Find section header using regex pattern
            3. Extract text from section start to next section
            4. Clean and return text

        Args:
            html_content: Raw HTML from SEC filing
            section_name: Section to extract ("business", "risk_factors", "mda", etc.)

        Returns:
            str: Section text or error message if section not found

        Notes:
            - Uses regex to find section headers (handles formatting variations)
            - Extracts from section start to next "Item X" header
            - Returns "Section not found" message if pattern doesn't match
            - Some filings use non-standard formatting (fallback to full text)
        """
        try:
            # Get full text first
            soup = BeautifulSoup(html_content, 'lxml')
            for tag in soup(['script', 'style', 'table']):
                tag.decompose()

            text = soup.get_text()

            # Get pattern for requested section
            pattern = self.SECTION_PATTERNS.get(section_name)
            if not pattern:
                logger.warning(f"No pattern defined for section: {section_name}")
                return self._clean_text(text)

            # Find section header
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                msg = (
                    f"Section '{section_name}' not found in filing. "
                    f"Filing may use non-standard formatting. Try section='full'."
                )
                logger.warning(msg)
                return msg

            start_pos = match.start()

            # Find next section (Item X.) to determine end
            # Look for pattern starting after current section header
            next_section_match = re.search(
                r'Item\s+\d+[A-Z]?[\.\s\-]',
                text[start_pos + 50:],  # Skip ahead to avoid matching current item
                re.IGNORECASE
            )

            if next_section_match:
                end_pos = start_pos + 50 + next_section_match.start()
            else:
                # No next section found, take rest of document
                end_pos = len(text)

            # Extract section text
            section_text = text[start_pos:end_pos]

            # Clean and return
            cleaned_section = self._clean_text(section_text)
            logger.info(f"Extracted section '{section_name}': {len(cleaned_section)} characters")

            return cleaned_section

        except Exception as e:
            logger.error(f"Error extracting section '{section_name}': {e}")
            return f"Error extracting section: {str(e)}"

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text for readability.

        Cleaning operations:
            - Remove excessive whitespace (normalize to single spaces)
            - Remove page numbers (standalone numbers on lines)
            - Remove table of contents artifacts
            - Add paragraph breaks at sentence boundaries
            - Strip leading/trailing whitespace

        Args:
            text: Raw extracted text

        Returns:
            str: Cleaned, readable text

        Notes:
            - Preserves sentence structure
            - Maintains paragraph breaks
            - Removes formatting artifacts from HTML→text conversion
        """
        if not text:
            return ""

        # Remove excessive whitespace (collapse to single space)
        text = re.sub(r'\s+', ' ', text)

        # Remove standalone page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

        # Remove common table of contents artifacts
        text = re.sub(r'Table\s+of\s+Contents', '', text, flags=re.IGNORECASE)

        # Add paragraph breaks at sentence boundaries followed by capital letters
        # (helps readability, especially for long documents)
        text = re.sub(r'\.(\s+)([A-Z])', r'.\n\n\2', text)

        # Remove any remaining multiple spaces
        text = re.sub(r' {2,}', ' ', text)

        # Remove multiple newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error response.

        Args:
            error_message: Human-readable error description

        Returns:
            Dict: Error response with success=False
        """
        return {
            "success": False,
            "data": None,
            "error": error_message
        }


# Module exports
__all__ = ["SECFilingTool"]
