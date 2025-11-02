# Brave Search API Documentation

## Overview

Brave Search API provides access to Brave's independent search index of over 30 billion pages. It's designed for AI applications, RAG (Retrieval-Augmented Generation) pipelines, and building search-powered products. The API is particularly well-suited for grounding AI responses with real-time web data.

**Base URL:** `https://api.search.brave.com/res/v1/`

**Authentication:** API key via `X-Subscription-Token` header

**Index Size:** 30+ billion pages

**Update Frequency:** 100+ million page updates daily

**Cost:** Free tier available (2,000 calls/month), paid plans start at $0.50/month

---

## Key Features for Investment Agent

1. **Real-time Data:** Fresh results for news, earnings announcements, management changes
2. **High Quality:** Spam-filtered results with quality ranking
3. **Fast:** 95% of requests return in <1 second
4. **RAG-Optimized:** Up to 5 contextual snippets per result
5. **Structured Data:** Rich results for stock prices, company info
6. **No Ads:** Clean results without sponsored content

---

## Authentication

**Header:** `X-Subscription-Token`

**Example Request:**
```bash
curl -X GET "https://api.search.brave.com/res/v1/web/search?q=Apple+Inc+earnings" \
  -H "Accept: application/json" \
  -H "Accept-Encoding: gzip" \
  -H "X-Subscription-Token: YOUR_API_KEY"
```

**Python Example:**
```python
import requests

API_KEY = "your_brave_api_key"

headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'X-Subscription-Token': API_KEY
}

response = requests.get(
    'https://api.search.brave.com/res/v1/web/search',
    params={'q': 'Warren Buffett portfolio changes'},
    headers=headers
)

results = response.json()
```

---

## Rate Limits & Pricing

### Free Tier
- **Calls:** 2,000 per month
- **Rate Limit:** Reasonable usage
- **Features:** Web search, basic results
- **Use Case:** Testing and development

### Paid Plans

| Plan | Monthly Cost | Calls Included | Extra Cost |
|------|-------------|----------------|------------|
| **AI Starter** | $5 | 5,000 | $3 per 1K |
| **Pro** | $15 | 25,000 | $2 per 1K |
| **Pro AI** | $25 | 50,000 | $1.50 per 1K |
| **Enterprise** | Custom | Custom | Custom |

**Rate Limit Handling:**
- Standard rate limits apply per plan
- Response headers indicate remaining quota
- Exceeded limits return 429 status code

**Best for basīrah:**
- Development: Free tier
- Production: Pro AI ($25/month, 50K calls)

---

## Web Search Endpoint

**Endpoint:** `/web/search`

**Full URL:** `https://api.search.brave.com/res/v1/web/search`

**Method:** GET

**Description:** Primary search endpoint for web results. Returns titles, URLs, descriptions, and contextual snippets optimized for AI/RAG applications.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query (URL encoded) |
| `count` | integer | No | Number of results (default: 10, max: 20) |
| `offset` | integer | No | Pagination offset (default: 0, max: 9) |
| `country` | string | No | Country code for localized results (e.g., 'US') |
| `search_lang` | string | No | Language code (e.g., 'en') |
| `safesearch` | string | No | Filter level: 'off', 'moderate', 'strict' |
| `freshness` | string | No | Time filter: 'pd' (past day), 'pw' (past week), 'pm' (past month), 'py' (past year) |
| `text_decorations` | boolean | No | Include text highlights in results (default: true) |
| `spellcheck` | boolean | No | Include spell check suggestions (default: true) |
| `result_filter` | string | No | Filter results: 'web', 'news', 'videos' |

### Request Example

```python
import requests

API_KEY = "your_api_key"

params = {
    'q': 'Apple Inc management changes 2024',
    'count': 10,
    'freshness': 'pm',  # Past month
    'search_lang': 'en'
}

headers = {
    'X-Subscription-Token': API_KEY,
    'Accept': 'application/json'
}

response = requests.get(
    'https://api.search.brave.com/res/v1/web/search',
    params=params,
    headers=headers
)

data = response.json()
```

### Response Structure

```json
{
  "type": "search",
  "query": {
    "original": "Apple Inc management changes 2024",
    "show_strict_warning": false,
    "is_navigational": false,
    "is_news_breaking": false,
    "spellcheck_off": false,
    "country": "US",
    "bad_results": false,
    "should_fallback": false,
    "postal_code": "",
    "city": "",
    "header_country": "",
    "more_results_available": true,
    "state": ""
  },
  "mixed": {
    "type": "mixed",
    "main": [
      {
        "type": "web",
        "index": 0,
        "all": true
      }
    ],
    "top": [],
    "side": []
  },
  "web": {
    "type": "search",
    "results": [
      {
        "title": "Apple's Leadership Changes: New CFO Appointed in 2024",
        "url": "https://www.apple.com/newsroom/2024/01/apple-announces-new-cfo",
        "is_source_local": false,
        "is_source_both": false,
        "description": "Apple Inc. announced significant leadership changes today, appointing John Smith as Chief Financial Officer effective immediately. This marks a major transition in the company's financial leadership...",
        "language": "en",
        "family_friendly": true,
        "profile": {
          "name": "Apple Newsroom",
          "long_name": "apple.com",
          "url": "https://www.apple.com/newsroom",
          "img": "https://imgs.search.brave.com/..."
        },
        "extra_snippets": [
          "The new CFO brings extensive experience from his previous role at Microsoft, where he oversaw a $200 billion portfolio.",
          "Apple's CEO Tim Cook expressed confidence in the new appointment, citing Smith's track record of financial discipline and strategic growth.",
          "The leadership change comes as Apple focuses on expanding its services division and exploring new markets in AI and AR."
        ],
        "meta_url": {
          "scheme": "https",
          "netloc": "www.apple.com",
          "hostname": "www.apple.com",
          "favicon": "https://imgs.search.brave.com/...",
          "path": "› newsroom › 2024 › 01 › apple-announces-new-cfo"
        },
        "published": "2024-01-15T09:30:00Z",
        "thumbnail": {
          "src": "https://www.apple.com/...",
          "original": "https://www.apple.com/...",
          "logo": false
        }
      },
      {
        "title": "Analysis: What Apple's Management Shake-Up Means for Investors",
        "url": "https://www.reuters.com/business/apple-management-changes-2024",
        "description": "Financial analysts weigh in on Apple's recent leadership changes and what they signal for the company's strategic direction...",
        "extra_snippets": [
          "Wall Street reacted positively to the announcement, with AAPL shares rising 2.3% in after-hours trading.",
          "Analysts note that the new CFO's background in cloud services aligns with Apple's strategic priorities."
        ]
      }
    ]
  },
  "news": {
    "type": "news",
    "results": [
      {
        "meta_url": {
          "scheme": "https",
          "netloc": "www.bloomberg.com",
          "hostname": "www.bloomberg.com",
          "favicon": "...",
          "path": "..."
        },
        "source": "Bloomberg",
        "title": "Apple Names New CFO as Part of Executive Reshuffle",
        "url": "https://www.bloomberg.com/news/articles/2024-apple-cfo",
        "description": "Apple Inc. announced a significant change to its executive team...",
        "age": "2 hours ago",
        "breaking": false,
        "thumbnail": {
          "src": "..."
        }
      }
    ]
  }
}
```

### Key Response Fields

**Web Results (`web.results[]`):**
- `title` - Page title
- `url` - URL of the result
- `description` - Main snippet describing the page
- `extra_snippets[]` - Additional contextual snippets (up to 5)
- `published` - Publication date (ISO 8601 format)
- `language` - Content language
- `profile.name` - Source name
- `thumbnail.src` - Image thumbnail if available

**News Results (`news.results[]`):**
- `source` - News publisher name
- `title` - Article title
- `url` - Article URL
- `age` - How recent ("2 hours ago", "1 day ago")
- `breaking` - Boolean indicating breaking news

**Query Metadata (`query`):**
- `more_results_available` - Whether more pages exist
- `is_news_breaking` - Breaking news detected
- `country` - Detected/specified country

---

## Use Cases for Investment Agent

### 1. Recent Company News
```python
def search_company_news(company_name: str, api_key: str) -> list:
    """Search for recent news about a company"""
    params = {
        'q': f'{company_name} news',
        'count': 10,
        'freshness': 'pw',  # Past week
        'result_filter': 'news'
    }
    
    headers = {'X-Subscription-Token': api_key}
    response = requests.get(
        'https://api.search.brave.com/res/v1/web/search',
        params=params,
        headers=headers
    )
    
    results = response.json()
    return results.get('news', {}).get('results', [])
```

### 2. Management Quality Research
```python
def research_management(company_name: str, ceo_name: str, api_key: str) -> dict:
    """Research company management and CEO"""
    queries = [
        f'{ceo_name} CEO {company_name} track record',
        f'{company_name} management compensation scandal',
        f'{ceo_name} previous companies leadership',
        f'{company_name} executive turnover'
    ]
    
    results = {}
    headers = {'X-Subscription-Token': api_key}
    
    for query in queries:
        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            params={'q': query, 'count': 5},
            headers=headers
        )
        results[query] = response.json()
    
    return results
```

### 3. Competitive Analysis
```python
def analyze_competitors(company_name: str, industry: str, api_key: str) -> dict:
    """Research industry and competitors"""
    query = f'{company_name} competitors {industry} market share'
    
    params = {
        'q': query,
        'count': 15,
        'search_lang': 'en'
    }
    
    headers = {'X-Subscription-Token': api_key}
    response = requests.get(
        'https://api.search.brave.com/res/v1/web/search',
        params=params,
        headers=headers
    )
    
    return response.json()
```

### 4. Economic Moat Research
```python
def research_economic_moat(company_name: str, api_key: str) -> dict:
    """Research company's competitive advantages"""
    queries = [
        f'{company_name} competitive advantage brand strength',
        f'{company_name} network effects',
        f'{company_name} switching costs customers',
        f'{company_name} cost advantages economies of scale',
        f'{company_name} patents intellectual property'
    ]
    
    moat_research = {}
    headers = {'X-Subscription-Token': api_key}
    
    for query in queries:
        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            params={'q': query, 'count': 5},
            headers=headers
        )
        moat_research[query] = response.json()
        time.sleep(0.5)  # Rate limiting courtesy
    
    return moat_research
```

### 5. Red Flag Detection
```python
def search_red_flags(company_name: str, api_key: str) -> dict:
    """Search for potential red flags"""
    red_flag_queries = [
        f'{company_name} lawsuit legal troubles',
        f'{company_name} accounting irregularities restatement',
        f'{company_name} SEC investigation',
        f'{company_name} insider trading scandal',
        f'{company_name} product recall safety issues',
        f'{company_name} layoffs downsizing'
    ]
    
    red_flags = {}
    headers = {'X-Subscription-Token': api_key}
    
    for query in red_flag_queries:
        params = {
            'q': query,
            'count': 5,
            'freshness': 'py'  # Past year
        }
        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            params=params,
            headers=headers
        )
        red_flags[query] = response.json()
        time.sleep(0.5)
    
    return red_flags
```

---

## Response Headers

**Rate Limit Information:**
```
X-RateLimit-Limit: 50000
X-RateLimit-Remaining: 49950
X-RateLimit-Reset: 1640995200
```

**Monitoring Usage:**
```python
def check_rate_limits(response: requests.Response) -> dict:
    """Extract rate limit info from response headers"""
    return {
        'limit': response.headers.get('X-RateLimit-Limit'),
        'remaining': response.headers.get('X-RateLimit-Remaining'),
        'reset': response.headers.get('X-RateLimit-Reset'),
        'reset_datetime': datetime.fromtimestamp(
            int(response.headers.get('X-RateLimit-Reset', 0))
        )
    }
```

---

## Advanced Features

### Goggles (Result Re-ranking)

Brave Search Goggles allow custom ranking rules to boost or demote specific domains.

**Use Case:** Boost authoritative financial sources, demote clickbait

```python
# Apply custom ranking rules
params = {
    'q': 'Apple Inc financial analysis',
    'goggles_id': 'custom_financial_sources_boost'
}
```

### Snippets for RAG

Brave optimizes snippets for AI consumption:
- Up to 5 snippets per result
- Contextually relevant to query
- Suitable for LLM prompts

**Example RAG Prompt:**
```python
def create_rag_prompt(query: str, search_results: dict) -> str:
    """Create RAG prompt from search results"""
    snippets = []
    
    for result in search_results['web']['results'][:5]:
        title = result['title']
        url = result['url']
        description = result['description']
        
        # Collect extra snippets
        extra = result.get('extra_snippets', [])
        
        snippet_text = f"Source: {title} ({url})\n{description}\n"
        if extra:
            snippet_text += "\n".join(extra)
        
        snippets.append(snippet_text)
    
    context = "\n\n---\n\n".join(snippets)
    
    prompt = f"""Based on the following web search results, answer the question: "{query}"

Search Results:
{context}

Answer:"""
    
    return prompt
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process results |
| 400 | Bad Request | Check query parameters |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check subscription status |
| 429 | Rate Limit Exceeded | Wait and retry |
| 500 | Server Error | Retry with backoff |

### Error Response Example

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "You have exceeded your rate limit. Please try again later.",
    "retry_after": 3600
  }
}
```

### Retry Logic

```python
import time

def search_with_retry(query: str, api_key: str, max_retries: int = 3) -> dict:
    """Search with exponential backoff retry logic"""
    headers = {'X-Subscription-Token': api_key}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                'https://api.search.brave.com/res/v1/web/search',
                params={'q': query},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            
            elif response.status_code >= 500:
                # Server error - exponential backoff
                wait = (2 ** attempt) * 2
                print(f"Server error. Retrying in {wait} seconds...")
                time.sleep(wait)
                continue
            
            else:
                response.raise_for_status()
        
        except requests.exceptions.Timeout:
            wait = (2 ** attempt) * 2
            print(f"Timeout. Retrying in {wait} seconds...")
            time.sleep(wait)
            continue
        
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
    
    return None
```

---

## Comprehensive Python Implementation

```python
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime

class BraveSearchAPI:
    """
    Brave Search API client for basīrah investment agent
    Handles web search for company research, news, and competitive analysis
    """
    
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize Brave Search client
        
        Args:
            api_key: Brave Search API key
        """
        self.api_key = api_key
        self.headers = {
            'X-Subscription-Token': api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search(
        self,
        query: str,
        count: int = 10,
        freshness: Optional[str] = None,
        country: str = 'US',
        search_lang: str = 'en',
        result_filter: Optional[str] = None
    ) -> Dict:
        """
        Perform web search
        
        Args:
            query: Search query string
            count: Number of results (1-20)
            freshness: Time filter ('pd', 'pw', 'pm', 'py')
            country: Country code
            search_lang: Language code
            result_filter: Filter type ('web', 'news', 'videos')
        
        Returns:
            Search results dictionary
        """
        params = {
            'q': query,
            'count': min(count, 20),
            'country': country,
            'search_lang': search_lang
        }
        
        if freshness:
            params['freshness'] = freshness
        
        if result_filter:
            params['result_filter'] = result_filter
        
        try:
            response = self.session.get(
                f'{self.BASE_URL}/web/search',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Search failed: {e}")
            return {}
    
    def search_company_news(
        self,
        company_name: str,
        days_back: str = 'pw'
    ) -> List[Dict]:
        """
        Search for recent company news
        
        Args:
            company_name: Company name or ticker
            days_back: Freshness filter ('pd', 'pw', 'pm', 'py')
        
        Returns:
            List of news articles
        """
        results = self.search(
            query=f'{company_name} news',
            count=15,
            freshness=days_back,
            result_filter='news'
        )
        
        return results.get('news', {}).get('results', [])
    
    def research_management(
        self,
        company_name: str,
        ceo_name: Optional[str] = None
    ) -> Dict:
        """
        Research company management quality
        
        Args:
            company_name: Company name
            ceo_name: CEO name (optional)
        
        Returns:
            Dictionary of search results by query
        """
        queries = [
            f'{company_name} management team leadership',
            f'{company_name} CEO track record',
            f'{company_name} executive compensation',
            f'{company_name} management changes turnover'
        ]
        
        if ceo_name:
            queries.extend([
                f'{ceo_name} CEO background experience',
                f'{ceo_name} previous companies'
            ])
        
        results = {}
        for query in queries:
            results[query] = self.search(query, count=5)
            time.sleep(0.5)  # Courtesy rate limiting
        
        return results
    
    def find_economic_moat_indicators(self, company_name: str) -> Dict:
        """
        Search for signs of economic moat
        
        Args:
            company_name: Company name
        
        Returns:
            Search results about competitive advantages
        """
        moat_queries = {
            'brand_power': f'{company_name} brand recognition customer loyalty',
            'network_effects': f'{company_name} network effects platform users',
            'switching_costs': f'{company_name} customer switching costs',
            'cost_advantages': f'{company_name} economies of scale cost leadership',
            'intangibles': f'{company_name} patents intellectual property'
        }
        
        results = {}
        for category, query in moat_queries.items():
            results[category] = self.search(query, count=5)
            time.sleep(0.5)
        
        return results
    
    def search_red_flags(self, company_name: str) -> Dict:
        """
        Search for potential investment red flags
        
        Args:
            company_name: Company name
        
        Returns:
            Dictionary of search results for various red flags
        """
        red_flag_queries = {
            'legal_issues': f'{company_name} lawsuit litigation legal trouble',
            'accounting': f'{company_name} accounting irregularities restatement',
            'regulatory': f'{company_name} SEC investigation fine penalty',
            'insider_activity': f'{company_name} insider selling stock sales',
            'product_issues': f'{company_name} product recall safety issue',
            'financial_distress': f'{company_name} layoffs downsizing restructuring'
        }
        
        results = {}
        for category, query in red_flag_queries.items():
            results[category] = self.search(
                query,
                count=5,
                freshness='py'  # Past year
            )
            time.sleep(0.5)
        
        return results
    
    def research_competitive_landscape(
        self,
        company_name: str,
        industry: str
    ) -> Dict:
        """
        Research industry competition and market position
        
        Args:
            company_name: Company name
            industry: Industry/sector
        
        Returns:
            Search results about competitive landscape
        """
        queries = [
            f'{company_name} market share {industry}',
            f'{company_name} competitors {industry}',
            f'{industry} industry trends 2024',
            f'{company_name} competitive advantages vs competitors'
        ]
        
        results = {}
        for query in queries:
            results[query] = self.search(query, count=10)
            time.sleep(0.5)
        
        return results
    
    def extract_snippets_for_llm(self, search_results: Dict) -> List[str]:
        """
        Extract and format snippets for LLM context
        
        Args:
            search_results: Raw search results from API
        
        Returns:
            List of formatted snippet strings
        """
        snippets = []
        
        web_results = search_results.get('web', {}).get('results', [])
        
        for result in web_results[:5]:  # Top 5 results
            title = result.get('title', '')
            url = result.get('url', '')
            description = result.get('description', '')
            extra = result.get('extra_snippets', [])
            
            snippet = f"**{title}**\nSource: {url}\n\n{description}"
            
            if extra:
                snippet += "\n\nAdditional context:\n" + "\n".join(f"- {s}" for s in extra)
            
            snippets.append(snippet)
        
        return snippets
    
    def get_rate_limit_status(self, response: requests.Response) -> Dict:
        """
        Extract rate limit information from response headers
        
        Args:
            response: requests Response object
        
        Returns:
            Dictionary with rate limit info
        """
        return {
            'limit': response.headers.get('X-RateLimit-Limit'),
            'remaining': response.headers.get('X-RateLimit-Remaining'),
            'reset': response.headers.get('X-RateLimit-Reset'),
            'reset_time': datetime.fromtimestamp(
                int(response.headers.get('X-RateLimit-Reset', 0))
            ) if response.headers.get('X-RateLimit-Reset') else None
        }

# Example Usage
if __name__ == "__main__":
    # Initialize client
    api = BraveSearchAPI("your_api_key")
    
    # Search company news
    news = api.search_company_news("Apple Inc", days_back='pw')
    print(f"Found {len(news)} recent news articles")
    
    # Research management
    mgmt_research = api.research_management("Apple Inc", "Tim Cook")
    print(f"Management research queries: {len(mgmt_research)}")
    
    # Find economic moat indicators
    moat = api.find_economic_moat_indicators("Apple Inc")
    print(f"Moat research categories: {list(moat.keys())}")
    
    # Search for red flags
    red_flags = api.search_red_flags("Apple Inc")
    print(f"Red flag categories checked: {list(red_flags.keys())}")
```

---

## Best Practices

1. **Cache Results:** Save API responses to avoid redundant calls
2. **Rate Limit Awareness:** Monitor headers and stay under limits
3. **Meaningful Queries:** Craft specific, targeted search queries
4. **Result Filtering:** Use appropriate filters (news, time ranges)
5. **Snippet Extraction:** Leverage `extra_snippets` for LLM context
6. **Error Handling:** Implement retry logic with exponential backoff
7. **Cost Monitoring:** Track API usage against budget

---

## Testing Checklist

✅ Test basic web search functionality  
✅ Test news filtering  
✅ Test freshness filters (pd, pw, pm, py)  
✅ Verify rate limit headers  
✅ Test error handling (401, 429, 500)  
✅ Validate result count parameter  
✅ Test snippet extraction for LLM context  
✅ Verify pagination with offset parameter  

---

## Additional Resources

- **Official API Documentation:** https://brave.com/search/api/
- **API Dashboard:** https://api.search.brave.com/app/dashboard
- **Pricing Calculator:** https://brave.com/search/api/#pricing
- **Community SDKs:** Various community implementations available

---

**Last Updated:** October 28, 2025  
**API Version:** v1  
**Free Tier:** 2,000 calls/month  
**Recommended Plan:** Pro AI ($25/month, 50,000 calls)
