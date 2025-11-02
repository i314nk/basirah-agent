"""
Tests for Web Search Tool

Module: tests.test_tools.test_web_search
Purpose: Comprehensive test suite for Web Search API integration
Status: Complete - Sprint 3, Phase 3
Created: 2025-10-30

Test Coverage:
- All 3 search types (general, news, recent)
- Input validation
- Freshness filtering
- Company context addition
- RAG snippet extraction
- HTML cleaning
- Date parsing
- Domain extraction
- Error handling (timeout, rate limit, server errors)
- Both mocked tests (no API key) and real API tests (with key)
"""

import os
import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.tools.web_search_tool import WebSearchTool


# ==============================================================================
# TEST FIXTURES
# ==============================================================================

@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key for tests"""
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test_api_key_12345")


@pytest.fixture
def tool(mock_api_key):
    """Create Web Search tool instance with mocked API key"""
    return WebSearchTool()


@pytest.fixture
def mock_search_response():
    """Mock response from Brave Search API"""
    return {
        "web": {
            "results": [
                {
                    "title": "Apple Inc. - Official Investor Relations",
                    "url": "https://www.apple.com/investor",
                    "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
                    "age": "2 days ago",
                    "extra_snippets": [
                        "Apple is known for its strong brand loyalty and ecosystem",
                        "The company maintains premium pricing power across product lines",
                        "Network effects from App Store create switching costs for users"
                    ]
                },
                {
                    "title": "Tim Cook's Leadership at Apple - Analysis",
                    "url": "https://www.bloomberg.com/apple-ceo-analysis",
                    "description": "An analysis of Tim Cook's decade-long leadership of Apple Inc. and the company's evolution under his management.",
                    "age": "1 week ago",
                    "extra_snippets": [
                        "Cook emphasized operational excellence and supply chain management",
                        "Services revenue grew significantly under his tenure"
                    ]
                }
            ]
        }
    }


# ==============================================================================
# INITIALIZATION TESTS
# ==============================================================================

def test_tool_initialization_no_api_key(monkeypatch):
    """Test that tool raises error when API key is not set"""
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)

    with pytest.raises(ValueError, match="BRAVE_SEARCH_API_KEY environment variable not set"):
        WebSearchTool()


def test_tool_initialization_with_api_key(mock_api_key):
    """Test successful tool initialization with API key"""
    tool = WebSearchTool()

    assert tool.api_key == "test_api_key_12345"
    assert tool.name == "web_search_tool"
    assert "Brave Search" in tool.description


def test_tool_properties(tool):
    """Test tool properties"""
    assert tool.name == "web_search_tool"
    assert "qualitative" in tool.description.lower()

    # Check parameters schema
    params = tool.parameters
    assert params["type"] == "object"
    assert "query" in params["properties"]
    assert "search_type" in params["properties"]
    assert params["properties"]["search_type"]["enum"] == ["general", "news", "recent"]


# ==============================================================================
# INPUT VALIDATION TESTS
# ==============================================================================

def test_empty_query(tool):
    """Test error handling for empty query"""
    result = tool.execute(query="")

    assert result["success"] is False
    assert "empty" in result["error"].lower()


def test_query_too_long(tool):
    """Test error handling for query exceeding 400 characters"""
    long_query = "a" * 401
    result = tool.execute(query=long_query)

    assert result["success"] is False
    assert "400 character limit" in result["error"]


def test_invalid_count(tool):
    """Test error handling for invalid count values"""
    # Count too low
    result = tool.execute(query="test", count=0)
    assert result["success"] is False

    # Count too high
    result = tool.execute(query="test", count=21)
    assert result["success"] is False


def test_invalid_search_type(tool):
    """Test error handling for invalid search type"""
    result = tool.execute(query="test", search_type="invalid")

    assert result["success"] is False
    assert "Invalid search_type" in result["error"]
    assert "general, news, recent" in result["error"]


def test_invalid_freshness(tool):
    """Test error handling for invalid freshness value"""
    result = tool.execute(query="test", freshness="invalid")

    assert result["success"] is False
    assert "Invalid freshness" in result["error"]


# ==============================================================================
# MOCKED API TESTS: GENERAL SEARCH
# ==============================================================================

@patch('requests.Session.get')
def test_general_search_success(mock_get, tool, mock_search_response):
    """Test successful general search (mocked)"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(query="Apple business model", count=10)

    assert result["success"] is True
    assert result["data"]["query"] == "Apple business model"
    assert len(result["data"]["results"]) == 2

    # Check first result
    first = result["data"]["results"][0]
    assert first["title"] == "Apple Inc. - Official Investor Relations"
    assert first["source"] == "apple.com"
    assert len(first["extra_snippets"]) == 3
    assert "brand loyalty" in first["extra_snippets"][0]


@patch('requests.Session.get')
def test_company_context_addition(mock_get, tool, mock_search_response):
    """Test that company name is added to query automatically"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(
        query="management changes",
        company="Apple Inc",
        count=5
    )

    assert result["success"] is True
    # Company should be appended to query
    assert "Apple Inc" in result["data"]["query"] or "apple" in result["data"]["query"].lower()


@patch('requests.Session.get')
def test_company_context_no_duplication(mock_get, tool, mock_search_response):
    """Test that company name is not duplicated if already in query"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(
        query="Apple management changes",
        company="Apple Inc",
        count=5
    )

    assert result["success"] is True
    # Should not duplicate "Apple"
    query_parts = result["data"]["query"].lower().split()
    assert query_parts.count("apple") == 1


# ==============================================================================
# MOCKED API TESTS: NEWS SEARCH
# ==============================================================================

@patch('requests.Session.get')
def test_news_search(mock_get, tool):
    """Test news-focused search"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "web": {
            "results": [
                {
                    "title": "Apple Announces Q4 Earnings",
                    "url": "https://www.apple.com/newsroom/",
                    "description": "Apple reports record Q4 revenue",
                    "age": "3 hours ago",
                    "extra_snippets": []
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    result = tool.execute(
        query="earnings announcement",
        company="Apple",
        search_type="news"
    )

    assert result["success"] is True
    assert result["data"]["metadata"]["search_type"] == "news"


# ==============================================================================
# MOCKED API TESTS: RECENT SEARCH
# ==============================================================================

@patch('requests.Session.get')
def test_recent_search(mock_get, tool, mock_search_response):
    """Test recent search (last 30 days)"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(
        query="product launches",
        company="Tesla",
        search_type="recent"
    )

    assert result["success"] is True
    assert result["data"]["metadata"]["search_type"] == "recent"


# ==============================================================================
# FRESHNESS FILTERING TESTS
# ==============================================================================

@patch('requests.Session.get')
def test_freshness_day(mock_get, tool, mock_search_response):
    """Test freshness filter: day"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(query="test", freshness="day")

    assert result["success"] is True
    # Check that pd (past day) was sent to API
    call_params = mock_get.call_args[1]["params"]
    assert call_params["freshness"] == "pd"


@patch('requests.Session.get')
def test_freshness_week(mock_get, tool, mock_search_response):
    """Test freshness filter: week"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(query="test", freshness="week")

    assert result["success"] is True
    call_params = mock_get.call_args[1]["params"]
    assert call_params["freshness"] == "pw"


# ==============================================================================
# HTML CLEANING TESTS
# ==============================================================================

def test_html_entity_cleaning(tool):
    """Test HTML entity unescaping"""
    # Test _clean_text method
    assert tool._clean_text("Apple&#39;s iPhone") == "Apple's iPhone"
    assert tool._clean_text("AT&amp;T") == "AT&T"
    assert tool._clean_text("&quot;quoted&quot;") == '"quoted"'


def test_html_tag_removal(tool):
    """Test HTML tag removal"""
    assert tool._clean_text("<b>Bold text</b>") == "Bold text"
    assert tool._clean_text("Normal <span>text</span>") == "Normal text"


def test_whitespace_normalization(tool):
    """Test whitespace normalization"""
    assert tool._clean_text("Too   many    spaces") == "Too many spaces"
    assert tool._clean_text("  Leading and trailing  ") == "Leading and trailing"


# ==============================================================================
# DATE PARSING TESTS
# ==============================================================================

def test_parse_date_hours(tool):
    """Test parsing 'X hours ago'"""
    result = tool._parse_date("2 hours ago")

    assert result is not None
    # Should be today's date
    today = datetime.now().strftime('%Y-%m-%d')
    assert result == today


def test_parse_date_days(tool):
    """Test parsing 'X days ago'"""
    result = tool._parse_date("5 days ago")

    assert result is not None
    expected = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    assert result == expected


def test_parse_date_weeks(tool):
    """Test parsing 'X weeks ago'"""
    result = tool._parse_date("2 weeks ago")

    assert result is not None
    expected = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d')
    assert result == expected


def test_parse_date_months(tool):
    """Test parsing 'X months ago'"""
    result = tool._parse_date("3 months ago")

    assert result is not None
    expected = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    assert result == expected


def test_parse_date_years(tool):
    """Test parsing 'X years ago'"""
    result = tool._parse_date("1 year ago")

    assert result is not None
    expected = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    assert result == expected


def test_parse_date_invalid(tool):
    """Test that invalid date strings return None"""
    assert tool._parse_date("") is None
    assert tool._parse_date("invalid") is None
    assert tool._parse_date("yesterday") is None


# ==============================================================================
# DOMAIN EXTRACTION TESTS
# ==============================================================================

def test_extract_domain_basic(tool):
    """Test basic domain extraction"""
    assert tool._extract_domain("https://www.apple.com/news") == "apple.com"
    assert tool._extract_domain("https://bloomberg.com/article") == "bloomberg.com"


def test_extract_domain_removes_www(tool):
    """Test that www. prefix is removed"""
    assert tool._extract_domain("https://www.reuters.com/news") == "reuters.com"
    assert tool._extract_domain("https://www.nytimes.com/article") == "nytimes.com"


def test_extract_domain_empty(tool):
    """Test empty URL handling"""
    assert tool._extract_domain("") == ""


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================

@patch('requests.Session.get')
def test_invalid_api_key_401(mock_get, tool):
    """Test handling of invalid API key (401)"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    result = tool.execute(query="test")

    assert result["success"] is False
    assert "Invalid" in result["error"]
    assert "API key" in result["error"]


@patch('requests.Session.get')
def test_rate_limit_429(mock_get, tool):
    """Test handling of rate limit exceeded (429)"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    result = tool.execute(query="test")

    assert result["success"] is False
    assert "Rate limit" in result["error"]


@patch('requests.Session.get')
def test_server_error_500_with_retries(mock_get, tool):
    """Test handling of server error (500) with retries"""
    # First two attempts fail, third succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 500

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"web": {"results": []}}

    mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]

    result = tool.execute(query="test")

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
    mock_response_success.json.return_value = {"web": {"results": []}}

    mock_get.side_effect = [
        requests.exceptions.Timeout("Request timeout"),
        mock_response_success
    ]

    result = tool.execute(query="test")

    # Should succeed after retry
    assert result["success"] is True
    assert mock_get.call_count == 2


# ==============================================================================
# DATA STRUCTURE VALIDATION
# ==============================================================================

@patch('requests.Session.get')
def test_response_structure_complete(mock_get, tool, mock_search_response):
    """Test that response has all required fields"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(query="test")

    # Check top-level structure
    assert "success" in result
    assert "data" in result
    assert "error" in result

    # Check data structure
    data = result["data"]
    assert "query" in data
    assert "results" in data
    assert "total_results" in data
    assert "metadata" in data

    # Check result structure
    if data["results"]:
        r = data["results"][0]
        assert "title" in r
        assert "url" in r
        assert "description" in r
        assert "age" in r
        assert "published_date" in r
        assert "source" in r
        assert "extra_snippets" in r


@patch('requests.Session.get')
def test_rag_snippets_extracted(mock_get, tool, mock_search_response):
    """Test that RAG-optimized snippets are extracted"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_response
    mock_get.return_value = mock_response

    result = tool.execute(query="test")

    assert result["success"] is True
    first_result = result["data"]["results"][0]

    # Check extra_snippets present
    assert "extra_snippets" in first_result
    assert isinstance(first_result["extra_snippets"], list)
    assert len(first_result["extra_snippets"]) == 3

    # Check snippet content
    assert "brand loyalty" in first_result["extra_snippets"][0]


# ==============================================================================
# REAL API TESTS (REQUIRES API KEY)
# ==============================================================================

@pytest.mark.skipif(
    not os.getenv("BRAVE_SEARCH_API_KEY"),
    reason="BRAVE_SEARCH_API_KEY not set - skipping real API tests"
)
class TestRealAPI:
    """Tests that require actual Brave Search API key"""

    def test_real_api_general_search_apple(self):
        """Test real API call for general search"""
        tool = WebSearchTool()
        result = tool.execute(query="Apple Inc management", count=5, search_type="general")

        assert result["success"] is True
        assert result["data"]["total_results"] > 0
        assert "extra_snippets" in result["data"]["results"][0]

    def test_real_api_news_search_microsoft(self):
        """Test real API call for news search"""
        tool = WebSearchTool()
        result = tool.execute(
            query="management changes earnings",
            company="Microsoft",
            count=10,
            search_type="news"
        )

        assert result["success"] is True
        assert result["data"]["metadata"]["search_type"] == "news"

    def test_real_api_recent_search_tesla(self):
        """Test real API call for recent search"""
        tool = WebSearchTool()
        result = tool.execute(
            query="production deliveries",
            company="Tesla",
            search_type="recent"
        )

        assert result["success"] is True

    def test_real_api_freshness_filter(self):
        """Test real API call with freshness filter"""
        tool = WebSearchTool()
        result = tool.execute(
            query="tech industry news",
            freshness="week",
            count=5
        )

        assert result["success"] is True

    def test_real_api_integration_with_gurufocus(self):
        """Test integration with GuruFocus for company context"""
        from src.tools.gurufocus_tool import GuruFocusTool

        # Only run if both API keys present
        if not os.getenv("GURUFOCUS_API_KEY"):
            pytest.skip("GURUFOCUS_API_KEY not set")

        # Get company name from GuruFocus
        gf_tool = GuruFocusTool()
        gf_result = gf_tool.execute(ticker="AAPL", endpoint="summary")

        if not gf_result["success"]:
            pytest.skip("GuruFocus API call failed")

        company_name = gf_result["data"]["company_name"]

        # Use in web search
        ws_tool = WebSearchTool()
        ws_result = ws_tool.execute(
            query="economic moat competitive advantages",
            company=company_name,
            count=5
        )

        assert ws_result["success"] is True
        assert company_name.lower() in ws_result["data"]["query"].lower() or \
               "apple" in ws_result["data"]["query"].lower()


# ==============================================================================
# TEST SUMMARY
# ==============================================================================

if __name__ == "__main__":
    """Run test suite with pytest"""
    pytest.main([__file__, "-v", "--tb=short"])
