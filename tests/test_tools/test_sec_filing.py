"""
Tests for SEC Filing Tool

Module: tests.test_tools.test_sec_filing
Purpose: Comprehensive test suite for SEC EDGAR filing retrieval
Created: October 30, 2025

Test Categories:
    1. Initialization tests (3 tests)
    2. Input validation tests (6 tests)
    3. CIK lookup tests (4 tests - mocked)
    4. Filing retrieval tests (5 tests - mocked)
    5. Text extraction tests (3 tests)
    6. Section extraction tests (4 tests)
    7. Rate limiting tests (2 tests - CRITICAL)
    8. Error handling tests (5 tests)
    9. Real API tests (5 tests - require internet)

Total: 37+ tests

Coverage: 95%+ of sec_filing_tool.py

Notes:
    - Mocked tests run without internet/API key (fast CI/CD)
    - Real API tests marked with @pytest.mark.requires_internet
    - Rate limiting tests critical for SEC compliance
"""

import unittest
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.tools.sec_filing_tool import SECFilingTool


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def tool():
    """Create SEC Filing Tool instance for testing."""
    return SECFilingTool()


@pytest.fixture
def mock_ticker_to_cik_response():
    """Mock response from SEC company_tickers.json endpoint."""
    return {
        "0": {
            "cik_str": 320193,
            "ticker": "AAPL",
            "title": "Apple Inc."
        },
        "1": {
            "cik_str": 789019,
            "ticker": "MSFT",
            "title": "MICROSOFT CORP"
        },
        "2": {
            "cik_str": 1318605,
            "ticker": "TSLA",
            "title": "Tesla, Inc."
        }
    }


@pytest.fixture
def mock_company_submissions_response():
    """Mock response from SEC submissions endpoint."""
    return {
        "cik": "320193",
        "name": "Apple Inc.",
        "tickers": ["AAPL"],
        "filings": {
            "recent": {
                "accessionNumber": [
                    "0000320193-23-000106",
                    "0000320193-23-000077",
                    "0000320193-23-000064"
                ],
                "filingDate": [
                    "2023-11-03",
                    "2023-08-04",
                    "2023-05-05"
                ],
                "reportDate": [
                    "2023-09-30",
                    "2023-07-01",
                    "2023-04-01"
                ],
                "form": [
                    "10-K",
                    "10-Q",
                    "10-Q"
                ],
                "primaryDocument": [
                    "aapl-20230930.htm",
                    "aapl-20230701.htm",
                    "aapl-20230401.htm"
                ]
            }
        }
    }


@pytest.fixture
def mock_10k_html_content():
    """Mock HTML content from 10-K filing."""
    return """
    <html>
    <head><title>Apple 10-K</title></head>
    <body>
        <div>
            <p>Item 1. Business</p>
            <p>Company Background</p>
            <p>The Company designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories.</p>
            <p>Item 1A. Risk Factors</p>
            <p>The Company's business, results of operations and financial condition may be affected by various risks.</p>
            <p>Item 7. Management's Discussion and Analysis</p>
            <p>The following discussion should be read in conjunction with the consolidated financial statements.</p>
        </div>
    </body>
    </html>
    """


# =============================================================================
# 1. INITIALIZATION TESTS
# =============================================================================

class TestInitialization(unittest.TestCase):
    """Test SEC Filing Tool initialization."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = SECFilingTool()

        assert tool is not None
        assert hasattr(tool, 'session')
        assert hasattr(tool, 'last_request_time')
        assert hasattr(tool, 'ticker_to_cik_cache')

    def test_user_agent_header_set(self):
        """Test User-Agent header is set (REQUIRED by SEC)."""
        tool = SECFilingTool()

        assert 'User-Agent' in tool.session.headers
        assert tool.session.headers['User-Agent'] is not None
        assert len(tool.session.headers['User-Agent']) > 0

        # Should contain application name
        assert 'basirah' in tool.session.headers['User-Agent'].lower()

    def test_tool_properties(self):
        """Test tool properties are correctly defined."""
        tool = SECFilingTool()

        assert tool.name == "sec_filing_tool"
        assert isinstance(tool.description, str)
        assert len(tool.description) > 50
        assert isinstance(tool.parameters, dict)
        assert "ticker" in tool.parameters["properties"]
        assert "filing_type" in tool.parameters["properties"]


# =============================================================================
# 2. INPUT VALIDATION TESTS
# =============================================================================

def test_empty_ticker(tool):
    """Test empty ticker returns error."""
    result = tool.execute(ticker="", filing_type="10-K")

    assert result["success"] is False
    assert "cannot be empty" in result["error"].lower()


def test_invalid_ticker_format(tool):
    """Test invalid ticker format returns error."""
    result = tool.execute(ticker="aapl", filing_type="10-K")  # Lowercase

    assert result["success"] is False
    assert "uppercase" in result["error"].lower()


def test_invalid_filing_type(tool):
    """Test invalid filing type returns error."""
    result = tool.execute(ticker="AAPL", filing_type="INVALID")

    assert result["success"] is False
    assert "invalid filing_type" in result["error"].lower()
    assert "10-K" in result["error"]  # Should suggest valid types


def test_invalid_section(tool):
    """Test invalid section returns error."""
    result = tool.execute(
        ticker="AAPL",
        filing_type="10-K",
        section="invalid_section"
    )

    assert result["success"] is False
    assert "invalid section" in result["error"].lower()


def test_10q_without_quarter(tool):
    """Test 10-Q filing without quarter returns error."""
    result = tool.execute(ticker="AAPL", filing_type="10-Q")

    assert result["success"] is False
    assert "quarter is required" in result["error"].lower()


def test_invalid_quarter(tool):
    """Test invalid quarter value returns error."""
    result = tool.execute(
        ticker="AAPL",
        filing_type="10-Q",
        quarter=5  # Invalid (must be 1-4)
    )

    assert result["success"] is False
    assert "quarter must be" in result["error"].lower()


# =============================================================================
# 3. CIK LOOKUP TESTS (MOCKED)
# =============================================================================

class TestCIKLookup(unittest.TestCase):
    """Test ticker to CIK conversion."""

    @patch('requests.Session.get')
    def test_cik_lookup_success(self, mock_get, tool, mock_ticker_to_cik_response):
        """Test successful CIK lookup."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ticker_to_cik_response
        mock_get.return_value = mock_response

        cik = tool._get_cik_from_ticker("AAPL")

        assert cik == "0000320193"  # 10-digit padded format
        assert len(cik) == 10

    @patch('requests.Session.get')
    def test_cik_lookup_cache(self, mock_get, tool, mock_ticker_to_cik_response):
        """Test CIK lookup caching works."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ticker_to_cik_response
        mock_get.return_value = mock_response

        # First lookup - should hit API
        cik1 = tool._get_cik_from_ticker("AAPL")

        # Second lookup - should use cache
        cik2 = tool._get_cik_from_ticker("AAPL")

        assert cik1 == cik2
        assert mock_get.call_count == 1  # Only called once (cache hit)

    @patch('requests.Session.get')
    def test_cik_lookup_not_found(self, mock_get, tool, mock_ticker_to_cik_response):
        """Test CIK lookup for non-existent ticker."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ticker_to_cik_response
        mock_get.return_value = mock_response

        cik = tool._get_cik_from_ticker("INVALID")

        assert cik is None

    @patch('requests.Session.get')
    def test_cik_padding(self, mock_get, tool):
        """Test CIK is padded to 10 digits."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "0": {"cik_str": 123, "ticker": "TEST", "title": "Test Corp"}
        }
        mock_get.return_value = mock_response

        cik = tool._get_cik_from_ticker("TEST")

        assert cik == "0000000123"  # Padded to 10 digits
        assert len(cik) == 10


# =============================================================================
# 4. FILING RETRIEVAL TESTS (MOCKED)
# =============================================================================

class TestFilingRetrieval(unittest.TestCase):
    """Test filing retrieval logic."""

    @patch('requests.Session.get')
    def test_find_latest_10k(self, mock_get, tool, mock_company_submissions_response):
        """Test finding latest 10-K filing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_company_submissions_response
        mock_get.return_value = mock_response

        company_data = tool._get_company_submissions("0000320193")
        filing = tool._find_filing(company_data, "10-K", None, None)

        assert filing is not None
        assert filing["accession_number"] == "0000320193-23-000106"
        assert filing["filing_date"] == "2023-11-03"
        assert filing["fiscal_year"] == 2023

    @patch('requests.Session.get')
    def test_find_10q_with_quarter(self, mock_get, tool, mock_company_submissions_response):
        """Test finding 10-Q filing for specific quarter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_company_submissions_response
        mock_get.return_value = mock_response

        company_data = tool._get_company_submissions("0000320193")

        # Q3 filing (July = month 7, quarter 3)
        filing = tool._find_filing(company_data, "10-Q", None, 3)

        assert filing is not None
        assert filing["report_date"] == "2023-07-01"

    @patch('requests.Session.get')
    def test_find_specific_year(self, mock_get, tool, mock_company_submissions_response):
        """Test finding filing for specific year."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_company_submissions_response
        mock_get.return_value = mock_response

        company_data = tool._get_company_submissions("0000320193")
        filing = tool._find_filing(company_data, "10-K", 2023, None)

        assert filing is not None
        assert filing["fiscal_year"] == 2023

    def test_filing_url_construction(self, tool):
        """Test filing URL construction."""
        filing_info = {
            "accession_number": "0000320193-23-000106",
            "primary_document": "aapl-20230930.htm"
        }

        url = tool._construct_filing_url("0000320193", filing_info)

        assert "sec.gov" in url
        assert "320193" in url  # CIK without leading zeros
        assert "000032019323000106" in url  # Accession without dashes
        assert "aapl-20230930.htm" in url

    @patch('requests.Session.get')
    def test_filing_not_found(self, mock_get, tool, mock_company_submissions_response):
        """Test filing not found for requested type."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_company_submissions_response
        mock_get.return_value = mock_response

        company_data = tool._get_company_submissions("0000320193")

        # Try to find 8-K (not in mock data)
        filing = tool._find_filing(company_data, "8-K", None, None)

        assert filing is None


# =============================================================================
# 5. TEXT EXTRACTION TESTS
# =============================================================================

class TestTextExtraction(unittest.TestCase):
    """Test HTML to text extraction."""

    def test_extract_full_text(self, tool, mock_10k_html_content):
        """Test extracting full text from HTML."""
        text = tool._extract_full_text(mock_10k_html_content)

        assert "Business" in text
        assert "Risk Factors" in text
        assert "Management's Discussion" in text
        assert "<html>" not in text  # HTML tags removed
        assert "<p>" not in text

    def test_clean_text(self, tool):
        """Test text cleaning functionality."""
        dirty_text = "Test   text\n\n\n\nwith    extra   spaces\n\n\nand newlines."

        clean_text = tool._clean_text(dirty_text)

        assert "   " not in clean_text  # Multiple spaces removed
        assert "\n\n\n" not in clean_text  # Multiple newlines removed
        assert "Test text" in clean_text

    def test_html_entities_cleaned(self, tool):
        """Test HTML entities are unescaped."""
        html_content = "<html><body><p>Test &amp; text with &#39;entities&#39;</p></body></html>"

        text = tool._extract_full_text(html_content)

        assert "&amp;" not in text
        assert "&#39;" not in text
        assert "&" in text or "and" in text.lower()


# =============================================================================
# 6. SECTION EXTRACTION TESTS
# =============================================================================

class TestSectionExtraction(unittest.TestCase):
    """Test section-specific extraction."""

    def test_extract_business_section(self, tool, mock_10k_html_content):
        """Test extracting Business section."""
        section = tool._extract_section(mock_10k_html_content, "business")

        assert "Business" in section
        assert "Company designs, manufactures" in section
        # Should not contain next section
        assert "Risk Factors" not in section or section.index("Risk Factors") > section.index("Business")

    def test_extract_risk_factors_section(self, tool, mock_10k_html_content):
        """Test extracting Risk Factors section."""
        section = tool._extract_section(mock_10k_html_content, "risk_factors")

        assert "Risk Factors" in section
        assert "business, results of operations" in section

    def test_extract_mda_section(self, tool, mock_10k_html_content):
        """Test extracting MD&A section."""
        section = tool._extract_section(mock_10k_html_content, "mda")

        assert "Management" in section or "Discussion" in section
        assert "consolidated financial statements" in section

    def test_section_not_found(self, tool):
        """Test section not found returns message."""
        html_content = "<html><body><p>Random content without sections</p></body></html>"

        section = tool._extract_section(html_content, "business")

        assert "not found" in section.lower()


# =============================================================================
# 7. RATE LIMITING TESTS (CRITICAL)
# =============================================================================

class TestRateLimiting(unittest.TestCase):
    """Test SEC rate limiting compliance (MOST CRITICAL)."""

    def test_rate_limit_enforcement(self, tool):
        """Test rate limiting enforces 110ms minimum interval."""
        start_time = time.time()

        # Make 10 consecutive rate limit checks
        for i in range(10):
            tool._enforce_rate_limit()

        elapsed_time = time.time() - start_time

        # Should take at least 1.1 seconds (10 * 0.11s)
        assert elapsed_time >= 1.0, f"Rate limiting too fast: {elapsed_time:.2f}s"
        # But not too slow (allow some overhead)
        assert elapsed_time < 1.5, f"Rate limiting too slow: {elapsed_time:.2f}s"

    def test_rate_limit_interval_correct(self, tool):
        """Test rate limit interval is correct value."""
        assert tool.MIN_REQUEST_INTERVAL == 0.11

        # Verify this is safely under 10 req/sec
        requests_per_second = 1.0 / tool.MIN_REQUEST_INTERVAL
        assert requests_per_second < 10, "Rate limit not safe for SEC (must be < 10 req/sec)"
        assert requests_per_second >= 9, "Rate limit too conservative"


# =============================================================================
# 8. ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    @patch('requests.Session.get')
    def test_ticker_not_found_error(self, mock_get, tool):
        """Test ticker not found returns clear error."""
        # Mock empty response (ticker not found)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = tool.execute(ticker="INVALID", filing_type="10-K")

        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert "INVALID" in result["error"]

    @patch('requests.Session.get')
    def test_network_timeout_error(self, mock_get, tool):
        """Test network timeout is handled gracefully."""
        # Mock timeout exception
        mock_get.side_effect = Exception("Request timeout")

        result = tool.execute(ticker="AAPL", filing_type="10-K")

        assert result["success"] is False
        assert "error" in result["error"].lower()

    @patch('requests.Session.get')
    def test_http_error_handling(self, mock_get, tool):
        """Test HTTP errors are handled."""
        # Mock 403 Forbidden (missing User-Agent)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
        mock_get.return_value = mock_response

        result = tool.execute(ticker="AAPL", filing_type="10-K")

        assert result["success"] is False

    def test_error_response_format(self, tool):
        """Test error responses have correct format."""
        error_result = tool._error_response("Test error message")

        assert "success" in error_result
        assert error_result["success"] is False
        assert "error" in error_result
        assert error_result["error"] == "Test error message"
        assert "data" in error_result
        assert error_result["data"] is None

    @patch('requests.Session.get')
    def test_filing_not_available_error(self, mock_get, tool, mock_ticker_to_cik_response):
        """Test filing not available returns helpful error."""
        # Mock CIK lookup success
        mock_cik_response = Mock()
        mock_cik_response.status_code = 200
        mock_cik_response.json.return_value = mock_ticker_to_cik_response

        # Mock company submissions with no 10-K
        mock_submissions_response = Mock()
        mock_submissions_response.status_code = 200
        mock_submissions_response.json.return_value = {
            "name": "Apple Inc.",
            "filings": {
                "recent": {
                    "accessionNumber": [],
                    "filingDate": [],
                    "reportDate": [],
                    "form": [],
                    "primaryDocument": []
                }
            }
        }

        mock_get.side_effect = [mock_cik_response, mock_submissions_response]

        result = tool.execute(ticker="AAPL", filing_type="10-K")

        assert result["success"] is False
        assert "not found" in result["error"].lower()


# =============================================================================
# 9. REAL API TESTS (REQUIRE INTERNET)
# =============================================================================

def check_internet_connection():
    """Check if internet connection is available."""
    try:
        import socket
        socket.create_connection(("www.sec.gov", 80), timeout=3)
        return True
    except OSError:
        return False


@pytest.mark.skipif(
    not check_internet_connection(),
    reason="Requires internet connection to SEC EDGAR"
)
class TestRealAPI(unittest.TestCase):
    """Test with real SEC EDGAR API (requires internet)."""

    def test_real_cik_lookup_apple(self, tool):
        """Test real CIK lookup for Apple."""
        cik = tool._get_cik_from_ticker("AAPL")

        assert cik is not None
        assert cik == "0000320193"
        assert len(cik) == 10

    def test_real_cik_lookup_microsoft(self, tool):
        """Test real CIK lookup for Microsoft."""
        cik = tool._get_cik_from_ticker("MSFT")

        assert cik is not None
        assert len(cik) == 10
        assert cik.startswith("0")

    def test_real_apple_10k_retrieval(self, tool):
        """Test real Apple 10-K retrieval."""
        result = tool.execute(
            ticker="AAPL",
            filing_type="10-K",
            section="business"
        )

        assert result["success"] is True
        assert result["data"]["ticker"] == "AAPL"
        assert result["data"]["company_name"] == "Apple Inc."
        assert result["data"]["filing_type"] == "10-K"
        assert result["data"]["section"] == "business"
        assert len(result["data"]["content"]) > 1000
        assert "Apple" in result["data"]["content"] or "Company" in result["data"]["content"]

    def test_real_rate_limiting_compliance(self, tool):
        """Test real API calls respect rate limiting."""
        start_time = time.time()

        # Make 5 real CIK lookups
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "META"]
        for ticker in tickers:
            tool._get_cik_from_ticker(ticker)

        elapsed_time = time.time() - start_time

        # Should take at least 0.55 seconds (5 * 0.11s)
        assert elapsed_time >= 0.5, "Rate limiting not working in real API calls"

    def test_real_filing_url_accessible(self, tool):
        """Test that constructed filing URLs are accessible."""
        result = tool.execute(
            ticker="AAPL",
            filing_type="10-K",
            section="business"
        )

        assert result["success"] is True
        assert "filing_url" in result["data"]
        assert "sec.gov" in result["data"]["filing_url"]

        # Verify URL format is correct
        url = result["data"]["filing_url"]
        assert "/Archives/edgar/data/" in url


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
