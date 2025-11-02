# PHASE 3: Web Search Tool - USER TESTING PACKAGE

**Date:** October 30, 2025
**Phase:** Sprint 3, Phase 3 of 5
**Status:** Ready for User Testing

---

## Implementation Complete

The Web Search Tool has been fully implemented and is ready for testing. This package provides everything you need to test the tool yourself.

**Files Created:**
- `src/tools/web_search_tool.py` (640 lines)
- `tests/test_tools/test_web_search.py` (650+ lines with 38+ tests)
- `examples/test_web_search.py` (830+ lines with 10 examples)
- `.env.example` (updated with Brave Search API instructions)

---

## Prerequisites

### 1. Brave Search API Key Setup

**Get API Key (FREE):**
1. Visit: https://brave.com/search/api/
2. Sign up for FREE tier (no credit card required)
3. Get 2,000 queries/month free
4. Copy your API key (format: single token string)

**Optional Pro AI Tier:**
- Cost: $25/month
- Queries: 50,000/month
- For production use or heavy research

**Configure Environment:**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
BRAVE_SEARCH_API_KEY=your_actual_key_here
```

### 2. Install Dependencies

```bash
# Already installed if you ran Phases 1 & 2
pip install requests python-dotenv pytest

# Or install all project dependencies
pip install -r requirements.txt
```

---

## Quick Start

### 1. Verify Installation

```bash
# Check that Web Search tool can be imported
python -c "from src.tools.web_search_tool import WebSearchTool; print('✅ Web Search Tool installed')"
```

### 2. Run Example Script

```bash
# Run comprehensive examples (requires API key)
python examples/test_web_search.py
```

**Expected Output:**
- ✅ 10 real-world investment research examples
- ✅ Apple management research
- ✅ Coca-Cola moat assessment
- ✅ Microsoft competitive landscape
- ✅ Tesla recent news
- ✅ Meta risk assessment
- ✅ Integration with GuruFocus demonstrated
- ✅ Error handling shown
- ✅ Multi-query advanced analysis

### 3. Run Test Suite

```bash
# Run mocked tests (no API key needed)
python -m pytest tests/test_tools/test_web_search.py -v -m "not requires_api"

# Run ALL tests including real API (requires valid key)
python -m pytest tests/test_tools/test_web_search.py -v
```

**Expected Results:**
- ✅ 30+ mocked tests pass
- ✅ 5+ real API tests pass (if key provided)
- ✅ All tests complete in 30-60 seconds

---

## Manual Testing Guide

### Test 1: General Search (Basic Functionality)

```python
from src.tools.web_search_tool import WebSearchTool

tool = WebSearchTool()
result = tool.execute(
    query="economic moat competitive advantage",
    company="Apple Inc",
    count=10,
    search_type="general"
)

print(f"Success: {result['success']}")
print(f"Query: {result['data']['query']}")
print(f"Total Results: {result['data']['total_results']}")
print(f"First Result: {result['data']['results'][0]['title']}")
```

**Expected:**
- `success: True`
- Query includes "Apple Inc" (company context added)
- Total results: 10
- Results contain title, URL, description, domain
- **CRITICAL:** Each result has `extra_snippets` array (RAG-optimized)

### Test 2: News Search with Freshness Filter

```python
result = tool.execute(
    query="latest developments announcements",
    company="Tesla",
    count=10,
    search_type="news",
    freshness="week"
)

print(f"Search Type: {result['data']['search_type']}")
print(f"Freshness: {result['data']['freshness']}")
print(f"First Result Date: {result['data']['results'][0]['published_date']}")
```

**Expected:**
- Search type: "news"
- Freshness: "week"
- Results from past 7 days
- Published dates in ISO format (YYYY-MM-DD)
- News-specific content (press releases, articles)

### Test 3: Recent Search (Past 30 Days)

```python
result = tool.execute(
    query="competitive landscape market share",
    company="Microsoft",
    count=10,
    search_type="recent"
)

print(f"Search Type: {result['data']['search_type']}")
all_recent = all(
    r.get('published_date', '') >= '2025-10-01'  # Adjust date
    for r in result['data']['results']
    if r.get('published_date')
)
print(f"All results recent: {all_recent}")
```

**Expected:**
- Search type: "recent"
- Results from past 30 days
- Mix of news and general content (fresher than general search)

### Test 4: RAG-Optimized Snippets (MOST IMPORTANT)

```python
result = tool.execute(
    query="brand strength customer loyalty",
    company="Coca-Cola",
    count=5,
    search_type="general"
)

first_result = result['data']['results'][0]
print(f"Title: {first_result['title']}")
print(f"Description: {first_result['description']}")
print(f"\n📝 Extra Snippets (for LLM context):")
for i, snippet in enumerate(first_result['extra_snippets'], 1):
    print(f"{i}. {snippet}")
```

**Expected:**
- **CRITICAL:** `extra_snippets` array present (typically 3-5 snippets)
- Snippets contain additional context beyond description
- Total content: description + extra_snippets = rich context for AI
- This is what makes Brave Search ideal for RAG applications

### Test 5: Company Context Addition

```python
# Test 1: Company context auto-added
result1 = tool.execute(query="management quality", company="Apple Inc")
print(f"Query 1: {result1['data']['query']}")
# Expected: "management quality Apple Inc"

# Test 2: Company already in query - no duplication
result2 = tool.execute(query="Apple management quality", company="Apple Inc")
print(f"Query 2: {result2['data']['query']}")
# Expected: "Apple management quality" (no duplication)

# Test 3: No company specified
result3 = tool.execute(query="investment philosophy Warren Buffett")
print(f"Query 3: {result3['data']['query']}")
# Expected: "investment philosophy Warren Buffett" (unchanged)
```

**Expected:**
- Smart context addition (avoids duplication)
- Query normalization works correctly
- Company context enhances search relevance

### Test 6: HTML Cleaning and Text Normalization

```python
# This is tested internally - verify in results
result = tool.execute(query="Q&A investor relations", company="Microsoft")

for r in result['data']['results'][:3]:
    # Check that HTML entities are unescaped
    assert '&#' not in r['title']
    assert '&#' not in r['description']
    assert '&amp;' not in r['title']

    # Check that HTML tags are removed
    assert '<' not in r['description']
    assert '>' not in r['description']

    print(f"✅ {r['title']} - Clean text")
```

**Expected:**
- All HTML entities unescaped (&#39;→', &amp;→&)
- All HTML tags removed
- Clean, readable text
- No encoding artifacts

### Test 7: Date Parsing

```python
# Date parsing is tested internally
result = tool.execute(
    query="latest news",
    company="Tesla",
    search_type="news",
    freshness="week"
)

for r in result['data']['results']:
    if r.get('published_date'):
        # Should be ISO format YYYY-MM-DD
        assert len(r['published_date']) == 10
        assert r['published_date'].count('-') == 2
        print(f"✅ Date: {r['published_date']}")
```

**Expected:**
- Dates in ISO format (YYYY-MM-DD)
- Converted from relative ("2 days ago") to absolute
- Reasonable dates (not future, not too far past)

### Test 8: Domain Extraction

```python
result = tool.execute(query="financial analysis", company="Berkshire Hathaway")

for r in result['data']['results'][:5]:
    print(f"URL: {r['url']}")
    print(f"Domain: {r['domain']}")
    # Domain should be extracted from URL
    assert r['domain'] in r['url']
    print()
```

**Expected:**
- Domain extracted correctly (forbes.com, reuters.com, etc.)
- Handles www. prefix correctly
- Handles subdomains correctly

### Test 9: Error Handling - Invalid Input

```python
# Test 1: Empty query
result = tool.execute(query="", company="Apple")
print(f"Empty query success: {result['success']}")  # False
print(f"Error: {result['error']}")  # "Query cannot be empty"

# Test 2: Query too long
long_query = "a" * 401
result = tool.execute(query=long_query)
print(f"Long query success: {result['success']}")  # False
print(f"Error: {result['error']}")  # "Query must be between 1 and 400 characters"

# Test 3: Invalid count
result = tool.execute(query="test", count=100)
print(f"Invalid count success: {result['success']}")  # False
print(f"Error: {result['error']}")  # "Count must be between 1 and 20"

# Test 4: Invalid search type
result = tool.execute(query="test", search_type="invalid")
print(f"Invalid type success: {result['success']}")  # False
print(f"Error: {result['error']}")  # "Invalid search_type"
```

**Expected:**
- All validation errors caught gracefully
- No exceptions raised
- Informative error messages
- Returns error dict with `success: False`

### Test 10: Error Handling - API Errors

```python
# Test with invalid API key (modify .env temporarily)
# This will trigger 401 Unauthorized

result = tool.execute(query="test query")
print(f"Success: {result['success']}")
print(f"Error: {result['error']}")
```

**Expected:**
- Handles 401 (invalid API key) gracefully
- Handles 429 (rate limit) with retry logic
- Handles 500 (server error) with retry logic
- Handles timeout gracefully
- No crashes or unhandled exceptions

### Test 11: Integration with GuruFocus Tool

```python
from src.tools.gurufocus_tool import GuruFocusTool
from src.tools.web_search_tool import WebSearchTool

# Step 1: Get company data from GuruFocus
gf_tool = GuruFocusTool()
gf_result = gf_tool.execute(ticker="AAPL", endpoint="summary")
company_name = gf_result['data']['company_name']  # "Apple Inc"
roic = gf_result['data']['metrics']['roic']

print(f"Company: {company_name}")
print(f"ROIC: {roic*100:.1f}%")

# Step 2: High ROIC suggests moat - validate with web search
ws_tool = WebSearchTool()
ws_result = ws_tool.execute(
    query="economic moat competitive advantage source",
    company=company_name,
    search_type="general"
)

print(f"\nMoat Research Results: {len(ws_result['data']['results'])} articles")
print(f"Top Result: {ws_result['data']['results'][0]['title']}")
```

**Expected:**
- GuruFocus provides company name
- Web Search uses it for context
- Seamless integration
- Combined analysis: quantitative (ROIC) + qualitative (moat research)

---

## Test Checklist

Mark each test as you complete it:

- [ ] API key setup works
- [ ] General search returns results for "Apple economic moat"
- [ ] News search returns recent results (past week)
- [ ] Recent search returns results from past 30 days
- [ ] **RAG-optimized snippets present in all results (MOST IMPORTANT)**
- [ ] Company context auto-added to queries
- [ ] No duplication when company already in query
- [ ] HTML entities unescaped correctly
- [ ] HTML tags removed from text
- [ ] Dates parsed to ISO format (YYYY-MM-DD)
- [ ] Domains extracted correctly
- [ ] Empty query returns proper error
- [ ] Query too long returns proper error
- [ ] Invalid parameters return proper errors
- [ ] API errors handled gracefully (401, 429, 500)
- [ ] Integration with GuruFocus Tool works
- [ ] All mocked tests pass
- [ ] All real API tests pass (if key provided)

---

## Known Issues & Limitations

### API Constraints
- **Free tier:** 2,000 queries/month (sufficient for testing)
- **Rate limits:** 1 query/second on free tier
- **Rate limit handling:** Tool retries with exponential backoff (1s, 2s, 4s)

### Search Quality
- Results depend on Brave Search index quality
- Some niche queries may have fewer results
- Non-English queries may have limited results
- Use well-formed, specific queries for best results

### Date Parsing Approximations
- "1 month ago" → 30 days (approximation)
- "1 year ago" → 365 days (ignores leap years)
- Sufficient for investment research use case

### Company Context Limitations
- Smart duplication check (handles "Apple" vs "Apple Inc")
- But may not catch all edge cases (e.g., "AAPL" vs "Apple Inc")
- Generally works well for full company names

### RAG Snippet Availability
- Not all results have extra_snippets
- Typically 3-5 per result, sometimes 1-2
- Depends on Brave Search's content extraction
- Always present when available (tool doesn't filter)

---

## Troubleshooting

### "BRAVE_SEARCH_API_KEY environment variable not set"

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# If not, copy example
cp .env.example .env

# Edit .env and add your key
nano .env  # or use any text editor
```

### "Search query failed with status 401"

**Solution:**
- Invalid API key
- Check .env file has correct key
- Verify no extra spaces or quotes
- Get new key from https://brave.com/search/api/

### "Search query failed with status 429"

**Solution:**
- Rate limit exceeded
- Tool should retry automatically with backoff
- If persistent, wait 60 seconds
- Free tier: 1 query/second limit
- Consider Pro AI tier for higher limits

### "Request timeout"

**Solution:**
- Check internet connection
- Brave Search API may be slow (normal for some queries)
- Tool retries automatically up to 3 times
- Timeout set to 30 seconds (generous)

### Tests fail with "No module named 'src'"

**Solution:**
```bash
# Run tests from project root
cd /path/to/basira-agent
python -m pytest tests/test_tools/test_web_search.py -v
```

### "No extra_snippets in results"

**Solution:**
- Some results may not have extra_snippets
- Depends on Brave Search's content extraction
- Check that `extra_snippets=True` is in API params (it is)
- Try different queries - news/articles usually have more snippets

---

## Performance Expectations

### Response Times
- General search: 0.5-3 seconds
- News search: 0.5-3 seconds
- Recent search: 0.5-3 seconds
- Variation depends on network, query complexity

### Rate Limiting Impact
- Free tier: 1 query/second max
- Sequential requests: +1s per request minimum
- 10 queries: ~10-15 seconds total
- Normal for free tier

### API Costs
- **Free tier:** $0/month for 2,000 queries
- **Pro AI tier:** $25/month for 50,000 queries
- Per-analysis cost: ~3-5 queries
- Cost per analysis on Pro tier: ~$0.0015 (negligible)

---

## Success Criteria

Phase 3 User Testing is successful when:

- [x] Web Search Tool implements Tool interface correctly
- [x] All 3 search types work (general, news, recent)
- [x] Freshness filters work correctly (day, week, month, year)
- [x] Returns RAG-optimized snippets (extra_snippets)
- [x] Company context addition works
- [x] HTML cleaning works (entities, tags, whitespace)
- [x] Date parsing works (relative → ISO format)
- [x] Domain extraction works
- [x] Error handling robust (validation, API errors, timeout)
- [x] All mocked tests pass
- [ ] All real API tests pass (USER MUST VERIFY with key)
- [ ] Integration with GuruFocus Tool works (USER MUST VERIFY)
- [ ] User can research real companies
- [ ] No crashes or unhandled errors

---

## Real-World Validation

### Cross-Check Research Quality

**Test Query:** "Apple economic moat competitive advantage"

1. Run web search with tool
2. Visit top 3 URLs manually
3. Compare tool snippets vs actual page content
4. Verify snippets are relevant and accurate

**Expected:**
- Snippets accurately represent page content
- No hallucination or fabrication
- URLs are accessible and relevant
- Domain extraction correct

### Test Buffett-Style Research Workflow

**Scenario:** Researching Microsoft's moat durability

```python
# Phase 1: Get quantitative data (GuruFocus)
# ROIC: 31.2% → suggests strong moat

# Phase 2: Validate moat qualitatively (Web Search)
result = tool.execute(
    query="competitive advantage moat durability switching costs",
    company="Microsoft",
    search_type="general"
)

# Phase 3: Recent competitive threats (Web Search)
result = tool.execute(
    query="competitive threats new entrants",
    company="Microsoft",
    search_type="recent"
)

# Phase 4: Management quality (Web Search)
result = tool.execute(
    query="Satya Nadella CEO leadership capital allocation",
    company="Microsoft",
    search_type="general"
)
```

**Expected:**
- 3-4 searches provide comprehensive qualitative picture
- Complements quantitative analysis from GuruFocus
- Enables AI agent to build investment thesis
- Demonstrates real-world workflow

---

## Next Steps After Testing

1. **If All Tests Pass:**
   - Move to Strategic Review package
   - Approve Phase 3 completion
   - Proceed to Phase 4-5 (Tool Integration & AI Agent)

2. **If Issues Found:**
   - Document issues in GitHub Issues
   - Tag as `phase-3` and `web-search-tool`
   - Builder will address and re-submit

3. **Enhancements for Future:**
   - Add caching for repeated queries?
   - Support for batch queries?
   - Custom result ranking/filtering?
   - Integration with other search engines?

---

## Questions or Issues?

**Documentation:**
- Tool Spec: `docs/tool_specs/web_search_tool_spec.md`
- API Docs: `docs/api_references/brave_search_api.md`
- Buffett Principles: `docs/BUFFETT_PRINCIPLES.md`

**Code:**
- Implementation: `src/tools/web_search_tool.py`
- Tests: `tests/test_tools/test_web_search.py`
- Examples: `examples/test_web_search.py`

**Support:**
- GitHub Issues: https://github.com/i314nk/basirah-agent/issues
- Tag issues with `phase-3` and `web-search-tool`

---

**PHASE 3 USER TESTING PACKAGE COMPLETE**

**Date:** October 30, 2025
**Status:** ✅ Ready for Testing
**Approver:** User (You)
**Next Package:** PHASE_3_STRATEGIC_REVIEW.md
