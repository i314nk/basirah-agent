# GuruFocus Tool Specification

## Tool Name: `gurufocus_tool`

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Status:** Sprint 2 - Ready for Implementation

---

## 1. Purpose & Use Cases

### Purpose

The GuruFocus Tool provides access to comprehensive financial data from the GuruFocus Premium API, enabling the basīrah agent to retrieve company summaries, financial statements, key ratios, and valuation metrics.

### When Agent Should Use This Tool

```
PHASE 1 (Initial Screening):
  → gurufocus_tool(ticker="AAPL", endpoint="summary")
  
PHASE 5 (Financial Analysis):
  → gurufocus_tool(ticker="AAPL", endpoint="financials")
  → gurufocus_tool(ticker="AAPL", endpoint="keyratios")
  
PHASE 6 (Valuation):
  → gurufocus_tool(ticker="AAPL", endpoint="valuation")
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
      "description": "Stock ticker symbol",
      "pattern": "^[A-Z]{1,5}$"
    },
    "endpoint": {
      "type": "string",
      "enum": ["summary", "financials", "keyratios", "valuation"]
    },
    "period": {
      "type": "string",
      "enum": ["annual", "quarterly"],
      "default": "annual"
    }
  },
  "required": ["ticker", "endpoint"]
}
```

---

## 3. Output Format

### Standard Response

```json
{
  "success": bool,
  "data": {
    "ticker": str,
    "endpoint": str,
    "company_name": str,
    "data": dict,
    "special_values_detected": [
      {"field": str, "value": int, "meaning": str}
    ],
    "metadata": {
      "source": "gurufocus",
      "timestamp": str,
      "period": str,
      "api_version": "v3"
    }
  },
  "error": str | null
}
```

### Special Values

| Value | Meaning |
|-------|---------|
| 9999 | Data Not Available |
| 10000 | No Debt / Negative Equity |
| 0 | At Loss (valid but indicates loss) |

---

## 4. Implementation Requirements

### API Configuration

**Base URL:** `https://api.gurufocus.com/public/user/{API_KEY}/stock/{ticker}/`  
**Authentication:** API key from `GURUFOCUS_API_KEY` environment variable  
**Rate Limiting:** 1.5 second minimum interval between requests  
**Timeout:** 30 seconds

### Field Mappings

**Owner Earnings Components:**
- Net Income: `annual["Net Income"][0]`
- D&A: `annual["Depreciation & Amortization"][0]`
- CapEx: `annual["Capital Expenditure"][0]`

**ROIC Components:**
- Operating Income: `annual["Operating Income"][0]`
- Total Assets: `annual["Total Assets"][0]`
- Cash: `annual["Cash and Cash Equivalents"][0]`

---

## 5. Error Handling

### Error Types

1. **Invalid Ticker** → Do not retry
2. **Rate Limit (429)** → Exponential backoff (2s, 4s, 8s), max 3 retries
3. **Network Timeout** → Retry up to 3 times
4. **Special Values (9999, 10000)** → Flag in response, continue with partial data

---

## 6. Dependencies

```python
requests==2.31.0
python-dotenv==1.0.0
```

Environment variable: `GURUFOCUS_API_KEY`

---

## 7. Use Cases for Agent

### Initial Screening
```python
result = gurufocus_tool.execute(ticker="AAPL", endpoint="summary")
# Check ROIC and debt ratios for quick assessment
```

### Financial Analysis
```python
result = gurufocus_tool.execute(ticker="AAPL", endpoint="financials")
# Get 10 years of financial statements for Owner Earnings
```

---

## 8. Testing Requirements

- Input validation (valid/invalid tickers)
- All four endpoints
- Special value detection
- Rate limiting enforcement
- Error handling (timeout, rate limit, invalid ticker)

---

## 9. Python Implementation Example

```python
import os
import time
import requests
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class GuruFocusTool:
    @property
    def name(self) -> str:
        return "gurufocus_tool"
    
    @property
    def description(self) -> str:
        return "Retrieves financial data from GuruFocus Premium API"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "pattern": "^[A-Z]{1,5}$"},
                "endpoint": {"type": "string", "enum": ["summary", "financials", "keyratios", "valuation"]},
                "period": {"type": "string", "enum": ["annual", "quarterly"], "default": "annual"}
            },
            "required": ["ticker", "endpoint"]
        }
    
    def __init__(self):
        self.api_key = os.getenv("GURUFOCUS_API_KEY")
        if not self.api_key:
            raise ValueError("GURUFOCUS_API_KEY not set")
        
        self.base_url = "https://api.gurufocus.com/public/user"
        self.last_request_time = 0
        self.min_interval = 1.5
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        })
    
    def execute(self, ticker: str, endpoint: str, period: str = "annual") -> Dict[str, Any]:
        # Validate inputs
        if not ticker or not ticker.isupper():
            return {"success": False, "data": None, "error": "Ticker must be uppercase"}
        
        if endpoint not in ["summary", "financials", "keyratios", "valuation"]:
            return {"success": False, "data": None, "error": f"Invalid endpoint: {endpoint}"}
        
        # Enforce rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
        
        # Construct URL
        url = f"{self.base_url}/{self.api_key}/stock/{ticker}/{endpoint}"
        
        # Make request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 404:
                    return {"success": False, "data": None, "error": f"Ticker '{ticker}' not found"}
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** (attempt + 1))
                        continue
                    return {"success": False, "data": None, "error": "Rate limit exceeded"}
                
                response.raise_for_status()
                data = response.json()
                
                # Detect special values
                special_values = self._detect_special_values(data)
                
                return {
                    "success": True,
                    "data": {
                        "ticker": ticker.upper(),
                        "endpoint": endpoint,
                        "company_name": self._extract_company_name(data, endpoint),
                        "data": data,
                        "special_values_detected": special_values,
                        "metadata": {
                            "source": "gurufocus",
                            "timestamp": datetime.now().isoformat(),
                            "period": period,
                            "api_version": "v3"
                        }
                    },
                    "error": None
                }
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "data": None, "error": "Request timeout"}
            except Exception as e:
                return {"success": False, "data": None, "error": str(e)}
        
        return {"success": False, "data": None, "error": "Failed after retries"}
    
    def _extract_company_name(self, data: dict, endpoint: str) -> str:
        try:
            if endpoint == "summary" and "general" in data:
                return data["general"].get("name", "Unknown")
            return "Unknown"
        except:
            return "Unknown"
    
    def _detect_special_values(self, data: dict) -> list:
        special_values = []
        
        def scan(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, (int, float)):
                        if value == 9999:
                            special_values.append({"field": new_path, "value": 9999, "meaning": "Data not available"})
                        elif value == 10000:
                            special_values.append({"field": new_path, "value": 10000, "meaning": "No debt or negative equity"})
                    else:
                        scan(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan(item, f"{path}[{i}]")
        
        scan(data)
        return special_values


# Example usage
if __name__ == "__main__":
    tool = GuruFocusTool()
    result = tool.execute(ticker="AAPL", endpoint="summary")
    if result["success"]:
        print(f"ROIC: {result['data']['data']['profitability']['roic']}")
```

---

## 10. Reference Documentation

**API Documentation:** `docs/api_references/gurufocus_api.md`

**Related Tools:**
- `calculator_tool_spec.md` - For Owner Earnings and ROIC calculations
- `sec_filing_tool_spec.md` - Alternative data source

**Buffett Principles:** `docs/BUFFETT_PRINCIPLES.md`

---

**Status:** Ready for Sprint 3 implementation

**File:** `docs/tool_specs/gurufocus_tool_spec.md`
