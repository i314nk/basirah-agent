# SEC Filing Tool Specification

## Tool Name: `sec_filing_tool`

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Status:** Sprint 2 - Ready for Implementation

---

## 1. Purpose & Use Cases

### Purpose

The SEC Filing Tool provides access to corporate filings from the SEC EDGAR database, enabling the basīrah agent to retrieve and analyze regulatory documents including 10-K annual reports, 10-Q quarterly reports, proxy statements (DEF 14A), and other SEC filings.

### Primary Use Cases for Agent

1. **Business Understanding:**
   - Extract "Business" section from 10-K for company description
   - Understand products, services, revenue sources
   - Identify key markets and customers

2. **Management Evaluation:**
   - Read proxy statements (DEF 14A) for executive compensation
   - Extract shareholder letters for management tone assessment
   - Review MD&A for management's perspective on performance

3. **Risk Assessment:**
   - Extract "Risk Factors" section from 10-K
   - Identify disclosed risks and uncertainties
   - Assess litigation and regulatory issues

4. **Financial Validation:**
   - Cross-reference financial data with GuruFocus
   - Verify accounting policies and notes
   - Check for restatements or irregularities

### When Agent Should Use This Tool

```
PHASE 2 (Business Understanding):
  → sec_filing_tool(ticker="AAPL", filing_type="10-K", section="business")
  → sec_filing_tool(ticker="AAPL", filing_type="10-K", section="risk_factors")

PHASE 4 (Management Evaluation):
  → sec_filing_tool(ticker="AAPL", filing_type="DEF 14A")  # Proxy statement
  → sec_filing_tool(ticker="AAPL", filing_type="10-K", section="mda")

PHASE 7 (Risk Assessment):
  → sec_filing_tool(ticker="AAPL", filing_type="10-K", section="risk_factors")
```

---

## 2. Input Parameters

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "ticker": {
      "type": "string",
      "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')",
      "pattern": "^[A-Z]{1,5}$"
    },
    "filing_type": {
      "type": "string",
      "description": "Type of SEC filing to retrieve",
      "enum": ["10-K", "10-Q", "DEF 14A", "8-K"],
      "examples": ["10-K", "DEF 14A"]
    },
    "section": {
      "type": "string",
      "description": "Specific section to extract (optional, applies to 10-K/10-Q)",
      "enum": ["business", "risk_factors", "mda", "financial_statements", "full"],
      "default": "full"
    },
    "year": {
      "type": "integer",
      "description": "Fiscal year (optional, defaults to most recent)",
      "minimum": 2010,
      "maximum": 2025,
      "examples": [2023, 2022]
    },
    "quarter": {
      "type": "integer",
      "description": "Fiscal quarter (required for 10-Q only)",
      "enum": [1, 2, 3, 4]
    }
  },
  "required": ["ticker", "filing_type"],
  "additionalProperties": false
}
```

### Parameter Details

#### `ticker` (required)
- **Type:** string
- **Format:** 1-5 uppercase letters
- **Description:** Stock ticker symbol
- **Validation:** Must match pattern `^[A-Z]{1,5}$`
- **Examples:** `"AAPL"`, `"MSFT"`, `"BRK.B"`

#### `filing_type` (required)
- **Type:** string
- **Allowed Values:**
  - `"10-K"` - Annual report (comprehensive company information)
  - `"10-Q"` - Quarterly report
  - `"DEF 14A"` - Proxy statement (executive compensation, governance)
  - `"8-K"` - Current report (material events)
- **Description:** Type of SEC filing to retrieve
- **Most Common:** `"10-K"` for business understanding and risk factors

#### `section` (optional)
- **Type:** string
- **Allowed Values:**
  - `"business"` - Item 1: Business description
  - `"risk_factors"` - Item 1A: Risk factors
  - `"mda"` - Item 7: Management's Discussion & Analysis
  - `"financial_statements"` - Item 8: Financial statements and notes
  - `"full"` - Complete filing (default)
- **Description:** Specific section to extract from filing
- **Applicable To:** `10-K` and `10-Q` filings only
- **Default:** `"full"`
- **Note:** Extracting specific sections reduces token usage and processing time

#### `year` (optional)
- **Type:** integer
- **Range:** 2010-2025
- **Description:** Fiscal year of filing
- **Default:** Most recent available filing
- **Examples:** `2023`, `2022`

#### `quarter` (conditional)
- **Type:** integer
- **Allowed Values:** 1, 2, 3, 4
- **Description:** Fiscal quarter
- **Required For:** `10-Q` filings only
- **Not Applicable To:** `10-K`, `DEF 14A`, `8-K`

### Example Input

```python
# Example 1: Get latest 10-K business section
{
    "ticker": "AAPL",
    "filing_type": "10-K",
    "section": "business"
}

# Example 2: Get specific year 10-K risk factors
{
    "ticker": "MSFT",
    "filing_type": "10-K",
    "section": "risk_factors",
    "year": 2022
}

# Example 3: Get latest proxy statement
{
    "ticker": "GOOGL",
    "filing_type": "DEF 14A"
}

# Example 4: Get Q2 2023 quarterly report
{
    "ticker": "AAPL",
    "filing_type": "10-Q",
    "quarter": 2,
    "year": 2023
}
```

---

## 3. Output Format

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the filing was successfully retrieved"
    },
    "data": {
      "type": "object",
      "properties": {
        "ticker": {
          "type": "string",
          "description": "Stock ticker symbol"
        },
        "company_name": {
          "type": "string",
          "description": "Official company name from SEC"
        },
        "cik": {
          "type": "string",
          "description": "Central Index Key (10-digit format)"
        },
        "filing_type": {
          "type": "string",
          "description": "Type of filing retrieved"
        },
        "filing_date": {
          "type": "string",
          "format": "date",
          "description": "Date filing was submitted to SEC"
        },
        "fiscal_year": {
          "type": "integer",
          "description": "Fiscal year of filing"
        },
        "fiscal_quarter": {
          "type": ["integer", "null"],
          "description": "Fiscal quarter (for 10-Q only)"
        },
        "section": {
          "type": "string",
          "description": "Section extracted (or 'full')"
        },
        "content": {
          "type": "string",
          "description": "Extracted text content from filing"
        },
        "content_length": {
          "type": "integer",
          "description": "Length of content in characters"
        },
        "filing_url": {
          "type": "string",
          "format": "uri",
          "description": "Direct URL to SEC filing"
        },
        "metadata": {
          "type": "object",
          "properties": {
            "source": {
              "type": "string",
              "const": "sec_edgar"
            },
            "timestamp": {
              "type": "string",
              "format": "date-time"
            },
            "accession_number": {
              "type": "string",
              "description": "SEC accession number"
            }
          }
        }
      },
      "required": ["ticker", "company_name", "cik", "filing_type", "content", "metadata"]
    },
    "error": {
      "type": ["string", "null"],
      "description": "Error message if success=false"
    }
  },
  "required": ["success", "data", "error"]
}
```

### Example Success Response

```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "cik": "0000320193",
    "filing_type": "10-K",
    "filing_date": "2023-11-03",
    "fiscal_year": 2023,
    "fiscal_quarter": null,
    "section": "business",
    "content": "Item 1. Business\n\nCompany Background\n\nThe Company designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services...",
    "content_length": 12543,
    "filing_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm",
    "metadata": {
      "source": "sec_edgar",
      "timestamp": "2025-10-29T17:30:00Z",
      "accession_number": "0000320193-23-000106"
    }
  },
  "error": null
}
```

### Error Response Examples

```json
{
  "success": false,
  "data": null,
  "error": "Ticker 'XYZ' not found in SEC EDGAR database."
}
```

```json
{
  "success": false,
  "data": null,
  "error": "No 10-K filing found for AAPL in fiscal year 2009."
}
```

```json
{
  "success": false,
  "data": null,
  "error": "SEC EDGAR rate limit exceeded (10 requests/second). Request blocked."
}
```

---

## 4. Implementation Requirements

### API Configuration

**Base URL:** `https://data.sec.gov`

**Key Endpoints:**
1. **Company Search:** `https://www.sec.gov/files/company_tickers.json`
2. **Company Submissions:** `https://data.sec.gov/submissions/CIK{CIK}.json`
3. **Filing Download:** `https://www.sec.gov/Archives/edgar/data/{CIK}/{ACCESSION}/{FILENAME}`

**CRITICAL: User-Agent Header (MANDATORY)**

```python
headers = {
    'User-Agent': 'basirah-agent contact@basirah.ai',
    'Accept-Encoding': 'gzip, deflate'
}
```

**Why Required:**
- SEC blocks requests without User-Agent header (403 Forbidden)
- Used for compliance monitoring and contact if issues arise
- Format: `{ApplicationName} {EmailAddress}`

### Rate Limiting Strategy

**SEC EDGAR Requirements:**
- **Strict Limit:** 10 requests per second per IP address
- **Enforcement:** Violators may be temporarily or permanently blocked
- **Implementation:** Minimum 110ms between requests (9 req/sec safely under limit)

```python
import time

class SECRateLimiter:
    def __init__(self, min_interval: float = 0.11):
        self.min_interval = min_interval  # 110ms = ~9 req/sec
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Enforce SEC rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
```

### CIK Lookup Process

SEC uses CIK (Central Index Key) not tickers. Must convert ticker → CIK:

**Step 1: Load Ticker-to-CIK Mapping**
```python
import requests

def ticker_to_cik(ticker: str) -> str:
    """Convert ticker to 10-digit CIK"""
    headers = {'User-Agent': 'basirah-agent contact@basirah.ai'}
    response = requests.get(
        'https://www.sec.gov/files/company_tickers.json',
        headers=headers
    )
    
    tickers_data = response.json()
    
    for entry in tickers_data.values():
        if entry['ticker'].upper() == ticker.upper():
            # Pad CIK to 10 digits with leading zeros
            return str(entry['cik_str']).zfill(10)
    
    return None
```

**Step 2: Get Filing List for CIK**
```python
def get_filings_for_cik(cik: str) -> dict:
    """Get all filings for a company"""
    headers = {'User-Agent': 'basirah-agent contact@basirah.ai'}
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    
    response = requests.get(url, headers=headers)
    return response.json()
```

**Step 3: Find Specific Filing**
```python
def find_filing(filings: dict, filing_type: str, year: int) -> dict:
    """Find specific filing by type and year"""
    recent = filings['filings']['recent']
    
    for i, form in enumerate(recent['form']):
        if form == filing_type:
            filing_date = recent['filingDate'][i]
            report_date = recent['reportDate'][i]
            
            # Check if matches requested year
            if year and str(year) in report_date:
                return {
                    'accession_number': recent['accessionNumber'][i],
                    'filing_date': filing_date,
                    'report_date': report_date,
                    'primary_document': recent['primaryDocument'][i]
                }
    
    return None
```

### Text Extraction from HTML

SEC filings are HTML documents. Must extract clean text:

**Requirements:**
1. Remove HTML tags (`<html>`, `<body>`, `<p>`, etc.)
2. Preserve paragraph structure (use `\n\n` for breaks)
3. Remove excessive whitespace
4. Handle special characters (convert HTML entities)
5. Remove tables of contents and navigation elements

**Section Extraction Strategy:**

For 10-K filings, identify sections by common patterns:

| Section | Search Pattern |
|---------|----------------|
| Business | `"Item 1. Business"` or `"Item 1 - Business"` |
| Risk Factors | `"Item 1A. Risk Factors"` |
| MD&A | `"Item 7. Management's Discussion"` |
| Financial Statements | `"Item 8. Financial Statements"` |

**Implementation:**

```python
from bs4 import BeautifulSoup
import re

def extract_section(html_content: str, section_name: str) -> str:
    """Extract specific section from 10-K HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get all text
    text = soup.get_text()
    
    # Define section patterns
    section_patterns = {
        'business': r'Item\s+1[\.\s\-]+Business',
        'risk_factors': r'Item\s+1A[\.\s\-]+Risk\s+Factors',
        'mda': r'Item\s+7[\.\s\-]+Management',
        'financial_statements': r'Item\s+8[\.\s\-]+Financial\s+Statements'
    }
    
    if section_name == 'full':
        return clean_text(text)
    
    pattern = section_patterns.get(section_name)
    if not pattern:
        return clean_text(text)
    
    # Find section start
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return f"Section '{section_name}' not found in filing"
    
    start = match.start()
    
    # Find next section (Item X.)
    next_section = re.search(r'Item\s+\d+[A-Z]?[\.\s\-]', text[start+50:], re.IGNORECASE)
    end = start + 50 + next_section.start() if next_section else len(text)
    
    section_text = text[start:end]
    return clean_text(section_text)

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    # Add paragraph breaks
    text = re.sub(r'\.(\s+[A-Z])', r'.\n\n\1', text)
    
    return text.strip()
```

---

## 5. Error Handling

### Error Types and Recovery Strategies

#### 1. Missing User-Agent Header

**Trigger:** Request made without User-Agent header

**HTTP Status:** 403 Forbidden

**Response:**
```json
{
  "success": false,
  "data": null,
  "error": "SEC EDGAR requires User-Agent header. Ensure 'User-Agent: basirah-agent contact@basirah.ai' is included."
}
```

**Recovery:** Configuration issue - do not retry. Fix implementation.

#### 2. Rate Limit Exceeded

**Trigger:** More than 10 requests per second

**HTTP Status:** 429 Too Many Requests

**Response:**
```json
{
  "success": false,
  "data": null,
  "error": "SEC EDGAR rate limit exceeded (10 requests/second)."
}
```

**Recovery:**
- Implement 110ms minimum interval between requests
- If still triggered, increase to 150ms
- Do not retry aggressively - respect SEC limits

#### 3. Ticker Not Found

**Trigger:** Ticker doesn't exist in SEC database

**HTTP Status:** 404 or empty results

**Response:**
```json
{
  "success": false,
  "data": null,
  "error": "Ticker 'XYZ' not found in SEC EDGAR database."
}
```

**Recovery:** Do not retry. Company may not be publicly traded or uses different ticker.

#### 4. Filing Not Available

**Trigger:** Requested filing doesn't exist for specified year

**Response:**
```json
{
  "success": false,
  "data": null,
  "error": "No 10-K filing found for AAPL in fiscal year 2009."
}
```

**Recovery:** Try previous year or different filing type.

#### 5. CIK Format Error

**Trigger:** CIK not properly padded to 10 digits

**Response:**
```json
{
  "success": false,
  "data": null,
  "error": "CIK must be 10 digits with leading zeros (e.g., 0000320193)."
}
```

**Recovery:** Fix CIK padding in code.

#### 6. Section Not Found

**Trigger:** Requested section doesn't exist in filing

**Response:**
```json
{
  "success": true,
  "data": {
    "content": "Section 'business' not found in filing. Filing structure may vary.",
    "content_length": 67
  }
}
```

**Recovery:** Return partial success with message. Agent can try `section="full"`.

#### 7. Network Timeout

**Trigger:** Filing download takes longer than 60 seconds

**Response:**
```json
{
  "success": false,
  "data": null,
  "error": "SEC EDGAR request timeout after 60 seconds."
}
```

**Recovery:** Retry up to 2 times. Large filings may legitimately take time.

---

## 6. Dependencies

### Required Python Packages

```python
# requirements.txt entries for SEC Filing tool

requests==2.31.0           # HTTP client
beautifulsoup4==4.12.2     # HTML parsing
lxml==4.9.3                # Fast HTML parser backend
python-dotenv==1.0.0       # Environment variables (optional)
```

### Environment Variables

**Optional:** User-Agent can be configured via environment variable

```bash
# .env file (optional)
SEC_USER_AGENT=basirah-agent contact@basirah.ai
```

**Default:** If not set, use hardcoded User-Agent: `"basirah-agent contact@basirah.ai"`

---

## 7. Use Cases for Agent

### Use Case 1: Business Understanding

**Scenario:** Agent needs to understand how Apple makes money

**Tool Call:**
```python
result = sec_filing_tool.execute(
    ticker="AAPL",
    filing_type="10-K",
    section="business"
)
```

**Agent Reasoning:**
```
"Need official business description from 10-K to understand products,
markets, and revenue sources. Extracting 'Business' section only
to minimize token usage."
```

**Expected Output:**
```python
{
  "success": True,
  "data": {
    "content": "Item 1. Business\n\nThe Company designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories..."
  }
}
```

**Agent Action:**
```
"Apple's business model clear: hardware (iPhone 52%, Mac, iPad, wearables)
+ services (App Store, subscriptions). Revenue sources predictable.
Business is within circle of competence."
```

---

### Use Case 2: Risk Assessment

**Scenario:** Agent needs to identify top business risks

**Tool Call:**
```python
result = sec_filing_tool.execute(
    ticker="MSFT",
    filing_type="10-K",
    section="risk_factors"
)
```

**Agent Reasoning:**
```
"Need to understand disclosed risks from company's perspective.
Risk Factors section is Item 1A in 10-K."
```

**Expected Output:**
```python
{
  "success": True,
  "data": {
    "content": "Item 1A. Risk Factors\n\nIntense competition in cloud computing services... cybersecurity threats... regulatory risks..."
  }
}
```

**Agent Action:**
```
"Identified top 3 risks: (1) Cloud competition from AWS/Google,
(2) Cybersecurity threats, (3) Regulatory antitrust scrutiny.
None are disqualifying but require monitoring."
```

---

### Use Case 3: Management Compensation

**Scenario:** Agent evaluating management alignment with shareholders

**Tool Call:**
```python
result = sec_filing_tool.execute(
    ticker="GOOGL",
    filing_type="DEF 14A"  # Proxy statement
)
```

**Agent Reasoning:**
```
"Need executive compensation details to assess shareholder alignment.
Proxy statement (DEF 14A) contains this information."
```

**Expected Output:**
```python
{
  "success": True,
  "data": {
    "content": "EXECUTIVE COMPENSATION\n\nCEO Total Compensation: $XX million\nSalary: $X, Stock Awards: $Y, Performance-based: Z%..."
  }
}
```

**Agent Action:**
```
"CEO compensation $280M seems high, but 85% is performance-based stock
with 4-year vesting. Good alignment with long-term shareholder value.
No red flags."
```

---

### Use Case 4: Management Candor Assessment

**Scenario:** Agent assessing management quality through MD&A

**Tool Call:**
```python
result = sec_filing_tool.execute(
    ticker="BRK.B",
    filing_type="10-K",
    section="mda"
)
```

**Agent Reasoning:**
```
"Need to assess management's tone and transparency. MD&A section
shows how management discusses challenges and opportunities."
```

**Agent Action:**
```
"Management discusses both successes and challenges candidly.
Acknowledges insurance underwriting losses in Q3. Transparent
about capital allocation challenges. High integrity signal."
```

---

## 8. Testing Requirements

### Unit Tests

**Test Coverage Requirements:**
- Ticker to CIK conversion
- All filing types (10-K, 10-Q, DEF 14A, 8-K)
- All sections (business, risk_factors, mda, full)
- User-Agent header validation
- Rate limiting enforcement
- Error handling (ticker not found, filing not available, timeout)
- Text extraction and cleaning

**Test Cases:**

```python
# Test 1: Valid 10-K business section
def test_valid_10k_business():
    result = sec_filing_tool.execute(
        ticker="AAPL",
        filing_type="10-K",
        section="business"
    )
    assert result["success"] == True
    assert "business" in result["data"]["content"].lower()
    assert len(result["data"]["content"]) > 1000

# Test 2: User-Agent header present
def test_user_agent_header():
    tool = SECFilingTool()
    assert 'User-Agent' in tool.session.headers
    assert 'basirah-agent' in tool.session.headers['User-Agent']

# Test 3: Rate limiting
def test_rate_limiting():
    start = time.time()
    sec_filing_tool.execute(ticker="AAPL", filing_type="10-K")
    sec_filing_tool.execute(ticker="MSFT", filing_type="10-K")
    elapsed = time.time() - start
    assert elapsed >= 0.11  # Minimum 110ms between calls

# Test 4: Invalid ticker
def test_invalid_ticker():
    result = sec_filing_tool.execute(
        ticker="INVALID",
        filing_type="10-K"
    )
    assert result["success"] == False
    assert "not found" in result["error"].lower()

# Test 5: Section extraction
def test_section_extraction():
    result = sec_filing_tool.execute(
        ticker="AAPL",
        filing_type="10-K",
        section="risk_factors"
    )
    assert result["success"] == True
    assert "risk" in result["data"]["content"].lower()

# Test 6: CIK padding
def test_cik_padding():
    cik = ticker_to_cik("AAPL")
    assert len(cik) == 10
    assert cik.startswith("0000")
    assert cik == "0000320193"
```

### Integration Tests

**Test Scenarios:**

1. **Complete Investigation Flow:**
   - Get 10-K business section → risk factors → MD&A for same company
   - Verify rate limiting doesn't block legitimate sequential requests
   - Ensure CIK caching avoids redundant lookups

2. **Multi-Filing Analysis:**
   - Get 10-K → 10-Q → DEF 14A for single company
   - Verify data consistency
   - Check URL construction for different filing types

3. **Error Recovery:**
   - Simulate rate limit → verify backoff
   - Request non-existent filing → verify graceful error
   - Request invalid ticker → verify clear error message

4. **Text Extraction Quality:**
   - Verify section boundaries correct
   - Check HTML entity handling (& → &, etc.)
   - Ensure paragraph structure preserved

---

## 9. Python Implementation Example

```python
import os
import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class SECFilingTool:
    """SEC EDGAR Filing Tool for basīrah investment agent"""
    
    @property
    def name(self) -> str:
        return "sec_filing_tool"
    
    @property
    def description(self) -> str:
        return """
        Retrieves corporate filings from SEC EDGAR database.
        
        Capabilities:
        - 10-K annual reports (business description, risk factors, MD&A)
        - 10-Q quarterly reports
        - DEF 14A proxy statements (executive compensation)
        - Section extraction (business, risk_factors, mda)
        
        Use for:
        - Business understanding (10-K Business section)
        - Management evaluation (proxy statements, MD&A)
        - Risk assessment (10-K Risk Factors section)
        """
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "pattern": "^[A-Z]{1,5}$"
                },
                "filing_type": {
                    "type": "string",
                    "enum": ["10-K", "10-Q", "DEF 14A", "8-K"]
                },
                "section": {
                    "type": "string",
                    "enum": ["business", "risk_factors", "mda", "financial_statements", "full"],
                    "default": "full"
                },
                "year": {
                    "type": "integer",
                    "minimum": 2010,
                    "maximum": 2025
                },
                "quarter": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4]
                }
            },
            "required": ["ticker", "filing_type"]
        }
    
    def __init__(self):
        user_agent = os.getenv("SEC_USER_AGENT", "basirah-agent contact@basirah.ai")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate'
        })
        
        self.last_request_time = 0
        self.min_interval = 0.11  # 110ms = ~9 req/sec (safely under 10)
        
        self.ticker_to_cik_cache = {}
    
    def execute(self, ticker: str, filing_type: str, section: str = "full",
                year: Optional[int] = None, quarter: Optional[int] = None) -> Dict[str, Any]:
        """Execute SEC filing retrieval"""
        
        # Validate inputs
        validation_error = self._validate_inputs(ticker, filing_type, section, quarter)
        if validation_error:
            return {"success": False, "data": None, "error": validation_error}
        
        try:
            # Step 1: Convert ticker to CIK
            cik = self._ticker_to_cik(ticker)
            if not cik:
                return {"success": False, "data": None,
                       "error": f"Ticker '{ticker}' not found in SEC EDGAR database"}
            
            # Step 2: Get company filings list
            company_data = self._get_company_filings(cik)
            if not company_data:
                return {"success": False, "data": None,
                       "error": f"Could not retrieve filings for {ticker}"}
            
            # Step 3: Find specific filing
            filing_info = self._find_filing(company_data, filing_type, year, quarter)
            if not filing_info:
                year_str = f" in fiscal year {year}" if year else ""
                return {"success": False, "data": None,
                       "error": f"No {filing_type} filing found for {ticker}{year_str}"}
            
            # Step 4: Download filing
            filing_url = self._construct_filing_url(cik, filing_info)
            html_content = self._download_filing(filing_url)
            
            if not html_content:
                return {"success": False, "data": None,
                       "error": "Failed to download filing content"}
            
            # Step 5: Extract section
            if filing_type in ["10-K", "10-Q"] and section != "full":
                content = self._extract_section(html_content, section)
            else:
                content = self._extract_text(html_content)
            
            # Return success
            return {
                "success": True,
                "data": {
                    "ticker": ticker.upper(),
                    "company_name": company_data.get("name", "Unknown"),
                    "cik": cik,
                    "filing_type": filing_type,
                    "filing_date": filing_info['filing_date'],
                    "fiscal_year": filing_info.get('fiscal_year'),
                    "fiscal_quarter": quarter,
                    "section": section,
                    "content": content,
                    "content_length": len(content),
                    "filing_url": filing_url,
                    "metadata": {
                        "source": "sec_edgar",
                        "timestamp": datetime.now().isoformat(),
                        "accession_number": filing_info['accession_number']
                    }
                },
                "error": None
            }
            
        except Exception as e:
            return {"success": False, "data": None,
                   "error": f"Unexpected error: {str(e)}"}
    
    def _validate_inputs(self, ticker, filing_type, section, quarter):
        if not ticker or not ticker.isupper():
            return "Ticker must be uppercase"
        
        valid_filings = ["10-K", "10-Q", "DEF 14A", "8-K"]
        if filing_type not in valid_filings:
            return f"Invalid filing_type: {filing_type}"
        
        if filing_type == "10-Q" and not quarter:
            return "Quarter required for 10-Q filings"
        
        return None
    
    def _wait_for_rate_limit(self):
        """Enforce SEC rate limiting (10 req/sec)"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _ticker_to_cik(self, ticker: str) -> Optional[str]:
        """Convert ticker to 10-digit CIK"""
        # Check cache
        if ticker in self.ticker_to_cik_cache:
            return self.ticker_to_cik_cache[ticker]
        
        # Rate limit
        self._wait_for_rate_limit()
        
        try:
            response = self.session.get(
                'https://www.sec.gov/files/company_tickers.json',
                timeout=30
            )
            response.raise_for_status()
            tickers_data = response.json()
            
            for entry in tickers_data.values():
                if entry['ticker'].upper() == ticker.upper():
                    cik = str(entry['cik_str']).zfill(10)
                    self.ticker_to_cik_cache[ticker] = cik
                    return cik
            
            return None
        except Exception as e:
            print(f"Error converting ticker to CIK: {e}")
            return None
    
    def _get_company_filings(self, cik: str) -> Optional[Dict]:
        """Get all filings for a company"""
        self._wait_for_rate_limit()
        
        try:
            url = f'https://data.sec.gov/submissions/CIK{cik}.json'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting company filings: {e}")
            return None
    
    def _find_filing(self, company_data: dict, filing_type: str,
                     year: Optional[int], quarter: Optional[int]) -> Optional[Dict]:
        """Find specific filing"""
        recent = company_data['filings']['recent']
        
        for i, form in enumerate(recent['form']):
            if form == filing_type:
                report_date = recent['reportDate'][i]
                
                # Check year match
                if year and str(year) not in report_date:
                    continue
                
                # Extract fiscal year from report date
                fiscal_year = int(report_date.split('-')[0])
                
                return {
                    'accession_number': recent['accessionNumber'][i],
                    'filing_date': recent['filingDate'][i],
                    'report_date': report_date,
                    'primary_document': recent['primaryDocument'][i],
                    'fiscal_year': fiscal_year
                }
        
        return None
    
    def _construct_filing_url(self, cik: str, filing_info: dict) -> str:
        """Construct URL to filing document"""
        # Remove leading zeros and dashes from CIK for URL
        cik_clean = cik.lstrip('0')
        accession_clean = filing_info['accession_number'].replace('-', '')
        
        url = (f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/"
               f"{accession_clean}/{filing_info['primary_document']}")
        
        return url
    
    def _download_filing(self, url: str) -> Optional[str]:
        """Download filing content"""
        self._wait_for_rate_limit()
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error downloading filing: {e}")
            return None
    
    def _extract_text(self, html_content: str) -> str:
        """Extract clean text from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text()
        return self._clean_text(text)
    
    def _extract_section(self, html_content: str, section_name: str) -> str:
        """Extract specific section from filing"""
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text()
        
        # Section patterns
        patterns = {
            'business': r'Item\s+1[\.\s\-]+Business',
            'risk_factors': r'Item\s+1A[\.\s\-]+Risk\s+Factors',
            'mda': r'Item\s+7[\.\s\-]+Management',
            'financial_statements': r'Item\s+8[\.\s\-]+Financial\s+Statements'
        }
        
        pattern = patterns.get(section_name)
        if not pattern:
            return self._clean_text(text)
        
        # Find section
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return f"Section '{section_name}' not found in filing"
        
        start = match.start()
        
        # Find next section
        next_match = re.search(r'Item\s+\d+[A-Z]?[\.\s\-]', text[start+50:], re.IGNORECASE)
        end = start + 50 + next_match.start() if next_match else len(text)
        
        section_text = text[start:end]
        return self._clean_text(section_text)
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        # Add paragraph breaks
        text = re.sub(r'\.(\s+[A-Z])', r'.\n\n\1', text)
        
        return text.strip()


# Example usage
if __name__ == "__main__":
    tool = SECFilingTool()
    
    # Get 10-K business section
    result = tool.execute(
        ticker="AAPL",
        filing_type="10-K",
        section="business"
    )
    
    if result["success"]:
        print(f"Company: {result['data']['company_name']}")
        print(f"Content length: {result['data']['content_length']} chars")
        print(f"First 500 chars:\n{result['data']['content'][:500]}")
```

---

## 10. Reference Documentation

**API Documentation:** `docs/api_references/sec_edgar_api.md`

**Related Tools:**
- `gurufocus_tool_spec.md` - Primary financial data source
- `web_search_tool_spec.md` - For recent news not in filings

**Buffett Principles:** `docs/BUFFETT_PRINCIPLES.md`
- Management Quality evaluation (Section 3)
- Circle of Competence (Section 1)

---

## Conclusion

The SEC Filing Tool provides regulatory document access for business understanding, management evaluation, and risk assessment.

**Key Features:**
- Automatic ticker → CIK conversion
- Section-specific extraction (reduces token usage)
- Rate limiting compliance (9 req/sec)
- Mandatory User-Agent header handling
- HTML parsing with clean text output

**Status:** Ready for Sprint 3 implementation

---

**File:** `docs/tool_specs/sec_filing_tool_spec.md`  
**Size:** ~30KB
