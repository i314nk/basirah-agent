# SEC EDGAR API Documentation

## Overview

The SEC (Securities and Exchange Commission) EDGAR (Electronic Data Gathering, Analysis, and Retrieval) system provides free public access to corporate filings through REST APIs. This is a critical data source for the basīrah investment agent to access 10-K annual reports, 10-Q quarterly reports, and other SEC filings.

**Base URL:** `https://data.sec.gov`

**Authentication:** None required (but User-Agent header mandatory)

**Rate Limit:** 10 requests per second per IP address

**Cost:** FREE

---

## Critical Requirements

### User-Agent Header (MANDATORY)

**The SEC requires ALL requests to include a proper User-Agent header.** Requests without this header will be blocked.

**Format:** `User-Agent: CompanyName AdminEmail@company.com`

**Example:**
```
User-Agent: basīrah-agent contact@basirah.ai
```

**Why it matters:** The SEC uses User-Agent strings to:
- Identify requesters for compliance monitoring
- Contact users if request patterns are problematic
- Block abusive scrapers

**Python Example:**
```python
import requests

headers = {
    'User-Agent': 'basīrah-agent contact@basirah.ai',
    'Accept-Encoding': 'gzip, deflate'
}

response = requests.get(
    'https://data.sec.gov/submissions/CIK0000320193.json',
    headers=headers
)
```

---

## Rate Limiting

**Strict Limit:** 10 requests per second per IP address

**Enforcement:** Violators may be temporarily or permanently blocked

**Best Practices:**
1. Space out requests (minimum 100ms between calls)
2. Implement request throttling
3. Cache responses to avoid repeated calls
4. Use bulk downloads for large datasets

**Python Rate Limiting Example:**
```python
import time
import requests

class SECAPIClient:
    def __init__(self, user_agent: str):
        self.headers = {'User-Agent': user_agent}
        self.last_request_time = 0
        self.min_interval = 0.11  # 110ms = ~9 req/sec (safely under 10)
    
    def make_request(self, url: str):
        # Enforce rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        response = requests.get(url, headers=self.headers)
        self.last_request_time = time.time()
        return response
```

---

## Key Endpoints

### 1. Company Submissions (CIK Lookup)

**Endpoint:** `/submissions/CIK{CIK}.json`

**Description:** Returns complete filing history and company metadata for a given CIK (Central Index Key). This is the primary endpoint for discovering available filings.

**CIK Format:**
- 10 digits with leading zeros
- Example: Apple's CIK is `0000320193`
- Non-padded CIKs will fail (e.g., `320193` won't work, must be `0000320193`)

**Full URL Example:**
```
https://data.sec.gov/submissions/CIK0000320193.json
```

**Request Example:**
```python
import requests

headers = {'User-Agent': 'basīrah-agent contact@basirah.ai'}
cik = '0000320193'  # Apple

response = requests.get(
    f'https://data.sec.gov/submissions/CIK{cik}.json',
    headers=headers
)

data = response.json()
```

**Response Structure:**
```json
{
  "cik": "320193",
  "entityType": "operating",
  "sic": "3571",
  "sicDescription": "Electronic Computers",
  "insiderTransactionForOwnerExists": 0,
  "insiderTransactionForIssuerExists": 1,
  "name": "Apple Inc.",
  "tickers": ["AAPL"],
  "exchanges": ["Nasdaq"],
  "ein": "942404110",
  "description": "Technology company...",
  "category": "Large accelerated filer",
  "fiscalYearEnd": "0930",
  "stateOfIncorporation": "CA",
  "addresses": {
    "mailing": {
      "street1": "ONE APPLE PARK WAY",
      "city": "CUPERTINO",
      "stateOrCountry": "CA",
      "zipCode": "95014"
    }
  },
  "filings": {
    "recent": {
      "accessionNumber": [
        "0000320193-23-000106",
        "0000320193-23-000077",
        "..."
      ],
      "filingDate": [
        "2023-11-03",
        "2023-08-04",
        "..."
      ],
      "reportDate": [
        "2023-09-30",
        "2023-07-01",
        "..."
      ],
      "form": [
        "10-K",
        "10-Q",
        "..."
      ],
      "primaryDocument": [
        "aapl-20230930.htm",
        "aapl-20230701.htm",
        "..."
      ],
      "primaryDocDescription": [
        "10-K - Annual report",
        "10-Q - Quarterly report",
        "..."
      ]
    },
    "files": []
  }
}
```

**Key Fields:**
- `cik` - Company's CIK number
- `name` - Official company name
- `tickers` - Array of ticker symbols
- `fiscalYearEnd` - Fiscal year end date (MMDD format)
- `filings.recent.accessionNumber[]` - Unique filing identifiers
- `filings.recent.form[]` - Filing types (10-K, 10-Q, 8-K, etc.)
- `filings.recent.primaryDocument[]` - Main document filenames
- `filings.recent.filingDate[]` - Dates filings were submitted

**Important Notes:**
- `recent` array contains most recent 1000 filings
- For older filings, use pagination via `files` array
- Accession numbers are needed to download actual filing documents

---

### 2. Ticker to CIK Mapping

**Challenge:** API requires CIK but users think in tickers (AAPL, MSFT, etc.)

**Solution:** Use submissions endpoint to map ticker to CIK

**Endpoint:** SEC provides a company tickers JSON file

**URL:** `https://www.sec.gov/files/company_tickers.json`

**Request Example:**
```python
import requests
import json

headers = {'User-Agent': 'basīrah-agent contact@basirah.ai'}
response = requests.get(
    'https://www.sec.gov/files/company_tickers.json',
    headers=headers
)

tickers_data = response.json()
```

**Response Structure:**
```json
{
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
  "...": "..."
}
```

**Lookup Function:**
```python
def ticker_to_cik(ticker: str) -> str:
    """Convert ticker symbol to CIK with leading zeros"""
    headers = {'User-Agent': 'basīrah-agent contact@basirah.ai'}
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

# Example
cik = ticker_to_cik('AAPL')  # Returns '0000320193'
```

---

### 3. Downloading Filing Documents

**Base URL for Filings:** `https://www.sec.gov/Archives/edgar/data/{CIK}/{ACCESSION_NUMBER}/{FILENAME}`

**Components:**
- `CIK` - Without leading zeros (e.g., `320193` not `0000320193`)
- `ACCESSION_NUMBER` - Accession number without dashes (e.g., `000032019323000106`)
- `FILENAME` - Primary document filename (e.g., `aapl-20230930.htm`)

**Example URLs:**

Apple 10-K for fiscal year 2023:
```
https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm
```

**Download Function:**
```python
def download_filing(cik: str, accession: str, filename: str) -> str:
    """
    Download SEC filing document
    
    Args:
        cik: CIK without leading zeros
        accession: Accession number with dashes removed
        filename: Primary document filename
    
    Returns:
        Filing content as text
    """
    # Remove dashes from accession number
    accession_clean = accession.replace('-', '')
    
    # Remove leading zeros from CIK for URL
    cik_clean = str(int(cik))
    
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{accession_clean}/{filename}"
    
    headers = {'User-Agent': 'basīrah-agent contact@basirah.ai'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.text

# Example usage
cik = '0000320193'
accession = '0000320193-23-000106'
filename = 'aapl-20230930.htm'

filing_html = download_filing(cik, accession, filename)
```

---

### 4. Company Concepts (XBRL Financial Data)

**Endpoint:** `/api/xbrl/companyconcept/CIK{CIK}/us-gaap/{TAG}.json`

**Description:** Returns all XBRL disclosures for a single company and accounting concept (e.g., revenue, assets).

**US GAAP Tags Examples:**
- `AccountsPayableCurrent` - Accounts Payable
- `Assets` - Total Assets
- `Liabilities` - Total Liabilities
- `StockholdersEquity` - Stockholders' Equity
- `Revenues` - Revenue
- `NetIncomeLoss` - Net Income
- `OperatingIncomeLoss` - Operating Income
- `DepreciationDepletionAndAmortization` - D&A

**Full URL Example:**
```
https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/Assets.json
```

**Request Example:**
```python
import requests

headers = {'User-Agent': 'basīrah-agent contact@basirah.ai'}
cik = '0000320193'
tag = 'Assets'

response = requests.get(
    f'https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json',
    headers=headers
)

concept_data = response.json()
```

**Response Structure:**
```json
{
  "cik": 320193,
  "taxonomy": "us-gaap",
  "tag": "Assets",
  "label": "Assets",
  "description": "Sum of the carrying amounts as of the balance sheet date of all assets...",
  "entityName": "Apple Inc.",
  "units": {
    "USD": [
      {
        "end": "2023-09-30",
        "val": 352755000000,
        "accn": "0000320193-23-000106",
        "fy": 2023,
        "fp": "FY",
        "form": "10-K",
        "filed": "2023-11-03",
        "frame": "CY2023Q3I"
      },
      {
        "end": "2022-09-24",
        "val": 352583000000,
        "accn": "0000320193-22-000108",
        "fy": 2022,
        "fp": "FY",
        "form": "10-K",
        "filed": "2022-10-28"
      }
    ]
  }
}
```

**Key Fields:**
- `units.USD[]` - Array of reported values over time
- `end` - Reporting period end date
- `val` - Reported value
- `fy` - Fiscal year
- `fp` - Fiscal period (FY, Q1, Q2, Q3, Q4)
- `form` - Filing type that reported this value

---

### 5. Company Facts (All XBRL Data)

**Endpoint:** `/api/xbrl/companyfacts/CIK{CIK}.json`

**Description:** Returns ALL XBRL concepts for a company in a single call. This is extremely useful for getting comprehensive financial data.

**Full URL Example:**
```
https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json
```

**Request Example:**
```python
import requests

headers = {'User-Agent': 'basīrah-agent contact@basirah.ai'}
cik = '0000320193'

response = requests.get(
    f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',
    headers=headers
)

all_facts = response.json()
```

**Response Structure:**
```json
{
  "cik": 320193,
  "entityName": "Apple Inc.",
  "facts": {
    "dei": {
      "EntityCommonStockSharesOutstanding": {
        "label": "Entity Common Stock, Shares Outstanding",
        "description": "Indicate number of shares...",
        "units": {
          "shares": [
            {
              "end": "2023-09-30",
              "val": 15550061000,
              "accn": "0000320193-23-000106",
              "fy": 2023,
              "fp": "FY",
              "form": "10-K",
              "filed": "2023-11-03"
            }
          ]
        }
      }
    },
    "us-gaap": {
      "Assets": {
        "label": "Assets",
        "description": "...",
        "units": {"USD": [...]}
      },
      "Revenues": {
        "label": "Revenues",
        "description": "...",
        "units": {"USD": [...]}
      },
      "NetIncomeLoss": {
        "label": "Net Income",
        "description": "...",
        "units": {"USD": [...]}
      }
    }
  }
}
```

**Accessing Data:**
```python
# Get all assets values
assets_data = all_facts['facts']['us-gaap']['Assets']['units']['USD']

# Get most recent assets value
latest_assets = assets_data[0]['val']  # Arrays are sorted newest first

# Get revenues
revenues_data = all_facts['facts']['us-gaap']['Revenues']['units']['USD']
```

---

## Extracting Text from 10-K Filings

10-K filings are HTML documents with sections. The agent needs to extract specific sections like:
- Item 1: Business
- Item 1A: Risk Factors
- Item 7: Management's Discussion and Analysis (MD&A)

**Basic Approach:**

```python
from bs4 import BeautifulSoup
import re

def extract_10k_section(html_content: str, item_number: str) -> str:
    """
    Extract specific section from 10-K filing
    
    Args:
        html_content: Full 10-K HTML content
        item_number: Section to extract (e.g., '1', '1A', '7')
    
    Returns:
        Extracted section text
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find section headers (patterns vary by company)
    patterns = [
        f"Item {item_number}.",
        f"Item {item_number}:",
        f"ITEM {item_number}.",
        f"ITEM {item_number}:"
    ]
    
    # Search for section start
    section_start = None
    for pattern in patterns:
        # Find the tag containing the pattern
        for tag in soup.find_all(text=re.compile(pattern, re.IGNORECASE)):
            section_start = tag.parent
            break
        if section_start:
            break
    
    if not section_start:
        return "Section not found"
    
    # Extract text until next item or end
    text_parts = []
    for sibling in section_start.next_siblings:
        if sibling.name:
            text = sibling.get_text(strip=True)
            # Stop if we hit the next item
            if re.match(r'Item \d+[A-Z]?\.', text, re.IGNORECASE):
                break
            text_parts.append(text)
    
    return '\n\n'.join(text_parts)

# Example usage
filing_html = download_filing('0000320193', '0000320193-23-000106', 'aapl-20230930.htm')
business_section = extract_10k_section(filing_html, '1')
risks_section = extract_10k_section(filing_html, '1A')
mda_section = extract_10k_section(filing_html, '7')
```

**Note:** Section extraction can be complex as companies format 10-Ks differently. Consider using specialized libraries like `sec-edgar-downloader` or `edgartools` for production.

---

## Comprehensive Python Implementation

```python
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime

class SECEdgarAPI:
    """
    SEC EDGAR API client for basīrah investment agent
    Handles rate limiting, CIK lookup, and filing retrieval
    """
    
    BASE_URL = "https://data.sec.gov"
    ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
    
    def __init__(self, user_agent: str):
        """
        Initialize SEC API client
        
        Args:
            user_agent: User-Agent string (format: "CompanyName email@company.com")
        """
        self.user_agent = user_agent
        self.headers = {
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate'
        }
        self.last_request_time = 0
        self.min_interval = 0.11  # 110ms = ~9 req/sec
    
    def _rate_limit(self):
        """Enforce rate limiting: max 10 requests/second"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> requests.Response:
        """Make rate-limited API request"""
        self._rate_limit()
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response
    
    def ticker_to_cik(self, ticker: str) -> Optional[str]:
        """
        Convert ticker symbol to CIK
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
        
        Returns:
            CIK with leading zeros (e.g., '0000320193') or None
        """
        url = 'https://www.sec.gov/files/company_tickers.json'
        response = self._make_request(url)
        tickers_data = response.json()
        
        for entry in tickers_data.values():
            if entry['ticker'].upper() == ticker.upper():
                return str(entry['cik_str']).zfill(10)
        
        return None
    
    def get_company_submissions(self, cik: str) -> Dict:
        """
        Get all filings for a company
        
        Args:
            cik: CIK with leading zeros
        
        Returns:
            Company metadata and filings history
        """
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        response = self._make_request(url)
        return response.json()
    
    def get_recent_10k(self, ticker: str) -> Optional[Dict]:
        """
        Get most recent 10-K filing info for a ticker
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dict with accession number, filing date, and document name
        """
        cik = self.ticker_to_cik(ticker)
        if not cik:
            return None
        
        submissions = self.get_company_submissions(cik)
        filings = submissions['filings']['recent']
        
        # Find first 10-K in recent filings
        for i, form in enumerate(filings['form']):
            if form == '10-K':
                return {
                    'cik': cik,
                    'accession': filings['accessionNumber'][i],
                    'filing_date': filings['filingDate'][i],
                    'report_date': filings['reportDate'][i],
                    'primary_document': filings['primaryDocument'][i]
                }
        
        return None
    
    def download_filing(self, cik: str, accession: str, filename: str) -> str:
        """
        Download filing document
        
        Args:
            cik: CIK (with or without leading zeros)
            accession: Accession number (with dashes)
            filename: Primary document filename
        
        Returns:
            Filing content as text
        """
        # Clean CIK and accession for URL
        cik_clean = str(int(cik))
        accession_clean = accession.replace('-', '')
        
        url = f"{self.ARCHIVES_URL}/{cik_clean}/{accession_clean}/{filename}"
        response = self._make_request(url)
        return response.text
    
    def get_company_facts(self, cik: str) -> Dict:
        """
        Get all XBRL facts for a company
        
        Args:
            cik: CIK with leading zeros
        
        Returns:
            All reported XBRL facts
        """
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        response = self._make_request(url)
        return response.json()
    
    def get_financial_metric(self, cik: str, metric: str, fiscal_year: Optional[int] = None) -> Optional[float]:
        """
        Get specific financial metric for a company
        
        Args:
            cik: CIK with leading zeros
            metric: US-GAAP tag (e.g., 'Assets', 'Revenues', 'NetIncomeLoss')
            fiscal_year: Specific fiscal year (None for most recent)
        
        Returns:
            Metric value or None
        """
        facts = self.get_company_facts(cik)
        
        try:
            metric_data = facts['facts']['us-gaap'][metric]['units']['USD']
            
            # Filter for annual data (form = 10-K)
            annual_data = [d for d in metric_data if d['form'] == '10-K']
            
            if not annual_data:
                return None
            
            if fiscal_year:
                # Find specific year
                for data_point in annual_data:
                    if data_point['fy'] == fiscal_year:
                        return data_point['val']
                return None
            else:
                # Return most recent
                return annual_data[0]['val']
        
        except (KeyError, IndexError):
            return None

# Example Usage
if __name__ == "__main__":
    # Initialize client
    api = SECEdgarAPI("basīrah-agent contact@basirah.ai")
    
    # Get Apple's CIK
    cik = api.ticker_to_cik("AAPL")
    print(f"Apple CIK: {cik}")
    
    # Get most recent 10-K
    filing_info = api.get_recent_10k("AAPL")
    print(f"Most recent 10-K: {filing_info['filing_date']}")
    
    # Download 10-K
    filing_content = api.download_filing(
        filing_info['cik'],
        filing_info['accession'],
        filing_info['primary_document']
    )
    print(f"Downloaded 10-K: {len(filing_content)} characters")
    
    # Get specific financial metrics
    assets = api.get_financial_metric(cik, 'Assets')
    revenue = api.get_financial_metric(cik, 'Revenues')
    net_income = api.get_financial_metric(cik, 'NetIncomeLoss')
    
    print(f"Assets: ${assets:,.0f}")
    print(f"Revenue: ${revenue:,.0f}")
    print(f"Net Income: ${net_income:,.0f}")
```

---

## Use Cases for Investment Agent

### 1. Company Due Diligence
- Download and analyze 10-K for business description
- Extract risk factors from Item 1A
- Review MD&A (Item 7) for management commentary

### 2. Financial Analysis
- Use Company Facts API for comprehensive XBRL data
- Extract key financial statement items
- Track metrics over time

### 3. Management Quality Assessment
- Read "Letter to Shareholders" sections
- Analyze MD&A for candor and transparency
- Check for accounting changes or restatements

### 4. Red Flag Detection
- Monitor for insider selling (Form 4 filings)
- Check for going concern warnings
- Review auditor opinions

---

## Bulk Data Downloads

For large-scale analysis, SEC provides bulk data files:

**Company Facts ZIP:**
```
https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip
```

**Submissions ZIP:**
```
https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip
```

These are updated nightly and contain all company data.

---

## Error Handling

```python
def safe_sec_request(api_client, func, *args, **kwargs):
    """Wrapper for safe SEC API requests with error handling"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("ERROR: Request forbidden. Check User-Agent header.")
        elif e.response.status_code == 429:
            print("ERROR: Rate limit exceeded. Backing off...")
            time.sleep(5)
            return func(*args, **kwargs)  # Retry once
        else:
            print(f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection failed. Check internet connection.")
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
```

---

## Best Practices

1. **Always include User-Agent header** - Non-negotiable
2. **Respect rate limits** - 10 req/sec maximum
3. **Cache responses** - Avoid redundant API calls
4. **Use bulk downloads** for historical analysis
5. **Handle errors gracefully** - Network issues are common
6. **Parse XBRL carefully** - Data quality varies by company
7. **Validate CIK format** - Must have leading zeros for API calls

---

## Testing Checklist

✅ Test CIK lookup for various tickers  
✅ Test with padded and non-padded CIKs  
✅ Verify User-Agent header is sent  
✅ Test rate limiting enforcement  
✅ Test 10-K download and parsing  
✅ Test XBRL data extraction  
✅ Handle missing data gracefully  
✅ Test error scenarios (404, 429, 403)  

---

## Additional Resources

- **Official SEC API Documentation:** https://www.sec.gov/edgar/sec-api-documentation
- **EDGAR Search:** https://www.sec.gov/edgar/search/
- **Python Library (sec-edgar-downloader):** https://pypi.org/project/sec-edgar-downloader/
- **Python Library (sec-api):** https://pypi.org/project/sec-api/
- **EDGAR Developer Resources:** https://www.sec.gov/about/developer-resources

---

**Last Updated:** October 28, 2025  
**API Version:** Current  
**Cost:** FREE  
**Rate Limit:** 10 requests/second
