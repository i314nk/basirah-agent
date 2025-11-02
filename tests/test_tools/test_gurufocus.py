"""
Tests for GuruFocus Tool

Module: tests.test_tools.test_gurufocus
Purpose: Comprehensive test suite for GuruFocus API integration
Status: Complete - Sprint 3, Phase 2
Created: 2025-10-30

Test Coverage:
- All 4 endpoints (summary, financials, keyratios, valuation)
- Input validation
- Special value detection (9999, 10000, 0)
- Rate limiting enforcement
- Error handling (timeout, rate limit, invalid ticker, server errors)
- Integration with Calculator Tool
- Both mocked tests (no API key) and real API tests (with key)
"""

import os
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.tools.gurufocus_tool import GuruFocusTool


# ==============================================================================
# TEST FIXTURES
# ==============================================================================

@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key for tests"""
    monkeypatch.setenv("GURUFOCUS_API_KEY", "test_key_12345:test_secret_67890")


@pytest.fixture
def tool(mock_api_key):
    """Create GuruFocus tool instance with mocked API key"""
    return GuruFocusTool()


@pytest.fixture
def mock_summary_response():
    """Mock response for /summary endpoint"""
    return {
        "general": {
            "name": "Apple Inc",
            "exchange": "NAS",
            "industry": "Consumer Electronics",
            "sector": "Technology",
            "currency": "USD",
            "address": "One Apple Park Way, Cupertino, CA"
        },
        "quote": {
            "price": 175.43,
            "market_cap": 2750000000000,
            "volume": 52431234
        },
        "profitability": {
            "operating_margin": 0.28,
            "net_margin": 0.24,
            "roic": 0.32,
            "roe": 1.47,
            "roa": 0.28
        },
        "financial_strength": {
            "score": 8,
            "cash_to_debt": 1.25,
            "equity_to_asset": 0.42,
            "debt_to_equity": 1.85
        },
        "valuation": {
            "pe_ratio": 28.5,
            "pb_ratio": 45.2,
            "ps_ratio": 7.3,
            "peg_ratio": 2.1,
            "ev_ebitda": 22.4
        }
    }


@pytest.fixture
def mock_financials_response():
    """Mock response for /financials endpoint"""
    return {
        "financials": {
            "annual": {
                "Fiscal Year": ["2023", "2022", "2021", "2020", "2019"],
                "Revenue": [383285000000, 394328000000, 365817000000, 274515000000, 260174000000],
                "Net Income": [96995000000, 99803000000, 94680000000, 57411000000, 55256000000],
                "Depreciation & Amortization": [11519000000, 11104000000, 11284000000, 11056000000, 12547000000],
                "Operating Income": [114301000000, 119437000000, 108949000000, 66288000000, 63930000000],
                "Capital Expenditure": [10959000000, 10708000000, 11085000000, 7309000000, 10495000000],
                "Free Cash Flow": [99584000000, 111443000000, 92953000000, 80674000000, 58896000000],
                "Total Assets": [352755000000, 352583000000, 351002000000, 323888000000, 338516000000],
                "Total Liabilities": [290437000000, 302083000000, 287912000000, 258549000000, 248028000000],
                "Total Stockholders Equity": [62318000000, 50672000000, 63090000000, 65339000000, 90488000000],
                "Cash and Cash Equivalents": [29965000000, 23646000000, 34940000000, 38016000000, 48844000000],
                "Total Debt": [106628000000, 120069000000, 124719000000, 112436000000, 108047000000]
            }
        }
    }


@pytest.fixture
def mock_keyratios_response():
    """Mock response for /keyratios endpoint"""
    return {
        "keyratios_per_share": {
            "Fiscal Year": ["2023", "2022", "2021", "2020", "2019"],
            "Revenue per Share": [26.42, 25.79, 24.11, 19.56, 18.72],
            "Earnings per Share": [6.87, 6.56, 6.25, 4.09, 3.97],
            "Book Value per Share": [4.42, 3.33, 4.16, 4.66, 6.51],
            "Free Cash Flow per Share": [7.06, 7.32, 6.13, 5.75, 4.23],
            "Dividends per Share": [0.94, 0.90, 0.85, 0.79, 0.75]
        },
        "profitability_ratios": {
            "Fiscal Year": ["2023", "2022", "2021", "2020", "2019"],
            "Operating Margin %": [29.8, 30.3, 29.8, 24.1, 24.6],
            "Net Margin %": [25.3, 25.3, 25.9, 20.9, 21.2],
            "ROE %": [155.8, 196.9, 150.1, 87.9, 61.1],
            "ROA %": [27.5, 28.3, 27.0, 17.7, 16.3],
            "ROIC %": [52.3, 56.7, 45.0, 29.2, 27.5]
        },
        "efficiency_ratios": {
            "Asset Turnover": 1.09,
            "Inventory Turnover": 45.2
        },
        "valuation_ratios": {
            "P/E Ratio": 28.5,
            "P/B Ratio": 45.2,
            "P/S Ratio": 7.3,
            "PEG Ratio": 2.1,
            "EV/EBITDA": 22.4,
            "Price to Free Cash Flow": 24.8
        }
    }


@pytest.fixture
def mock_valuation_response():
    """Mock response for /valuation endpoint"""
    return {
        "valuation": {
            "market_cap": 2750000000000,
            "enterprise_value": 2850000000000,
            "pe_ratio": 28.5,
            "forward_pe": 26.3,
            "peg_ratio": 2.1,
            "ps_ratio": 7.3,
            "pb_ratio": 45.2,
            "ev_ebitda": 22.4,
            "ev_sales": 7.8,
            "price_to_fcf": 24.8
        },
        "gurufocus_metrics": {
            "gf_value": 165.50,
            "current_price": 175.43,
            "gf_value_rank": "Overvalued",
            "graham_number": 142.35,
            "dcf_value": 158.75,
            "median_ps_value": 162.40,
            "peter_lynch_fair_value": 171.20
        },
        "growth_metrics": {
            "revenue_growth_3y": 0.122,
            "revenue_growth_5y": 0.095,
            "eps_growth_3y": 0.187,
            "eps_growth_5y": 0.142,
            "fcf_growth_3y": 0.161
        }
    }


# ==============================================================================
# INITIALIZATION TESTS
# ==============================================================================

def test_tool_initialization_no_api_key(monkeypatch):
    """Test that tool raises error when API key is not set"""
    monkeypatch.delenv("GURUFOCUS_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GURUFOCUS_API_KEY environment variable not set"):
        GuruFocusTool()


def test_tool_initialization_with_api_key(mock_api_key):
    """Test successful tool initialization with API key"""
    tool = GuruFocusTool()

    assert tool.api_key == "test_key_12345:test_secret_67890"
    assert tool.name == "gurufocus_tool"
    assert tool.MIN_INTERVAL == 1.5
    assert len(tool.description) > 50


def test_tool_properties(tool):
    """Test tool properties"""
    assert tool.name == "gurufocus_tool"
    assert "GuruFocus" in tool.description

    # Check parameters schema
    params = tool.parameters
    assert params["type"] == "object"
    assert "ticker" in params["properties"]
    assert "endpoint" in params["properties"]
    assert params["properties"]["endpoint"]["enum"] == ["summary", "financials", "keyratios", "valuation"]


# ==============================================================================
# INPUT VALIDATION TESTS
# ==============================================================================

def test_missing_ticker(tool):
    """Test error handling for missing ticker"""
    result = tool.execute(endpoint="summary")

    assert result["success"] is False
    assert "Missing required parameter" in result["error"]
    assert "ticker" in result["error"]


def test_invalid_ticker_format(tool):
    """Test error handling for invalid ticker format"""
    # Too long
    result = tool.execute(ticker="TOOLONG", endpoint="summary")
    assert result["success"] is False
    assert "Invalid ticker format" in result["error"]

    # Contains numbers
    result = tool.execute(ticker="ABC123", endpoint="summary")
    assert result["success"] is False


def test_missing_endpoint(tool):
    """Test error handling for missing endpoint"""
    result = tool.execute(ticker="AAPL")

    assert result["success"] is False
    assert "endpoint" in result["error"].lower()


def test_invalid_endpoint(tool):
    """Test error handling for invalid endpoint"""
    result = tool.execute(ticker="AAPL", endpoint="invalid")

    assert result["success"] is False
    assert "Invalid endpoint" in result["error"]
    assert "summary, financials, keyratios, valuation" in result["error"]


def test_invalid_period(tool):
    """Test error handling for invalid period"""
    result = tool.execute(ticker="AAPL", endpoint="financials", period="invalid")

    assert result["success"] is False
    assert "Invalid period" in result["error"]
    assert "annual" in result["error"]
    assert "quarterly" in result["error"]


# ==============================================================================
# MOCKED API TESTS: SUMMARY ENDPOINT
# ==============================================================================

@patch('requests.Session.get')
def test_summary_endpoint_success(mock_get, tool, mock_summary_response):
    """Test successful summary endpoint call (mocked)"""
    # Mock HTTP response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_summary_response
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="summary")

    assert result["success"] is True
    assert result["data"]["ticker"] == "AAPL"
    assert result["data"]["company_name"] == "Apple Inc"
    assert result["data"]["endpoint"] == "summary"

    # Check metrics extracted
    metrics = result["data"]["metrics"]
    assert metrics["roic"] == 0.32
    assert metrics["roe"] == 1.47
    assert metrics["operating_margin"] == 0.28
    assert metrics["financial_strength_score"] == 8

    # Check valuation data
    valuation = result["data"]["valuation"]
    assert valuation["price"] == 175.43
    assert valuation["market_cap"] == 2750000000000
    assert valuation["pe_ratio"] == 28.5

    # Check metadata
    assert result["data"]["metadata"]["source"] == "gurufocus"
    assert result["data"]["metadata"]["api_version"] == "v3"


# ==============================================================================
# MOCKED API TESTS: FINANCIALS ENDPOINT
# ==============================================================================

@patch('requests.Session.get')
def test_financials_endpoint_success(mock_get, tool, mock_financials_response):
    """Test successful financials endpoint call (mocked)"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_financials_response
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="financials", period="annual")

    assert result["success"] is True
    assert result["data"]["endpoint"] == "financials"

    # Check financial data extracted
    financials = result["data"]["financials"]
    assert financials["net_income"] == 96995000000
    assert financials["revenue"] == 383285000000
    assert financials["depreciation_amortization"] == 11519000000
    assert financials["capex"] == 10959000000
    assert financials["operating_income"] == 114301000000
    assert financials["total_assets"] == 352755000000
    assert financials["cash_equivalents"] == 29965000000

    # Check historical data
    assert "historical" in financials
    assert len(financials["historical"]["net_income"]) == 5
    assert len(financials["historical"]["revenue"]) == 5


# ==============================================================================
# MOCKED API TESTS: KEY RATIOS ENDPOINT
# ==============================================================================

@patch('requests.Session.get')
def test_keyratios_endpoint_success(mock_get, tool, mock_keyratios_response):
    """Test successful keyratios endpoint call (mocked) - MOST IMPORTANT"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_keyratios_response
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="keyratios")

    assert result["success"] is True
    assert result["data"]["endpoint"] == "keyratios"

    # Check pre-calculated metrics (hybrid approach)
    metrics = result["data"]["metrics"]

    # ROIC, ROE, ROA should be converted to decimals
    assert metrics["roic"] == 0.523  # 52.3% -> 0.523
    assert metrics["roe"] == 1.558  # 155.8% -> 1.558
    assert metrics["roa"] == 0.275  # 27.5% -> 0.275
    assert metrics["operating_margin"] == 0.298
    assert metrics["net_margin"] == 0.253

    # Per-share values
    assert metrics["eps"] == 6.87
    assert metrics["fcf_per_share"] == 7.06
    assert metrics["revenue_per_share"] == 26.42
    assert metrics["dividends_per_share"] == 0.94

    # 10-year averages
    assert "roic_10y_avg" in metrics
    assert "roe_10y_avg" in metrics

    # Valuation ratios
    valuation = result["data"]["valuation"]
    assert valuation["pe_ratio"] == 28.5
    assert valuation["pb_ratio"] == 45.2


# ==============================================================================
# MOCKED API TESTS: VALUATION ENDPOINT
# ==============================================================================

@patch('requests.Session.get')
def test_valuation_endpoint_success(mock_get, tool, mock_valuation_response):
    """Test successful valuation endpoint call (mocked)"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_valuation_response
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="valuation")

    assert result["success"] is True
    assert result["data"]["endpoint"] == "valuation"

    # Check valuation data
    valuation = result["data"]["valuation"]
    assert valuation["market_cap"] == 2750000000000
    assert valuation["pe_ratio"] == 28.5
    assert valuation["gf_value"] == 165.50
    assert valuation["current_price"] == 175.43
    assert valuation["gf_value_rank"] == "Overvalued"
    assert valuation["graham_number"] == 142.35

    # Check growth metrics
    metrics = result["data"]["metrics"]
    assert metrics["revenue_growth_3y"] == 0.122
    assert metrics["eps_growth_5y"] == 0.142


# ==============================================================================
# SPECIAL VALUE DETECTION TESTS
# ==============================================================================

@patch('requests.Session.get')
def test_special_value_detection_9999(mock_get, tool):
    """Test detection of 9999 (data not available) special value"""
    mock_response_data = {
        "profitability": {
            "roic": 9999,  # Data not available
            "roe": 0.25
        },
        "general": {"name": "Test Company"}
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_get.return_value = mock_response

    result = tool.execute(ticker="TEST", endpoint="summary")

    assert result["success"] is True

    # Check special values detected
    special_values = result["data"]["special_values_detected"]
    assert len(special_values) > 0

    # Find 9999 value
    sv_9999 = [sv for sv in special_values if sv["value"] == 9999]
    assert len(sv_9999) == 1
    assert sv_9999[0]["meaning"] == "Data not available"
    assert "roic" in sv_9999[0]["field"]


@patch('requests.Session.get')
def test_special_value_detection_10000(mock_get, tool):
    """Test detection of 10000 (no debt or negative equity) special value"""
    mock_response_data = {
        "financial_strength": {
            "debt_to_equity": 10000,  # No debt or negative equity
            "cash_to_debt": 10000
        },
        "general": {"name": "Test Company"}
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_get.return_value = mock_response

    result = tool.execute(ticker="TEST", endpoint="summary")

    assert result["success"] is True

    # Check special values detected
    special_values = result["data"]["special_values_detected"]
    sv_10000 = [sv for sv in special_values if sv["value"] == 10000]

    # Should detect both 10000 values
    assert len(sv_10000) == 2

    # Check debt field has "No debt" meaning
    debt_fields = [sv for sv in sv_10000 if "debt" in sv["field"].lower()]
    assert len(debt_fields) > 0
    assert any("No debt" in sv["meaning"] for sv in debt_fields)


@patch('requests.Session.get')
def test_zero_value_not_flagged_as_special(mock_get, tool):
    """Test that 0 values are NOT flagged as special (valid at-loss value)"""
    mock_response_data = {
        "valuation": {
            "pe_ratio": 0,  # At loss - valid value
            "pb_ratio": 5.0
        },
        "general": {"name": "Test Company"}
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_get.return_value = mock_response

    result = tool.execute(ticker="TEST", endpoint="summary")

    assert result["success"] is True

    # Zero should NOT be in special values
    special_values = result["data"]["special_values_detected"]
    sv_zero = [sv for sv in special_values if sv["value"] == 0]
    assert len(sv_zero) == 0


# ==============================================================================
# RATE LIMITING TESTS
# ==============================================================================

@patch('requests.Session.get')
def test_rate_limiting_enforced(mock_get, tool):
    """Test that rate limiting enforces 1.5s minimum between requests"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"general": {"name": "Test"}}
    mock_get.return_value = mock_response

    # Make first request
    start_time = time.time()
    tool.execute(ticker="AAPL", endpoint="summary")

    # Make second request immediately
    tool.execute(ticker="MSFT", endpoint="summary")
    elapsed = time.time() - start_time

    # Should take at least 1.5 seconds
    assert elapsed >= 1.5, f"Rate limiting not enforced: elapsed={elapsed:.2f}s"


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================

@patch('requests.Session.get')
def test_invalid_ticker_404(mock_get, tool):
    """Test handling of invalid ticker (404 error)"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    # Use valid format ticker that will reach API and get 404
    result = tool.execute(ticker="XXXXX", endpoint="summary")

    assert result["success"] is False
    assert "not found" in result["error"]
    assert "XXXXX" in result["error"]


@patch('requests.Session.get')
def test_rate_limit_exceeded_429(mock_get, tool):
    """Test handling of rate limit exceeded (429 error)"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="summary")

    assert result["success"] is False
    assert "Rate limit exceeded" in result["error"]


@patch('requests.Session.get')
def test_invalid_api_key_401(mock_get, tool):
    """Test handling of invalid API key (401 error)"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="summary")

    assert result["success"] is False
    assert "Invalid GuruFocus API key" in result["error"]


@patch('requests.Session.get')
def test_server_error_500_with_retries(mock_get, tool):
    """Test handling of server error (500) with retries"""
    # First two attempts fail, third succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 500

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"general": {"name": "Apple Inc"}}

    mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]

    result = tool.execute(ticker="AAPL", endpoint="summary")

    # Should succeed after retries
    assert result["success"] is True
    assert mock_get.call_count == 3


@patch('requests.Session.get')
def test_timeout_with_retries(mock_get, tool):
    """Test handling of request timeout with retries"""
    import requests

    # First attempt times out, second succeeds
    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"general": {"name": "Apple Inc"}}

    mock_get.side_effect = [
        requests.exceptions.Timeout("Request timeout"),
        mock_response_success
    ]

    result = tool.execute(ticker="AAPL", endpoint="summary")

    # Should succeed after retry
    assert result["success"] is True
    assert mock_get.call_count == 2


@patch('requests.Session.get')
def test_timeout_all_retries_exhausted(mock_get, tool):
    """Test failure when all retry attempts timeout"""
    import requests

    mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

    result = tool.execute(ticker="AAPL", endpoint="summary")

    assert result["success"] is False
    assert "timeout" in result["error"].lower()
    assert "retries exhausted" in result["error"].lower()


# ==============================================================================
# DATA STRUCTURE VALIDATION TESTS
# ==============================================================================

@patch('requests.Session.get')
def test_response_structure_complete(mock_get, tool, mock_summary_response):
    """Test that response has all required fields"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_summary_response
    mock_get.return_value = mock_response

    result = tool.execute(ticker="AAPL", endpoint="summary")

    # Check top-level structure
    assert "success" in result
    assert "data" in result
    assert "error" in result

    # Check data structure
    data = result["data"]
    assert "ticker" in data
    assert "company_name" in data
    assert "endpoint" in data
    assert "metrics" in data
    assert "financials" in data
    assert "valuation" in data
    assert "special_values_detected" in data
    assert "metadata" in data

    # Check metadata structure
    metadata = data["metadata"]
    assert "source" in metadata
    assert "api_version" in metadata
    assert "timestamp" in metadata
    assert "period" in metadata
    assert "url" in metadata


# ==============================================================================
# INTEGRATION TESTS WITH CALCULATOR TOOL
# ==============================================================================

@patch('requests.Session.get')
def test_integration_with_calculator_dcf(mock_get, tool, mock_keyratios_response):
    """Test integration with Calculator Tool for DCF calculation"""
    from src.tools.calculator_tool import CalculatorTool

    # Mock GuruFocus API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_keyratios_response
    mock_get.return_value = mock_response

    # Get data from GuruFocus
    gf_result = tool.execute(ticker="AAPL", endpoint="keyratios")
    assert gf_result["success"] is True

    # Use GuruFocus FCF per share for DCF calculation
    fcf_per_share = gf_result["data"]["metrics"]["fcf_per_share"]
    assert fcf_per_share == 7.06

    # Calculate intrinsic value using Calculator Tool
    calc_tool = CalculatorTool()

    # Assume 15.7B shares outstanding → Owner Earnings = FCF per share * shares
    shares = 15700000000
    owner_earnings = fcf_per_share * shares

    dcf_result = calc_tool.execute(
        calculation="dcf",
        data={
            "owner_earnings": owner_earnings,
            "growth_rate": 0.07,
            "discount_rate": 0.10,
            "terminal_growth": 0.03,
            "years": 10
        }
    )

    assert dcf_result["success"] is True
    assert dcf_result["data"]["result"] > 0


@patch('requests.Session.get')
def test_integration_with_calculator_margin_of_safety(mock_get, tool, mock_summary_response):
    """Test integration with Calculator Tool for Margin of Safety"""
    from src.tools.calculator_tool import CalculatorTool

    # Mock GuruFocus API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_summary_response
    mock_get.return_value = mock_response

    # Get price from GuruFocus
    gf_result = tool.execute(ticker="AAPL", endpoint="summary")
    assert gf_result["success"] is True

    current_price = gf_result["data"]["valuation"]["price"]
    assert current_price == 175.43

    # Calculate margin of safety
    calc_tool = CalculatorTool()

    mos_result = calc_tool.execute(
        calculation="margin_of_safety",
        data={
            "intrinsic_value": 200.00,  # Example intrinsic value
            "current_price": current_price
        }
    )

    assert mos_result["success"] is True
    assert mos_result["data"]["result"] > 0  # Positive margin


# ==============================================================================
# REAL API TESTS (REQUIRES API KEY)
# ==============================================================================

@pytest.mark.skipif(
    not os.getenv("GURUFOCUS_API_KEY"),
    reason="GURUFOCUS_API_KEY not set - skipping real API tests"
)
class TestRealAPI:
    """Tests that require actual GuruFocus API key"""

    def test_real_api_summary_apple(self):
        """Test real API call to summary endpoint for Apple"""
        tool = GuruFocusTool()
        result = tool.execute(ticker="AAPL", endpoint="summary")

        assert result["success"] is True
        assert result["data"]["ticker"] == "AAPL"
        assert "Apple" in result["data"]["company_name"]
        assert result["data"]["metrics"]["roic"] is not None

    def test_real_api_keyratios_microsoft(self):
        """Test real API call to keyratios endpoint for Microsoft"""
        tool = GuruFocusTool()
        result = tool.execute(ticker="MSFT", endpoint="keyratios")

        assert result["success"] is True
        assert result["data"]["ticker"] == "MSFT"
        assert "roic" in result["data"]["metrics"]
        assert result["data"]["metrics"]["roic"] is not None

    def test_real_api_financials_cocacola(self):
        """Test real API call to financials endpoint for Coca-Cola"""
        tool = GuruFocusTool()
        result = tool.execute(ticker="KO", endpoint="financials")

        assert result["success"] is True
        assert result["data"]["ticker"] == "KO"
        assert "net_income" in result["data"]["financials"]
        assert result["data"]["financials"]["net_income"] is not None

    def test_real_api_valuation_jnj(self):
        """Test real API call to valuation endpoint for Johnson & Johnson"""
        tool = GuruFocusTool()
        result = tool.execute(ticker="JNJ", endpoint="valuation")

        assert result["success"] is True
        assert result["data"]["ticker"] == "JNJ"
        assert "pe_ratio" in result["data"]["valuation"]

    def test_real_api_rate_limiting(self):
        """Test that rate limiting works with real API"""
        tool = GuruFocusTool()

        start_time = time.time()

        # Make 3 consecutive requests
        tool.execute(ticker="AAPL", endpoint="summary")
        tool.execute(ticker="MSFT", endpoint="summary")
        tool.execute(ticker="KO", endpoint="summary")

        elapsed = time.time() - start_time

        # Should take at least 3 seconds (1.5s * 2 intervals)
        assert elapsed >= 3.0, f"Rate limiting not working: elapsed={elapsed:.2f}s"


# ==============================================================================
# TEST SUMMARY
# ==============================================================================

if __name__ == "__main__":
    """Run test suite with pytest"""
    pytest.main([__file__, "-v", "--tb=short"])
