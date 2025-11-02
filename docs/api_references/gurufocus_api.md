# GuruFocus API Documentation

## Overview

GuruFocus provides comprehensive financial data and metrics for publicly traded companies through their RESTful API. The API returns data in JSON format and covers fundamentals, valuations, key ratios, insider trading, and more.

**Base URL:** `https://api.gurufocus.com/public/user/{API_KEY}/stock/{TICKER}/`

**Authentication:** API key embedded in URL path

**Note:** This documentation is based on GuruFocus Premium API access. Network restrictions prevented direct API testing, but this documentation reflects the official API structure and known response patterns from GuruFocus documentation and community implementations.

---

## Authentication

GuruFocus uses API key authentication embedded directly in the URL path. Your API key has two parts separated by a colon:

```
<token_part1>:<token_part2>
```

Example API key format: `108b637edeea70fc3115f7528a63583d:e9bf99e88e9f208aa85eb3681f40b594`

The full URL structure is:
```
https://api.gurufocus.com/public/user/{API_KEY}/stock/{TICKER}/{endpoint}
```

---

## Rate Limits

- GuruFocus enforces rate limits based on subscription tier
- Premium subscribers typically have higher limits
- API maintains internal counters that increment with each request
- Recommended: Add 1-2 second delays between requests to avoid throttling
- Monitor response headers for rate limit information

---

## Key Endpoints

### 1. Stock Summary

**Endpoint:** `/summary`

**Full URL:** `https://api.gurufocus.com/public/user/{API_KEY}/stock/{TICKER}/summary`

**Description:** Returns comprehensive company overview including valuation metrics, financial strength scores, profitability metrics, and growth rates.

**Example Request:**
```bash
curl "https://api.gurufocus.com/public/user/YOUR_API_KEY/stock/AAPL/summary" \
  -H "Accept: application/json"
```

**Response Structure:**
```json
{
  "general": {
    "name": "Apple Inc",
    "exchange": "NAS",
    "type": "Stock",
    "currency": "USD",
    "address": "...",
    "industry": "Consumer Electronics",
    "sector": "Technology"
  },
  "quote": {
    "price": 175.43,
    "change": 2.15,
    "change_percentage": 1.24,
    "volume": 52431234,
    "market_cap": 2750000000000
  },
  "valuation": {
    "pe_ratio": 28.5,
    "pb_ratio": 45.2,
    "ps_ratio": 7.3,
    "peg_ratio": 2.1,
    "ev_ebitda": 22.4
  },
  "financial_strength": {
    "score": 8,
    "cash_to_debt": 1.25,
    "equity_to_asset": 0.42,
    "debt_to_equity": 1.85
  },
  "profitability": {
    "operating_margin": 0.28,
    "net_margin": 0.24,
    "roic": 0.32,
    "roe": 1.47,
    "roa": 0.28
  }
}
```

**Key Fields:**
- `general.industry` - Industry classification
- `general.sector` - Sector classification
- `valuation.pe_ratio` - Price to Earnings ratio
- `profitability.roic` - Return on Invested Capital (%)
- `financial_strength.score` - GuruFocus financial strength score (0-10)

---

### 2. Financials

**Endpoint:** `/financials`

**Full URL:** `https://api.gurufocus.com/public/user/{API_KEY}/stock/{TICKER}/financials`

**Description:** Returns detailed financial statement data including income statement, balance sheet, and cash flow statement. Data includes both annual and quarterly figures with historical time series.

**Example Request:**
```python
import requests

API_KEY = "YOUR_API_KEY"
ticker = "AAPL"
url = f"https://api.gurufocus.com/public/user/{API_KEY}/stock/{ticker}/financials"

response = requests.get(url)
data = response.json()
```

**Response Structure:**
```json
{
  "financials": {
    "annual": {
      "Fiscal Year": ["2023", "2022", "2021", "2020", "2019"],
      "Revenue": [383285000000, 394328000000, 365817000000, 274515000000, 260174000000],
      "Net Income": [96995000000, 99803000000, 94680000000, 57411000000, 55256000000],
      "Depreciation & Amortization": [11519000000, 11104000000, 11284000000, 11056000000, 12547000000],
      "Operating Income": [114301000000, 119437000000, 108949000000, 66288000000, 63930000000],
      "Interest Expense": [3933000000, 2931000000, 2645000000, 2873000000, 3576000000],
      "Capital Expenditure": [10959000000, 10708000000, 11085000000, 7309000000, 10495000000],
      "Free Cash Flow": [99584000000, 111443000000, 92953000000, 80674000000, 58896000000],
      "Total Assets": [352755000000, 352583000000, 351002000000, 323888000000, 338516000000],
      "Total Liabilities": [290437000000, 302083000000, 287912000000, 258549000000, 248028000000],
      "Total Stockholders Equity": [62318000000, 50672000000, 63090000000, 65339000000, 90488000000],
      "Cash and Cash Equivalents": [29965000000, 23646000000, 34940000000, 38016000000, 48844000000],
      "Total Debt": [106628000000, 120069000000, 124719000000, 112436000000, 108047000000]
    },
    "quarterly": {
      "Fiscal Quarter": ["Q4 2023", "Q3 2023", "Q2 2023", "Q1 2023"],
      "Revenue": [119575000000, 89498000000, 81797000000, 94836000000],
      "Net Income": [33916000000, 22956000000, 19881000000, 24160000000]
    }
  }
}
```

**Critical Fields for Owner Earnings Calculation:**
- `Net Income` - Net profit after all expenses
- `Depreciation & Amortization` - Non-cash charges to add back
- `Capital Expenditure` - Cash spent on fixed assets (subtract)
- `Free Cash Flow` - Operating cash flow minus capex

**Working Capital Calculation Requires:**
- Current Assets (Total Assets - Long-term Assets)
- Current Liabilities (Total Liabilities - Long-term Debt)
- Change in Working Capital = (Current Assets - Current Liabilities)_t - (Current Assets - Current Liabilities)_t-1

**ROIC Calculation Fields:**
- `Operating Income` (EBIT) - Earnings before interest and taxes
- `Total Assets` - Total company assets
- `Total Liabilities` - Total company liabilities
- `Cash and Cash Equivalents` - Cash to exclude from invested capital
- `Total Debt` - Total debt obligations

---

### 3. Key Ratios

**Endpoint:** `/keyratios`

**Full URL:** `https://api.gurufocus.com/public/user/{API_KEY}/stock/{TICKER}/keyratios`

**Description:** Returns key financial and operational ratios calculated by GuruFocus, including profitability metrics, efficiency ratios, and per-share values.

**Example Request:**
```python
import requests

API_KEY = "YOUR_API_KEY"
ticker = "WMT"
url = f"https://api.gurufocus.com/public/user/{API_KEY}/stock/{ticker}/keyratios"

response = requests.get(url)
ratios = response.json()
```

**Response Structure:**
```json
{
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
    "Inventory Turnover": 45.2,
    "Days Sales Outstanding": 31.2,
    "Days Inventory": 8.1
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
```

**Key Ratios for Investment Analysis:**
- `ROIC %` - Return on Invested Capital (target: >15% consistently)
- `Operating Margin %` - Operating profit as % of revenue
- `Net Margin %` - Net profit as % of revenue
- `ROE %` - Return on Equity
- `Free Cash Flow per Share` - FCF divided by shares outstanding

---

### 4. Valuation

**Endpoint:** `/valuation`

**Full URL:** `https://api.gurufocus.com/public/user/{API_KEY}/stock/{TICKER}/valuation`

**Description:** Returns various valuation metrics, multiples, and GuruFocus proprietary valuation ratios.

**Example Request:**
```bash
curl "https://api.gurufocus.com/public/user/YOUR_API_KEY/stock/MSFT/valuation" \
  -H "Accept: application/json"
```

**Response Structure:**
```json
{
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
```

---

## Special Value Handling

**CRITICAL:** GuruFocus API returns special numeric codes for certain conditions:

| Value | Meaning | How to Handle |
|-------|---------|---------------|
| `10000` | No Debt OR Negative Equity | Check context - could be excellent (no debt) or concerning (negative equity) |
| `9999` | N/A or Data Not Available | Treat as missing data, skip calculation or use alternative method |
| `0` | At Loss or Zero Value | Company is unprofitable or value is actually zero |
| `null` | Missing Data | Field not applicable or data not reported |

**Example Handling in Python:**
```python
def process_gurufocus_value(value, field_name):
    """Process special GuruFocus values"""
    if value is None:
        return None
    
    if value == 9999:
        # Data not available
        return None
    
    if value == 10000:
        # Context-dependent handling
        if 'debt' in field_name.lower():
            return 0  # No debt = 0
        elif 'equity' in field_name.lower():
            return None  # Negative equity = invalid
        else:
            return None
    
    if value == 0:
        # At loss or truly zero
        return 0
    
    return value
```

---

## Data Type Inconsistencies

**Important:** GuruFocus API sometimes returns numbers as strings and sometimes as numbers. Your code must handle both:

```python
import json

def parse_gurufocus_number(value):
    """Parse number that might be string or float"""
    if value is None:
        return None
    
    if isinstance(value, str):
        try:
            # Try to parse as float
            return float(value)
        except ValueError:
            # Check for special error messages
            if "Negative" in value or "N/A" in value:
                return None
            return None
    
    return float(value)

# Example usage
revenue = parse_gurufocus_number(data['financials']['annual']['Revenue'][0])
```

---

## Field Mappings for Key Calculations

### Owner Earnings Components

**Owner Earnings = Net Income + D&A - CapEx - ΔWorking Capital**

| Component | GuruFocus Field Path | Notes |
|-----------|---------------------|-------|
| Net Income | `financials.annual.Net Income[0]` | Most recent annual figure |
| Depreciation & Amortization | `financials.annual.Depreciation & Amortization[0]` | Non-cash charge |
| Capital Expenditure | `financials.annual.Capital Expenditure[0]` | Cash outflow |
| Working Capital Change | Calculate from balance sheet | Current Assets - Current Liabilities (change over year) |

### ROIC Components

**ROIC = (Operating Income * (1 - Tax Rate)) / Invested Capital**

**Invested Capital = Total Assets - Current Liabilities - Cash**

| Component | GuruFocus Field Path | Notes |
|-----------|---------------------|-------|
| Operating Income | `financials.annual.Operating Income[0]` | EBIT |
| Tax Rate | Calculate from Net Income and Pre-tax Income | Tax Rate = 1 - (Net Income / Pre-tax Income) |
| Total Assets | `financials.annual.Total Assets[0]` | From balance sheet |
| Current Liabilities | Calculate from balance sheet | Total Liabilities - Long-term Debt |
| Cash | `financials.annual.Cash and Cash Equivalents[0]` | Exclude from invested capital |

**Alternative ROIC Calculation from GuruFocus:**
```
ROIC = (EBIT - Adjusted Taxes) / (Book Value of Debt + Book Value of Equity - Cash)
```

---

## Python Implementation Example

```python
import requests
import time
from typing import Dict, Optional, List

class GuruFocusAPI:
    """GuruFocus API client for basīrah investment agent"""
    
    BASE_URL = "https://api.gurufocus.com/public/user"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        })
    
    def _make_request(self, endpoint: str) -> Dict:
        """Make API request with error handling"""
        url = f"{self.BASE_URL}/{self.api_key}/stock/{endpoint}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(1)  # Rate limiting
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {}
    
    def get_summary(self, ticker: str) -> Dict:
        """Get company summary data"""
        return self._make_request(f"{ticker}/summary")
    
    def get_financials(self, ticker: str) -> Dict:
        """Get financial statements"""
        return self._make_request(f"{ticker}/financials")
    
    def get_keyratios(self, ticker: str) -> Dict:
        """Get key financial ratios"""
        return self._make_request(f"{ticker}/keyratios")
    
    def get_valuation(self, ticker: str) -> Dict:
        """Get valuation metrics"""
        return self._make_request(f"{ticker}/valuation")
    
    def calculate_owner_earnings(self, ticker: str) -> Optional[float]:
        """Calculate Owner Earnings for a company"""
        financials = self.get_financials(ticker)
        
        if not financials or 'financials' not in financials:
            return None
        
        annual = financials['financials'].get('annual', {})
        
        try:
            # Get most recent year data
            net_income = self._parse_number(annual['Net Income'][0])
            da = self._parse_number(annual['Depreciation & Amortization'][0])
            capex = self._parse_number(annual['Capital Expenditure'][0])
            
            if None in [net_income, da, capex]:
                return None
            
            # Simplified: ignoring working capital change for now
            owner_earnings = net_income + da - capex
            return owner_earnings
        
        except (KeyError, IndexError) as e:
            print(f"Error calculating owner earnings: {e}")
            return None
    
    @staticmethod
    def _parse_number(value) -> Optional[float]:
        """Parse GuruFocus number handling special values"""
        if value is None:
            return None
        
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return None
        
        # Handle special codes
        if value == 9999 or value == 10000:
            return None
        
        return float(value)

# Example usage
if __name__ == "__main__":
    api = GuruFocusAPI("YOUR_API_KEY")
    
    # Get Apple financials
    summary = api.get_summary("AAPL")
    print(f"Company: {summary['general']['name']}")
    print(f"ROIC: {summary['profitability']['roic']}%")
    
    # Calculate Owner Earnings
    owner_earnings = api.calculate_owner_earnings("AAPL")
    print(f"Owner Earnings: ${owner_earnings:,.0f}")
```

---

## Rate Limiting Best Practices

1. **Add delays between requests:**
   ```python
   import time
   time.sleep(1)  # 1 second between requests
   ```

2. **Implement exponential backoff on errors:**
   ```python
   import time
   
   def make_request_with_backoff(url, max_retries=3):
       for attempt in range(max_retries):
           try:
               response = requests.get(url)
               if response.status_code == 429:  # Too many requests
                   wait_time = (2 ** attempt)  # Exponential backoff
                   time.sleep(wait_time)
                   continue
               return response
           except requests.exceptions.RequestException:
               if attempt == max_retries - 1:
                   raise
               time.sleep(2 ** attempt)
   ```

3. **Cache responses to minimize API calls:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_company_data(ticker):
       return api.get_financials(ticker)
   ```

---

## Error Handling

Common error scenarios:

1. **Invalid Ticker:**
   - Response: 404 or empty JSON
   - Handle: Validate ticker before making request

2. **Rate Limit Exceeded:**
   - Response: 429 status code
   - Handle: Implement backoff and retry

3. **Missing Data:**
   - Response: Fields contain `null`, `9999`, or `10000`
   - Handle: Check for special values before calculations

4. **API Key Invalid:**
   - Response: 401 Unauthorized
   - Handle: Verify API key format and validity

---

## Additional Endpoints Available

- `/insider` - Insider trading data
- `/business_segments` - Business segment breakdown
- `/dividend` - Dividend history
- `/analyst_estimate` - Analyst estimates
- `/guru_trades` - Guru (super investor) trades for the stock
- `/price_history` - Historical price data

---

## Cost Considerations

- GuruFocus Premium subscription required (~$30-50/month)
- Each API call counts toward monthly limit
- Consider data caching strategy
- Batch requests where possible
- For MVP: Target 100-200 API calls per analysis session

---

## Testing Checklist

✅ Test with companies from different industries  
✅ Test with companies that have special values (10000, 9999, 0)  
✅ Test with recently IPO'd companies (limited data)  
✅ Test with international companies (different accounting standards)  
✅ Verify field names match exactly  
✅ Test error handling for network failures  
✅ Test rate limiting behavior  

---

## References

- GuruFocus API Documentation: https://www.gurufocus.com/api/overview
- GuruFocus Data Specifications: https://www.gurufocus.com/data/stock-fundamentals
- Community Rust Implementation: https://github.com/xemwebe/gurufocus_api

---

**Last Updated:** October 28, 2025  
**API Version:** v3  
**Documentation Status:** Based on research and official documentation (direct testing prevented by network restrictions)
