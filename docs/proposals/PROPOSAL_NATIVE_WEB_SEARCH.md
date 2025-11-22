# Proposal: Replace Brave Search with Provider-Native Web Search

**Date:** 2025-11-14
**Status:** RECOMMENDED
**Priority:** HIGH
**Impact:** Eliminates rate limits, reduces costs, improves quality

---

## Executive Summary

**Both Claude and Kimi now have native web search capabilities.** We should completely replace Brave Search API with provider-native implementations.

**Benefits:**
- ✅ **No rate limits** - No more 2,000/month Brave Search cap
- ✅ **Lower costs** - Kimi includes search in tokens, Claude $10/1K
- ✅ **Better integration** - Native to model reasoning
- ✅ **Automatic citations** - Claude provides source attribution
- ✅ **One less dependency** - Eliminate Brave Search API entirely

---

## Current Problem

**Brave Search Limitations:**
```
ERROR: Rate limit exceeded
Free tier: 2,000 calls/month
Paid tier: $25/month for 50,000 calls

Test Evidence:
- NVO deep dive: ~35 search calls
- Hit rate limit during validation
- Analysis degraded/blocked
```

---

## Solution: Provider-Native Web Search

### **Option 1: Claude Native Web Search**

**Type:** `web_search_20250305`

**Supported Models:**
- claude-sonnet-4-5-20250929
- claude-sonnet-4-20250514
- claude-haiku-4-5-20251001
- claude-opus-4-1-20250805

**Implementation:**
```python
# In claude.py provider
tools = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 10,  # Limit searches per request

        # Optional: Domain filtering
        "allowed_domains": ["sec.gov", "nasdaq.com", "reuters.com"],

        # Optional: Localization
        "user_location": {
            "type": "approximate",
            "country": "US"
        }
    }
]

response = client.messages.create(
    model="claude-sonnet-4-5",
    messages=messages,
    tools=tools
)
```

**Response Format:**
```python
{
    "role": "assistant",
    "content": [
        # Search decision
        {"type": "text", "text": "I'll search for..."},

        # Search execution (automatic)
        {"type": "server_tool_use", "name": "web_search", "input": {"query": "..."}},

        # Search results
        {"type": "web_search_tool_result", "content": [
            {
                "type": "web_search_result",
                "url": "https://...",
                "title": "...",
                "page_age": "November 2025"
            }
        ]},

        # Response with citations
        {
            "type": "text",
            "text": "Based on the search results...",
            "citations": [
                {
                    "type": "web_search_result_location",
                    "url": "https://...",
                    "title": "...",
                    "cited_text": "Up to 150 chars..."
                }
            ]
        }
    ],
    "usage": {
        "input_tokens": 6039,
        "output_tokens": 931,
        "server_tool_use": {
            "web_search_requests": 1  # Billed at $10/1000
        }
    }
}
```

**Features:**
- ✅ Automatic execution (no manual implementation)
- ✅ **Automatic citations** with source URLs and excerpts
- ✅ Domain filtering (allowed/blocked lists)
- ✅ Max uses limit (prevent runaway costs)
- ✅ Localization support
- ✅ Prompt caching compatible
- ✅ Streaming support
- ✅ Batch API support

**Pricing:**
- **$10 per 1,000 searches**
- Plus standard token costs for search results
- Citations (cited_text, title, url) don't count as tokens

---

### **Option 2: Kimi Native Web Search**

**Type:** `builtin_function.$web_search`

**Supported Models:**
- kimi-k2-turbo-preview
- kimi-k2-thinking
- kimi-k2-0711-preview

**Implementation:**
```python
# In kimi.py provider
tools = [
    {
        "type": "builtin_function",
        "function": {
            "name": "$web_search"
        }
    }
]

# When Kimi calls $web_search:
tool_call = response.choices[0].message.tool_calls[0]

if tool_call.function.name == "$web_search":
    # Get token usage for search results
    search_tokens = json.loads(tool_call.function.arguments).get("usage", {}).get("total_tokens", 0)
    logger.info(f"Web search will use ~{search_tokens} tokens")

    # Return arguments as-is (Kimi executes internally)
    tool_result = {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": "$web_search",
        "content": tool_call.function.arguments  # Pass back as-is
    }
```

**How It Works:**
1. Kimi decides to search, generates `tool_calls` with `$web_search`
2. Returns arguments: `{"query": "...", "usage": {"total_tokens": 13046}}`
3. You pass arguments back **unchanged** in tool result
4. Kimi executes search internally and generates response
5. Search results counted as input tokens

**Features:**
- ✅ **Included in token costs** (no separate search fee)
- ✅ Simple implementation (just pass arguments back)
- ✅ Token usage reported in advance
- ✅ Compatible with kimi-k2-turbo-preview (dynamic sizing)
- ✅ Can coexist with other tools

**Pricing:**
- **$0 search fees** (only token costs)
- Search results counted as input tokens (~13K tokens per search typical)
- Use `kimi-k2-turbo-preview` for dynamic context sizing

---

## Implementation Strategy

### **Approach: Provider-Native Only (Recommended)**

Replace Brave Search entirely with provider-native implementations:

```
┌────────────────────────────────┐
│   web_search_tool.execute()    │
└────────────┬───────────────────┘
             │
             ├─── Claude? ────────────┐
             │                        ▼
             │              ┌──────────────────────┐
             │              │ Claude Native Search │
             │              │ type: web_search_... │
             │              │ $10/1K + tokens      │
             │              └──────────────────────┘
             │
             └─── Kimi? ─────────────┐
                                     ▼
                           ┌──────────────────────┐
                           │ Kimi Native Search   │
                           │ type: builtin_func   │
                           │ Only token costs     │
                           └──────────────────────┘
```

**Remove:**
- Brave Search API integration
- `BRAVE_SEARCH_API_KEY` requirement
- External HTTP requests to Brave
- Rate limit handling

---

## Implementation Steps

### **Phase 1: Add Claude Native Web Search**

**File:** `src/llm/providers/claude.py`

```python
def _get_tool_definitions(self) -> List[Dict[str, Any]]:
    """Get tool definitions in Claude format."""

    # Convert regular tools
    tools = []
    for tool_name, tool in self.tools.items():
        if tool_name == "web_search":
            # Use Claude native web search instead
            tools.append({
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10,  # Prevent runaway costs
                # Optional: Domain filtering for investment research
                "allowed_domains": [
                    "sec.gov",
                    "investor.com",
                    "nasdaq.com",
                    "reuters.com",
                    "bloomberg.com",
                    "ft.com"
                ]
            })
            logger.info("Using Claude native web search")
        else:
            # Regular tool conversion
            tools.append(self._convert_tool_schema(tool))

    return tools
```

**Handle Claude Search Results:**

```python
# In ReAct loop
for content_block in response.content:
    if content_block.type == "server_tool_use":
        # Claude is executing search
        logger.info(f"Claude executing native search: {content_block.input['query']}")

    elif content_block.type == "web_search_tool_result":
        # Search results returned
        search_count = len(content_block.content)
        logger.info(f"Claude search returned {search_count} results")

    elif content_block.type == "text" and hasattr(content_block, 'citations'):
        # Response with citations
        for citation in content_block.citations:
            logger.info(f"Citation: {citation.url} - {citation.title}")
```

---

### **Phase 2: Add Kimi Native Web Search**

**File:** `src/llm/providers/kimi.py`

```python
def _get_tool_definitions(self) -> List[Dict[str, Any]]:
    """Get tool definitions in Kimi format."""

    tools = []
    has_web_search = False

    for tool_name, tool in self.tools.items():
        if tool_name == "web_search":
            has_web_search = True
            # Don't add regular web_search tool - will use builtin instead
        else:
            # Regular tool conversion
            tools.append(self._convert_tool_schema(tool))

    # Add Kimi builtin web search if web_search_tool is present
    if has_web_search:
        tools.append({
            "type": "builtin_function",
            "function": {
                "name": "$web_search"
            }
        })
        logger.info("Using Kimi native $web_search")

    return tools
```

**Handle Kimi Search Execution:**

```python
# In ReAct loop - tool execution
if tool_call.function.name == "$web_search":
    # Parse arguments to get token usage estimate
    arguments = json.loads(tool_call.function.arguments)
    search_tokens = arguments.get("usage", {}).get("total_tokens", 0)
    logger.info(f"Kimi $web_search will use ~{search_tokens} tokens")

    # Return arguments as-is (Kimi executes internally)
    tool_results.append({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": "$web_search",
        "content": tool_call.function.arguments  # Pass back unchanged
    })
```

---

### **Phase 3: Remove Brave Search (Optional Fallback)**

**Option A: Complete Removal (Recommended)**

```python
# Remove from src/tools/web_search_tool.py
# Remove BRAVE_SEARCH_API_KEY requirement
# Remove Brave Search HTTP requests

# web_search_tool becomes a simple proxy:
class WebSearchTool(Tool):
    def execute(self, query: str, **kwargs):
        """
        Web search proxy - actual search handled by provider.

        This tool declaration signals to providers that web search is needed.
        Actual implementation uses provider-native search:
        - Claude: web_search_20250305
        - Kimi: $web_search builtin_function
        """
        return {
            "note": "Web search handled by provider natively",
            "query": query
        }
```

**Option B: Keep Brave Search as Fallback**

```python
def execute(self, query: str, _provider: str = None, **kwargs):
    """Execute web search using provider-native or Brave fallback."""

    if _provider in ["claude", "kimi"]:
        # Provider handles search natively
        return {
            "note": f"{_provider} native search",
            "query": query
        }
    else:
        # Fallback to Brave Search for unknown providers
        return self._execute_brave_search(query, **kwargs)
```

---

## Cost Analysis

### **Example: NVO Deep Dive (35 searches)**

| Provider | Search Cost | Token Cost (est) | Total | vs Brave |
|----------|-------------|------------------|-------|----------|
| **Kimi** | $0 | $15 (300K tokens) | **$15** | ✅ -$0 |
| **Claude** | $0.35 (35 × $0.01) | $30 (300K tokens) | **$30.35** | ✅ -$0 |
| **Brave** | $0 (free tier) | N/A | **$0** | Rate limited! |
| **Brave Pro** | $25/month | N/A | **$25** | ❌ Higher |

**Key Insights:**
- Kimi cheapest (search included in tokens)
- Claude more expensive but provides citations
- Brave free tier blocks analyses (rate limit)
- Brave Pro costs more than Kimi+Claude combined

---

## Testing Plan

### **Test 1: Claude Native Search**

```python
from src.llm.providers.claude import ClaudeProvider

provider = ClaudeProvider(model="claude-sonnet-4-5")
messages = [{"role": "user", "content": "What is Novo Nordisk's current CEO?"}]
tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

response = provider.generate(messages, tools)

# Verify:
# - Search executed automatically
# - Results include citations
# - Usage reports web_search_requests
```

### **Test 2: Kimi Native Search**

```python
from src.llm.providers.kimi import KimiProvider

provider = KimiProvider(model="kimi-k2-turbo-preview")
messages = [{"role": "user", "content": "What is Novo Nordisk's current CEO?"}]

# Provider should add $web_search builtin automatically
response = provider.generate_with_tools(messages)

# Verify:
# - tool_calls includes $web_search
# - Token usage reported in arguments
# - Search executes when arguments passed back
```

### **Test 3: NVO Deep Dive (Full Integration)**

```bash
python test_nvo_deep_dive.py --provider=kimi --enable-validation

# Expected:
# - 35+ web searches
# - NO rate limit errors
# - Search token usage logged
# - Final analysis quality maintained
```

---

## Migration Path

### **Step 1: Add Claude Support** (2 hours)
- Modify `claude.py` to use `web_search_20250305`
- Handle search results and citations
- Test with simple queries

### **Step 2: Add Kimi Support** (2 hours)
- Modify `kimi.py` to use `$web_search`
- Handle builtin_function tool calls
- Test token usage reporting

### **Step 3: Update web_search_tool** (1 hour)
- Make tool a proxy (signals need for search)
- Remove Brave Search implementation (or keep as fallback)
- Update documentation

### **Step 4: Integration Testing** (3 hours)
- Test quick screen (both providers)
- Test deep dive (both providers)
- Test validation with web search
- Compare quality vs Brave Search

### **Step 5: Documentation** (1 hour)
- Update README (remove Brave API key requirement)
- Document provider-native search
- Add cost comparison

**Total Time:** ~1 day

---

## Risks & Mitigation

### **Risk 1: Different Result Quality**

**Concern:** Provider searches may return different results than Brave
**Mitigation:**
- A/B test analyses (Brave vs native)
- Compare citation quality
- Monitor validation scores

### **Risk 2: Token Cost Increase**

**Concern:** Search results counted as tokens (expensive)
**Mitigation:**
- Use Kimi for high-volume (cheaper)
- Limit max_uses in Claude (prevent runaway)
- Monitor token usage in metadata

### **Risk 3: Less Control**

**Concern:** Can't customize search parameters (freshness, domains, etc.)
**Mitigation:**
- Claude supports domain filtering
- Use prompt engineering for specific searches
- Query construction can guide results

---

## Recommendation

**✅ IMPLEMENT PROVIDER-NATIVE SEARCH**

**Why:**
1. Eliminates rate limit issues (immediate benefit)
2. Lower costs (Kimi) or competitive costs (Claude)
3. Better integration (native reasoning)
4. Automatic citations (Claude)
5. One less API dependency

**Rollout:**
1. Implement Claude + Kimi native search (1 day)
2. Test thoroughly with deep dives
3. Keep Brave Search code as fallback initially
4. Remove Brave Search after 2 weeks if no issues

**Success Criteria:**
- ✅ No rate limit errors in deep dives
- ✅ Analysis quality maintained (validation scores)
- ✅ Cost competitive with Brave Pro ($25/month)
- ✅ Citations present in Claude outputs

---

## Conclusion

Both Claude and Kimi now have robust native web search capabilities that **eliminate the need for Brave Search API entirely**. The implementation is straightforward, costs are competitive, and benefits are substantial.

**Recommendation:** Proceed with implementation immediately. This solves the rate limiting issue that blocked the NVO deep dive test and improves overall system reliability.

---

**Proposed By:** Claude Code
**Date:** 2025-11-14
**Status:** READY FOR IMPLEMENTATION
**Priority:** HIGH
**Next Step:** Implement Claude + Kimi native search in providers
