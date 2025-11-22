# Proposal: Hybrid Web Search System

**Date:** 2025-11-14
**Status:** PROPOSED
**Priority:** HIGH (Solves Brave Search rate limiting)

---

## Problem

**Current Situation:**
- All web searches go through Brave Search API
- Brave Search free tier: 2,000 calls/month
- **Hit rate limit during NVO deep dive test** (~30+ search calls)
- Analysis blocked/degraded when limit exceeded

**Test Evidence:**
```
ERROR:src.tools.web_search_tool:Rate limit exceeded
Free tier: 2,000 calls/month
Consider upgrading to Pro AI ($25/month, 50K calls)
```

---

## Opportunity

**Kimi (Moonshot AI) has native web search:**
- Built-in `$web_search` function
- No rate limits (part of Kimi subscription)
- Native integration with model reasoning
- Returns search results directly to model

---

## Proposed Solution

### **Hybrid Web Search System**

Route web search requests based on provider capabilities:

```
┌─────────────────────────────────────┐
│     web_search_tool.execute()       │
└───────────────┬─────────────────────┘
                │
                ├─── Is provider Kimi? ──────┐
                │                             ▼
                │                   ┌──────────────────────┐
                │                   │ Use Kimi Native      │
                │                   │ $web_search          │
                │                   │ (No rate limits)     │
                │                   └──────────────────────┘
                │
                └─── Other provider ─────────┐
                                             ▼
                                   ┌──────────────────────┐
                                   │ Use Brave Search API │
                                   │ (Has rate limits)    │
                                   └──────────────────────┘
```

---

## Implementation

### **Phase 1: Add Provider Context to Tools**

**Problem:** Tools don't currently know which provider is calling them.

**Solution:** Pass provider info when executing tools.

**Files Modified:**
- `src/agent/buffett_agent.py` - Pass provider to tool execution
- `src/llm/providers/kimi.py` - Provide provider name
- `src/tools/web_search_tool.py` - Accept provider parameter

**Example:**
```python
# In buffett_agent.py
tool_result = tool.execute(
    **tool_input,
    _provider=self.llm_client.provider_name  # NEW
)

# In web_search_tool.py
def execute(self, query: str, _provider: str = None, **kwargs):
    if _provider == "kimi":
        return self._execute_kimi_native_search(query, **kwargs)
    else:
        return self._execute_brave_search(query, **kwargs)
```

---

### **Phase 2: Implement Kimi Native Search**

**Add to web_search_tool.py:**

```python
def _execute_kimi_native_search(self, query: str, search_type: str = "general", **kwargs):
    """
    Execute web search using Kimi's native $web_search function.

    This is a pass-through that signals to the Kimi provider to use
    its built-in web search capability.

    Args:
        query: Search query
        search_type: Type of search (general, news, recent)

    Returns:
        Dict with search results from Kimi native search
    """
    return {
        "use_kimi_native_search": True,
        "query": query,
        "search_type": search_type,
        "note": "Kimi will execute native $web_search"
    }
```

**Modify kimi.py provider:**

```python
# In kimi.py ReAct loop
tools_param = self._get_tool_definitions()

# Add Kimi native web search if web_search_tool is present
if any("web_search" in t.get("name", "") for t in tools_param):
    tools_param.append({
        "type": "builtin_function",
        "function": {
            "name": "$web_search"
        }
    })
    logger.info("Added Kimi native $web_search capability")
```

---

### **Phase 3: Handle Kimi Search Results**

**When Kimi returns web search results:**

```python
# In kimi.py provider ReAct loop
if tool_call.function.name == "$web_search":
    logger.info(f"Kimi executed native web search: {tool_call.function.arguments}")

    # Kimi handles search internally, just acknowledge
    tool_results.append({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": "$web_search",
        "content": "Web search completed by Kimi"
    })
```

---

## Benefits

### **Cost Savings**
- Avoid Brave Search Pro upgrade ($25/month)
- Use included Kimi capabilities

### **No Rate Limits**
- Kimi native search has no separate limits
- Deep dive analyses can make 50+ web searches without issues

### **Better Integration**
- Kimi can reason over search results natively
- No need to format/parse external API responses

### **Backward Compatible**
- Claude and other providers still use Brave Search
- Existing Brave Search functionality unchanged

---

## Trade-offs

### **Advantages**

| Feature | Kimi Native | Brave Search |
|---------|-------------|--------------|
| Rate Limits | None | 2,000/month (free) |
| Cost | Included | $25/month (pro) |
| Integration | Native | External API |
| Result Format | Model-optimized | Manual parsing |
| Search Quality | Good | Excellent |

### **Disadvantages**

| Aspect | Kimi Native | Brave Search |
|--------|-------------|--------------|
| Consistency | Varies by provider | Same for all |
| Control | Limited | Full control |
| Freshness filters | Unknown | Explicit (day/week/month) |
| Search types | Unknown | 3 types (general/news/recent) |
| Citations | Automatic | Manual extraction |

---

## Implementation Plan

### **Step 1: Research Kimi Native Search**
- [ ] Test Kimi `$web_search` behavior
- [ ] Document result format
- [ ] Test search types (news, recent, etc.)
- [ ] Compare quality vs. Brave Search

### **Step 2: Refactor Tool Execution**
- [ ] Add provider context to tool execution
- [ ] Update all tool execute() signatures
- [ ] Pass provider name through call chain

### **Step 3: Implement Routing Logic**
- [ ] Add provider detection to web_search_tool
- [ ] Implement Kimi native search path
- [ ] Keep Brave Search for other providers

### **Step 4: Update Kimi Provider**
- [ ] Add `$web_search` builtin function to tools
- [ ] Handle Kimi search result format
- [ ] Log when native search is used

### **Step 5: Testing**
- [ ] Test NVO deep dive with Kimi (should use native search)
- [ ] Test NVO deep dive with Claude (should use Brave Search)
- [ ] Verify no rate limit errors with Kimi
- [ ] Compare analysis quality

---

## Alternative: Fallback System

Instead of provider-based routing, implement a **fallback system**:

1. Try Brave Search first
2. If rate limit error → Switch to Kimi native search (if available)
3. Log when fallback occurs

**Advantages:**
- Consistent Brave Search quality when available
- Automatic failover when rate limited
- Simple implementation

**Disadvantages:**
- Wastes Brave Search quota
- Requires error handling
- Mixed result formats in single analysis

---

## Recommendation

**Implement provider-based routing (not fallback)**

**Reasons:**
1. Kimi native search is **free and unlimited**
2. No point paying for/using Brave Search if Kimi has native capability
3. Better model integration when search is native
4. Simpler implementation (route once, not fallback)

**Timeline:**
- Research & Testing: 2 hours
- Implementation: 4 hours
- Testing & Verification: 2 hours
- **Total: ~1 day**

**Priority:** HIGH - Unblocks deep dive analyses when using Kimi

---

## Success Criteria

1. ✅ Kimi-based analyses use native `$web_search` (0 Brave API calls)
2. ✅ Claude-based analyses use Brave Search (existing behavior)
3. ✅ No rate limit errors during NVO deep dive with Kimi
4. ✅ Analysis quality maintained or improved
5. ✅ Backward compatible with existing code

---

## Future Enhancements

### **Phase 2: Add More Provider-Native Tools**

**Perplexity AI:**
- Entire API is search-focused
- Could replace Brave Search entirely for all providers
- Returns AI-summarized results with citations

**OpenAI:**
- ChatGPT has web browsing, but not exposed in API (yet)
- Watch for future capabilities

**Anthropic Claude:**
- No native search currently
- Continue using Brave Search

---

## Conclusion

**YES, we can and should use provider-native web search APIs.**

Kimi's `$web_search` eliminates rate limit issues, reduces costs, and provides better integration. The implementation is straightforward and backward compatible.

**Recommendation:** Proceed with implementation after testing Kimi native search behavior.

---

**Proposed By:** Claude Code
**Date:** 2025-11-14
**Status:** Awaiting approval & testing
**Next Step:** Test Kimi `$web_search` to understand result format
