# Web Search Tool Specification

## Tool Name: `web_search_tool`

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Status:** Sprint 2 - Ready for Implementation

---

## 1. Purpose & Use Cases

### Purpose

The Web Search Tool provides web search capabilities using the Brave Search API, enabling the basīrah agent to gather current information about companies, management teams, competitive dynamics, and market conditions that may not be available in regulatory filings or financial databases.

### Primary Use Cases for Agent

1. **Business Understanding:**
   - Search for recent business model changes or pivots
   - Investigate product launches and market reception
   - Understand competitive landscape and market position

2. **Management Evaluation:**
   - Research CEO/executive backgrounds and track records
   - Search for management controversies or red flags
   - Find interviews, statements, and public communications

3. **Moat Assessment:**
   - Investigate brand strength and customer loyalty
   - Research switching costs and network effects
   - Analyze competitive advantages and pricing power

4. **Risk Assessment:**
   - Search for litigation, regulatory issues, or controversies
   - Find product recalls or quality issues
   - Investigate labor disputes or operational problems

5. **Industry Analysis:**
   - Research industry trends and disruption threats
   - Understand competitive dynamics
   - Identify emerging competitors or substitutes

### When Agent Should Use This Tool

```
PHASE 2 (Business Understanding):
  → web_search_tool(query="business model", company="Apple Inc", search_type="general")
  → web_search_tool(query="recent product launches", company="Apple Inc", search_type="news")

PHASE 3 (Moat Assessment):
  → web_search_tool(query="brand loyalty customer satisfaction", company="Apple Inc")
  → web_search_tool(query="competitive advantages vs competitors", company="Apple Inc")

PHASE 4 (Management Evaluation):
  → web_search_tool(query="Tim Cook leadership track record", search_type="general")
  → web_search_tool(query="executive compensation controversy", company="Apple Inc", search_type="news")

PHASE 7 (Risk Assessment):
  → web_search_tool(query="litigation OR regulatory issues", company="Apple Inc", search_type="news")
  → web_search_tool(query="product recalls OR quality problems", company="Apple Inc", search_type="recent")
```

---

## 2. Input Parameters

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query string",
      "minLength": 1,
      "maxLength": 400,
      "examples": [
        "recent news about management changes",
        "competitive advantages brand loyalty",
        "Tim Cook leadership track record"
      ]
    },
    "company": {
      "type": "string",
      "description": "Company name or ticker for context filtering (optional)",
      "examples": ["Apple Inc", "AAPL", "Microsoft Corporation"]
    },
    "count": {
      "type": "integer",
      "description": "Number of results to return",
      "default": 10,
      "minimum": 1,
      "maximum": 20
    },
    "search_type": {
      "type": "string",
      "enum": ["general", "news", "recent"],
      "default": "general",
      "description": "Type of search to perform"
    },
    "freshness": {
      "type": "string",
      "enum": ["day", "week", "month", "year"],
      "description": "Filter results by freshness (optional)"
    }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

### Parameter Details

#### `query` (required)
- **Type:** string
- **Length:** 1-400 characters
- **Description:** The search query
- **Best Practices:**
  - Use specific, targeted queries (3-10 words optimal)
  - Include relevant keywords for better results
  - Use OR for alternative terms: "litigation OR lawsuit"
  - Avoid overly broad queries
- **Examples:**
  - `"recent management changes"`
  - `"customer satisfaction brand loyalty"`
  - `"competitive advantages moat"`
  - `"Warren Buffett on company"`

#### `company` (optional)
- **Type:** string
- **Description:** Company name or ticker to add context
- **Usage:** Automatically added to query for relevance filtering
- **Examples:** `"Apple Inc"`, `"AAPL"`, `"Berkshire Hathaway"`
- **Note:** Tool will intelligently append company name to query

#### `count` (optional)
- **Type:** integer
- **Range:** 1-20
- **Default:** 10
- **Description:** Number of search results to return
- **Guidance:**
  - 5 results: Quick validation of a specific claim
  - 10 results: Standard research (default)
  - 20 results: Comprehensive investigation

#### `search_type` (optional)
- **Type:** string
- **Allowed Values:**
  - `"general"` - Standard web search (default)
  - `"news"` - News-focused search
  - `"recent"` - Recent content only (last 30 days)
- **Default:** `"general"`
- **Usage:**
  - `"general"`: Background research, evergreen content
  - `"news"`: Current events, announcements, press releases
  - `"recent"`: Latest developments, breaking news

#### `freshness` (optional)
- **Type:** string
- **Allowed Values:** `"day"`, `"week"`, `"month"`, `"year"`
- **Description:** Filter results by recency
- **Usage:** Overrides `search_type="recent"` with specific timeframe
- **Examples:**
  - `"day"`: Last 24 hours
  - `"week"`: Last 7 days
  - `"month"`: Last 30 days
  - `"year"`: Last 12 months

### Example Inputs

```python
# Example 1: General business research
{
    "query": "business model revenue sources",
    "company": "Apple Inc",
    "count": 10,
    "search_type": "general"
}

# Example 2: Recent news search
{
    "query": "management changes executive appointments",
    "company": "Microsoft",
    "count": 5,
    "search_type": "news"
}

# Example 3: Controversy investigation
{
    "query": "litigation OR lawsuit OR regulatory",
    "company": "Meta",
    "count": 15,
    "search_type": "recent"
}

# Example 4: CEO background research
{
    "query": "Satya Nadella leadership track record achievements",
    "count": 10,
    "search_type": "general"
}

# Example 5: Fresh competitive analysis
{
    "query": "competitive landscape market share",
    "company": "Tesla",
    "count": 10,
    "freshness": "month"
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
      "description": "Whether search completed successfully"
    },
    "data": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Actual query sent to Brave Search API"
        },
        "results": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": {
                "type": "string",
                "description": "Result title"
              },
              "url": {
                "type": "string",
                "format": "uri",
                "description": "Result URL"
              },
              "description": {
                "type": "string",
                "description": "Result description/snippet"
              },
              "age": {
                "type": "string",
                "description": "Relative age (e.g., '2 days ago')"
              },
              "published_date": {
                "type": ["string", "null"],
                "format": "date",
                "description": "Publication date if available"
              },
              "source": {
                "type": "string",
                "description": "Domain name of source"
              },
              "extra_snippets": {
                "type": "array",
                "items": {"type": "string"},
                "description": "RAG-optimized additional snippets"
              }
            }
          }
        },
        "total_results": {
          "type": "integer",
          "description": "Total number of results returned"
        },
        "metadata": {
          "type": "object",
          "properties": {
            "source": {
              "type": "string",
              "const": "brave_search"
            },
            "search_type": {
              "type": "string",
              "description": "Type of search performed"
            },
            "timestamp": {
              "type": "string",
              "format": "date-time"
            },
            "api_latency_ms": {
              "type": "integer",
              "description": "API response time in milliseconds"
            }
          }
        }
      }
    },
    "error": {
      "type": ["string", "null"],
      "description": "Error message if search failed"
    }
  }
}
```

### Example Output

```json
{
  "success": true,
  "data": {
    "query": "management changes Apple Inc",
    "results": [
      {
        "title": "Apple Announces Leadership Changes in Services Division - Apple Newsroom",
        "url": "https://www.apple.com/newsroom/2023/09/leadership-changes",
        "description": "Apple today announced organizational changes to its Services division, with Eddy Cue continuing to lead...",
        "age": "3 months ago",
        "published_date": "2023-09-15",
        "source": "apple.com",
        "extra_snippets": [
          "The changes reflect Apple's continued investment in services growth",
          "Services revenue reached $21.2 billion in Q3 2023",
          "New leadership structure aims to accelerate innovation"
        ]
      },
      {
        "title": "Analysis: What Apple's Executive Reshuffling Means for Investors",
        "url": "https://www.bloomberg.com/analysis/apple-executive-changes",
        "description": "Apple's recent management changes signal a strategic shift toward...",
        "age": "2 months ago",
        "published_date": "2023-10-12",
        "source": "bloomberg.com",
        "extra_snippets": [
          "Investors should watch for impact on services margins",
          "Historical pattern shows leadership changes precede new product launches"
        ]
      }
    ],
    "total_results": 2,
    "metadata": {
      "source": "brave_search",
      "search_type": "news",
      "timestamp": "2025-10-29T12:00:00Z",
      "api_latency_ms": 342
    }
  },
  "error": null
}
```

### Empty Results Output

```json
{
  "success": true,
  "data": {
    "query": "very obscure specific query that returns nothing",
    "results": [],
    "total_results": 0,
    "metadata": {
      "source": "brave_search",
      "search_type": "general",
      "timestamp": "2025-10-29T12:00:00Z",
      "api_latency_ms": 156
    }
  },
  "error": null
}
```

### Error Output

```json
{
  "success": false,
  "data": null,
  "error": "Rate limit exceeded (2000 searches/month). Resets on 2025-11-01."
}
```

---

## 4. Implementation Requirements

### API Configuration

**Base URL:** `https://api.search.brave.com/res/v1/web/search`  
**Authentication:** `X-Subscription-Token` header  
**API Key:** From `BRAVE_SEARCH_API_KEY` environment variable  
**Rate Limiting:** 
- Free tier: 2,000 searches/month
- Basic tier: 15,000 searches/month
- Pro tier: 100,000 searches/month

**Request Parameters:**

```python
params = {
    "q": query,                    # Search query
    "count": count,                # Results count (default: 10)
    "offset": 0,                   # Pagination offset
    "extra_snippets": True,        # Enable RAG snippets (CRITICAL)
    "text_decorations": False,     # Disable HTML in snippets
    "search_lang": "en",           # English results
    "country": "US",               # Default to US (can be customized)
    "safesearch": "moderate",      # Content filtering
    "freshness": freshness         # Optional: "day", "week", "month", "year"
}
```

**Headers:**

```python
headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": api_key
}
```

### RAG-Optimized Snippets (CRITICAL)

Brave Search provides **extra snippets** specifically designed for RAG (Retrieval-Augmented Generation) systems. **Always request these:**

```python
params["extra_snippets"] = True
```

**What you get:**
- Up to 5 additional snippets per result
- Longer, more context-rich excerpts
- Better semantic relevance for AI consumption
- Improved answer quality for agent reasoning

**Example:**
```json
"extra_snippets": [
  "The company's economic moat is characterized by strong brand loyalty and ecosystem lock-in effects.",
  "Switching costs are high due to integration with existing Apple products and services.",
  "Customer satisfaction scores consistently rank above 95% in multiple surveys."
]
```

### Query Construction Strategy

**Basic Query Construction:**

```python
def construct_query(query: str, company: Optional[str] = None) -> str:
    """Construct effective search query"""
    
    # If company specified, add to query for context
    if company:
        # Smart addition - avoid duplication
        if company.lower() not in query.lower():
            query = f"{query} {company}"
    
    # Clean query
    query = query.strip()
    
    return query
```

**Query Optimization Tips:**

1. **Specific Keywords:** Use precise terms instead of generic ones
   - Good: "brand loyalty customer retention rate"
   - Bad: "customers like company"

2. **Boolean Operators:** Use OR for alternatives
   - "litigation OR lawsuit OR legal issues"
   - "CEO OR chief executive officer"

3. **Phrase Matching:** Use quotes for exact phrases (sparingly)
   - `"Warren Buffett investment philosophy"`

4. **Company Context:** Include company name for relevance
   - Automatically handled by `company` parameter

5. **Avoid Over-Specification:** Too many constraints = fewer results
   - Good: "management changes 2023"
   - Over-specified: "management changes executive appointments C-suite September 2023"

### Response Processing

**HTML Cleaning:**

```python
import re
from html import unescape

def clean_snippet(text: str) -> str:
    """Clean HTML and artifacts from snippets"""
    
    # Unescape HTML entities
    text = unescape(text)
    
    # Remove HTML tags (Brave should not return these with text_decorations=False)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text
```

**Date Parsing:**

```python
from datetime import datetime, timedelta

def parse_relative_date(age_str: str) -> Optional[str]:
    """Convert relative date to ISO date"""
    
    # Brave returns: "2 hours ago", "3 days ago", "1 week ago"
    
    match = re.match(r'(\d+)\s+(hour|day|week|month|year)s?\s+ago', age_str.lower())
    
    if not match:
        return None
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    now = datetime.now()
    
    if unit == 'hour':
        date = now - timedelta(hours=amount)
    elif unit == 'day':
        date = now - timedelta(days=amount)
    elif unit == 'week':
        date = now - timedelta(weeks=amount)
    elif unit == 'month':
        date = now - timedelta(days=amount*30)
    elif unit == 'year':
        date = now - timedelta(days=amount*365)
    else:
        return None
    
    return date.strftime('%Y-%m-%d')
```

### Company Context Filtering

When `company` parameter is provided, the tool should:

1. **Add to Query:** Include company name in search
2. **Result Filtering:** Optionally filter results for relevance
3. **Snippet Enhancement:** Highlight company mentions

```python
def filter_by_relevance(results: List[Dict], company: str) -> List[Dict]:
    """Filter results by company relevance (optional)"""
    
    company_lower = company.lower()
    
    relevant_results = []
    for result in results:
        # Check if company mentioned in title or description
        text = f"{result['title']} {result['description']}".lower()
        
        if company_lower in text:
            relevant_results.append(result)
    
    return relevant_results if relevant_results else results  # Return all if none match
```

---

## 5. Error Handling

### Error Types and Responses

#### 1. Empty Query
```python
if not query or len(query.strip()) == 0:
    return {"success": False, "data": None, 
            "error": "Query cannot be empty"}
```

#### 2. Query Too Long
```python
if len(query) > 400:
    return {"success": False, "data": None,
            "error": "Query exceeds 400 character limit"}
```

#### 3. Invalid API Key
```python
# HTTP 401 Unauthorized
return {"success": False, "data": None,
        "error": "Invalid API key. Check BRAVE_SEARCH_API_KEY environment variable"}
```

#### 4. Rate Limit Exceeded
```python
# HTTP 429 Too Many Requests
return {"success": False, "data": None,
        "error": "Rate limit exceeded (2000 searches/month). Resets on 2025-11-01."}
```

#### 5. Network Timeout
```python
# Implement retry with exponential backoff
max_retries = 3
for attempt in range(max_retries):
    try:
        response = session.get(url, timeout=30)
        break
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
            continue
        return {"success": False, "data": None,
                "error": "Request timeout after 3 retries"}
```

#### 6. No Results Found
```python
# Return success with empty results (not an error)
return {
    "success": True,
    "data": {
        "query": query,
        "results": [],
        "total_results": 0,
        "metadata": {...}
    },
    "error": None
}
```

#### 7. API Error
```python
# HTTP 500 or other errors
return {"success": False, "data": None,
        "error": f"Brave Search API error: {response.status_code} - {response.text}"}
```

### Retry Strategy

```python
def execute_with_retry(self, query: str, max_retries: int = 3) -> Dict:
    """Execute search with exponential backoff retry"""
    
    for attempt in range(max_retries):
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            # Success
            if response.status_code == 200:
                return self._process_response(response.json())
            
            # Rate limit - don't retry (it won't help)
            if response.status_code == 429:
                return self._error("Rate limit exceeded")
            
            # Auth error - don't retry
            if response.status_code == 401:
                return self._error("Invalid API key")
            
            # Server error - retry
            if response.status_code >= 500:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return self._error(f"API error: {response.status_code}")
            
            # Other errors - don't retry
            return self._error(f"Unexpected error: {response.status_code}")
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return self._error("Request timeout")
        
        except Exception as e:
            return self._error(f"Unexpected exception: {str(e)}")
```

---

## 6. Dependencies

```python
requests==2.31.0
python-dotenv==1.0.0
```

**Environment Variable:** `BRAVE_SEARCH_API_KEY`

**Optional:**
```python
beautifulsoup4==4.12.0  # For additional HTML cleaning if needed
```

---

## 7. Testing Requirements

### Test Cases

#### Basic Functionality
- ✓ Simple query (company name)
- ✓ Complex query (multiple keywords)
- ✓ Query with company parameter
- ✓ Different search types (general, news, recent)
- ✓ Freshness filtering
- ✓ Various result counts (5, 10, 20)

#### Edge Cases
- ✓ Empty query (should error)
- ✓ Very long query (>400 chars, should error)
- ✓ Query with special characters
- ✓ No results found (should return empty list)
- ✓ Single result

#### Error Handling
- ✓ Invalid API key (401)
- ✓ Rate limit exceeded (429)
- ✓ Network timeout
- ✓ API server error (500)

#### Integration
- ✓ RAG snippets are returned
- ✓ HTML cleaned from results
- ✓ Dates parsed correctly
- ✓ Company filtering works

### Unit Test Example

```python
def test_basic_search():
    tool = WebSearchTool()
    result = tool.execute(
        query="Warren Buffett investment philosophy",
        count=5
    )
    
    assert result["success"] == True
    assert len(result["data"]["results"]) <= 5
    assert "title" in result["data"]["results"][0]
    assert "url" in result["data"]["results"][0]
    assert "extra_snippets" in result["data"]["results"][0]

def test_company_context():
    tool = WebSearchTool()
    result = tool.execute(
        query="management changes",
        company="Apple Inc",
        count=10
    )
    
    assert result["success"] == True
    assert "Apple Inc" in result["data"]["query"].lower() or \
           "apple" in result["data"]["query"].lower()

def test_empty_query():
    tool = WebSearchTool()
    result = tool.execute(query="")
    
    assert result["success"] == False
    assert "empty" in result["error"].lower()
```

---

## 8. Use Cases for Agent

### Phase 2: Business Understanding

```python
# Understand business model
result = web_search_tool.execute(
    query="business model revenue streams",
    company="Apple Inc",
    count=10,
    search_type="general"
)

# Recent business changes
result = web_search_tool.execute(
    query="business strategy changes pivots",
    company="Apple Inc",
    search_type="recent",
    freshness="month"
)
```

### Phase 3: Moat Assessment

```python
# Brand strength research
result = web_search_tool.execute(
    query="brand loyalty customer satisfaction NPS score",
    company="Apple Inc",
    count=10
)

# Competitive advantages
result = web_search_tool.execute(
    query="competitive advantages vs Samsung Google",
    company="Apple Inc",
    count=15
)

# Network effects
result = web_search_tool.execute(
    query="ecosystem lock-in network effects",
    company="Apple Inc",
    count=10
)
```

### Phase 4: Management Evaluation

```python
# CEO background
result = web_search_tool.execute(
    query="Tim Cook leadership track record achievements",
    count=10,
    search_type="general"
)

# Management controversies
result = web_search_tool.execute(
    query="executive compensation controversy OR scandal",
    company="Apple Inc",
    search_type="news",
    freshness="year"
)

# Shareholder communication quality
result = web_search_tool.execute(
    query="shareholder letter annual meeting transcript",
    company="Apple Inc",
    count=5
)
```

### Phase 7: Risk Assessment

```python
# Legal and regulatory issues
result = web_search_tool.execute(
    query="litigation OR lawsuit OR regulatory investigation",
    company="Apple Inc",
    search_type="news",
    freshness="year"
)

# Product issues
result = web_search_tool.execute(
    query="product recall OR quality issues OR defects",
    company="Apple Inc",
    search_type="recent"
)

# Labor and operational risks
result = web_search_tool.execute(
    query="labor dispute OR strike OR supply chain issues",
    company="Apple Inc",
    search_type="news",
    freshness="month"
)
```

---

## 9. Python Implementation Example

```python
import os
import time
import requests
import re
from html import unescape
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class WebSearchTool:
    """Web search tool using Brave Search API"""
    
    def __init__(self):
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY not set")
        
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': self.api_key
        })
    
    @property
    def name(self) -> str:
        return "web_search_tool"
    
    @property
    def description(self) -> str:
        return "Search the web for company information, news, and research using Brave Search"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 400,
                    "description": "Search query"
                },
                "company": {
                    "type": "string",
                    "description": "Company name/ticker for context (optional)"
                },
                "count": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Number of results"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["general", "news", "recent"],
                    "default": "general"
                },
                "freshness": {
                    "type": "string",
                    "enum": ["day", "week", "month", "year"]
                }
            },
            "required": ["query"]
        }
    
    def execute(
        self,
        query: str,
        company: Optional[str] = None,
        count: int = 10,
        search_type: str = "general",
        freshness: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute web search"""
        
        # Validate query
        if not query or len(query.strip()) == 0:
            return self._error("Query cannot be empty")
        
        if len(query) > 400:
            return self._error("Query exceeds 400 character limit")
        
        # Construct full query
        full_query = self._construct_query(query, company)
        
        # Build request parameters
        params = {
            "q": full_query,
            "count": min(count, 20),  # Cap at 20
            "offset": 0,
            "extra_snippets": True,    # CRITICAL for RAG
            "text_decorations": False,  # No HTML in snippets
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate"
        }
        
        # Add freshness if specified
        if freshness:
            params["freshness"] = freshness
        elif search_type == "recent":
            params["freshness"] = "month"  # Default for "recent"
        
        # Execute with retry
        return self._execute_with_retry(full_query, params)
    
    def _construct_query(self, query: str, company: Optional[str]) -> str:
        """Construct effective search query"""
        
        query = query.strip()
        
        # Add company for context if provided and not already in query
        if company and company.lower() not in query.lower():
            query = f"{query} {company}"
        
        return query
    
    def _execute_with_retry(
        self,
        query: str,
        params: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Execute search with retry logic"""
        
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.base_url,
                    params=params,
                    timeout=30
                )
                
                # Success
                if response.status_code == 200:
                    latency_ms = int((time.time() - start_time) * 1000)
                    return self._process_response(
                        response.json(),
                        query,
                        params.get("search_type", "general"),
                        latency_ms
                    )
                
                # Rate limit - don't retry
                if response.status_code == 429:
                    return self._error("Rate limit exceeded. Check your Brave Search API plan.")
                
                # Auth error - don't retry
                if response.status_code == 401:
                    return self._error("Invalid API key. Check BRAVE_SEARCH_API_KEY.")
                
                # Server error - retry
                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return self._error(f"Brave Search API error: {response.status_code}")
                
                # Other errors
                return self._error(f"Unexpected API error: {response.status_code}")
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return self._error("Request timeout after 3 retries")
            
            except Exception as e:
                return self._error(f"Unexpected exception: {str(e)}")
        
        return self._error("Failed after maximum retries")
    
    def _process_response(
        self,
        response_data: Dict,
        query: str,
        search_type: str,
        latency_ms: int
    ) -> Dict[str, Any]:
        """Process Brave Search API response"""
        
        # Extract web results
        web_results = response_data.get("web", {}).get("results", [])
        
        # Process each result
        processed_results = []
        for result in web_results:
            processed_result = {
                "title": self._clean_text(result.get("title", "")),
                "url": result.get("url", ""),
                "description": self._clean_text(result.get("description", "")),
                "age": result.get("age", ""),
                "published_date": self._parse_date(result.get("age", "")),
                "source": self._extract_domain(result.get("url", "")),
                "extra_snippets": [
                    self._clean_text(snippet)
                    for snippet in result.get("extra_snippets", [])
                ]
            }
            processed_results.append(processed_result)
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": processed_results,
                "total_results": len(processed_results),
                "metadata": {
                    "source": "brave_search",
                    "search_type": search_type,
                    "timestamp": datetime.now().isoformat(),
                    "api_latency_ms": latency_ms
                }
            },
            "error": None
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML and artifacts from text"""
        if not text:
            return ""
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove HTML tags (shouldn't be present, but just in case)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return ""
    
    def _parse_date(self, age_str: str) -> Optional[str]:
        """Convert relative date to ISO date"""
        if not age_str:
            return None
        
        # Parse "X hours/days/weeks/months/years ago"
        match = re.match(r'(\d+)\s+(hour|day|week|month|year)s?\s+ago', age_str.lower())
        
        if not match:
            return None
        
        amount = int(match.group(1))
        unit = match.group(2)
        
        now = datetime.now()
        
        delta_map = {
            'hour': timedelta(hours=amount),
            'day': timedelta(days=amount),
            'week': timedelta(weeks=amount),
            'month': timedelta(days=amount*30),
            'year': timedelta(days=amount*365)
        }
        
        if unit in delta_map:
            date = now - delta_map[unit]
            return date.strftime('%Y-%m-%d')
        
        return None
    
    def _error(self, message: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "data": None,
            "error": message
        }


# Example usage
if __name__ == "__main__":
    tool = WebSearchTool()
    
    # Example 1: General business research
    result = tool.execute(
        query="business model competitive advantages",
        company="Apple Inc",
        count=5,
        search_type="general"
    )
    
    if result["success"]:
        print(f"Found {result['data']['total_results']} results")
        for item in result["data"]["results"]:
            print(f"\n{item['title']}")
            print(f"  {item['url']}")
            print(f"  {item['age']} - {item['source']}")
            print(f"  Snippets: {len(item['extra_snippets'])}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Recent news search
    result = tool.execute(
        query="management changes",
        company="Microsoft",
        count=10,
        search_type="news",
        freshness="month"
    )
    
    if result["success"]:
        print(f"\nRecent news: {result['data']['total_results']} articles")
```

---

## 10. Reference Documentation

**API Documentation:** `docs/api_references/brave_search_api.md`

**Related Tools:**
- `sec_filing_tool_spec.md` - For regulatory information
- `gurufocus_tool_spec.md` - For financial data

**Buffett Principles:** `docs/BUFFETT_PRINCIPLES.md`
- Economic Moats (Section 2) - Use web search to validate moat characteristics
- Management Quality (Section 3) - Use web search for management research

---

## Conclusion

The Web Search Tool is the agent's window into current information, enabling investigation of business dynamics, management quality, and competitive positioning beyond what's available in financial statements and regulatory filings.

**Key Features:**
- Brave Search API integration with RAG-optimized snippets
- Flexible search types (general, news, recent)
- Freshness filtering for time-sensitive research
- Company context for relevance
- Robust error handling and retry logic
- Clean, structured output for agent consumption

**Critical for Agent Success:**
- Moat validation through customer sentiment and competitive analysis
- Management evaluation through public statements and controversies
- Risk assessment through news of legal, operational, or reputational issues
- Industry analysis for understanding competitive dynamics

**Status:** Ready for Sprint 3 implementation

---

**Document Complete**  
**File:** `docs/tool_specs/web_search_tool_spec.md`  
**Size:** ~30KB  
**Sections:** 10 comprehensive sections  
**Status:** PRODUCTION-READY
