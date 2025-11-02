"""
Simple working tests for SEC Filing Tool
Demonstrates core functionality works
"""
import time
from unittest.mock import Mock, patch
from src.tools.sec_filing_tool import SECFilingTool


def test_tool_initialization():
    """Test tool initializes correctly."""
    tool = SECFilingTool()
    assert tool.name == "sec_filing_tool"
    assert 'User-Agent' in tool.session.headers


def test_rate_limiting_interval():
    """Test rate limit interval is correct."""
    tool = SECFilingTool()
    assert tool.MIN_REQUEST_INTERVAL == 0.11
    requests_per_second = 1.0 / tool.MIN_REQUEST_INTERVAL
    assert requests_per_second < 10  # Safely under SEC limit


def test_rate_limit_enforcement():
    """Test rate limiting enforces delays."""
    tool = SECFilingTool()
    
    start = time.time()
    for i in range(5):
        tool._enforce_rate_limit()
    elapsed = time.time() - start
    
    # Should take at least 0.44 seconds (5 * 0.11s - first call is immediate)
    assert elapsed >= 0.4


def test_input_validation_empty_ticker():
    """Test empty ticker returns error."""
    tool = SECFilingTool()
    result = tool.execute(ticker="", filing_type="10-K")
    
    assert result["success"] is False
    assert "cannot be empty" in result["error"].lower()


def test_input_validation_invalid_filing_type():
    """Test invalid filing type returns error."""
    tool = SECFilingTool()
    result = tool.execute(ticker="AAPL", filing_type="INVALID")
    
    assert result["success"] is False
    assert "invalid filing_type" in result["error"].lower()


@patch('requests.Session.get')
def test_cik_lookup_success(mock_get):
    """Test successful CIK lookup."""
    tool = SECFilingTool()
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
    }
    mock_get.return_value = mock_response
    
    cik = tool._get_cik_from_ticker("AAPL")
    
    assert cik == "0000320193"
    assert len(cik) == 10


def test_text_cleaning():
    """Test text cleaning functionality."""
    tool = SECFilingTool()
    
    dirty = "Test   text\n\n\n\nwith    extra   spaces"
    clean = tool._clean_text(dirty)
    
    assert "   " not in clean
    assert "\n\n\n" not in clean


def test_error_response_format():
    """Test error responses have correct format."""
    tool = SECFilingTool()
    
    error = tool._error_response("Test error")
    
    assert error["success"] is False
    assert error["error"] == "Test error"
    assert error["data"] is None


print("All tests defined successfully!")
