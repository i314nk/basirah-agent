# Web Search API Implementation Architecture

**Summary:** Provider-native web search is implemented **across both** the Agent layer and Provider layer.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BUFFETT AGENT                            │
│                  (Tool Routing Layer)                       │
│                                                             │
│  _get_tool_definitions()                                   │
│    │                                                         │
│    ├─ Detects provider type                                │
│    │                                                         │
│    ├─ Claude → web_search_20250305                         │
│    ├─ Kimi   → $web_search (builtin_function)             │
│    └─ Other  → web_search_tool (fallback)                 │
│                                                             │
└──────────────────┬──────────────────────────────────────────┘
                   │ Tools sent to provider
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                  LLM PROVIDERS                              │
│              (Execution & Parsing Layer)                    │
│                                                             │
│  ┌──────────────────────────┐  ┌────────────────────────┐ │
│  │   CLAUDE PROVIDER        │  │   KIMI PROVIDER        │ │
│  │                          │  │                        │ │
│  │ • Receives tools         │  │ • Receives tools       │ │
│  │ • Passes to Claude API   │  │ • Converts to OpenAI   │ │
│  │ • Handles responses:     │  │   format               │ │
│  │   - server_tool_use      │  │ • Passes through       │ │
│  │   - web_search_result    │  │   builtin_function     │ │
│  │ • Tracks search count    │  │ • Handles $web_search  │ │
│  │ • Calculates cost        │  │   tool calls           │ │
│  │   ($10/1K searches)      │  │ • Logs token usage     │ │
│  └──────────────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                   │
                   ↓ Results returned to agent
```

---

## Layer 1: Agent (Tool Routing)

**File:** [src/agent/buffett_agent.py](src/agent/buffett_agent.py:168-243)

**Responsibility:** Decide WHICH web search tool to use based on provider

### Implementation

```python
def _get_tool_definitions(self) -> List[Dict[str, Any]]:
    """Route to provider-native web search when available."""

    # Detect provider
    provider_info = self.llm.get_provider_info()
    provider = provider_info.get("provider", "").lower()

    # Standard tools (same for all providers)
    tools = [gurufocus_tool, sec_filing_tool, calculator_tool]

    # Provider-specific web search
    if provider == "claude":
        tools.append({
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 10,
            "allowed_domains": ["sec.gov", "reuters.com", ...]
        })

    elif provider == "kimi":
        tools.append({
            "type": "builtin_function",
            "function": {"name": "$web_search"}
        })

    else:
        # Fallback for unknown providers
        tools.append(web_search_tool)

    return tools
```

**Key Points:**
- ✅ Provider detection via `llm.get_provider_info()`
- ✅ Different tool format for each provider
- ✅ Fallback to standard tool for unknowns
- ✅ Same logic in `sharia_screener.py`

---

## Layer 2: Providers (Execution & Parsing)

### Claude Provider

**File:** [src/llm/providers/claude.py](src/llm/providers/claude.py:238-246)

**Responsibility:** Handle Claude-specific web search responses

#### Tool Passthrough

Tools are passed directly to Claude API - no conversion needed:

```python
# Claude accepts web_search_20250305 natively
response = client.messages.create(
    model="claude-sonnet-4.5",
    tools=tools,  # Includes web_search_20250305
    ...
)
```

#### Response Handling

```python
# Handle special content blocks
elif block.type == "server_tool_use":
    # Claude executing web search internally
    current_block = {
        "type": "server_tool_use",
        "id": block.id,
        "name": block.name,
        "input": {}
    }
    logger.info(f"[Server Tool Use - Native Web Search] {block.name}")

elif block.type == "web_search_tool_result":
    # Results from Claude's search
    current_block = {
        "type": "web_search_tool_result",
        "tool_use_id": block.tool_use_id,
        "content": []
    }
```

#### Cost Tracking

**File:** [src/llm/providers/claude.py](src/llm/providers/claude.py:215-220, 384-403)

```python
# Track web search requests
if hasattr(event.message.usage, 'server_tool_use'):
    web_searches = getattr(event.message.usage.server_tool_use,
                          'web_search_requests', 0)
    total_web_search_requests += web_searches

# Calculate cost ($10/1K searches)
web_search_cost = (total_web_search_requests / 1000) * 10.0
total_cost = input_cost + output_cost + web_search_cost

# Add to metadata
if total_web_search_requests > 0:
    metadata["web_search_requests"] = total_web_search_requests
    metadata["web_search_cost"] = web_search_cost
```

---

### Kimi Provider

**File:** [src/llm/providers/kimi.py](src/llm/providers/kimi.py)

**Responsibility:** Handle Kimi-specific web search and tool conversion

#### Tool Conversion (Pass-Through)

**Lines 187-192:**

```python
def _convert_tools_to_openai_format(self, tools):
    for tool in tools:
        if tool.get("type") == "builtin_function":
            # Pass through unchanged - already in correct format
            openai_tools.append(tool)
        else:
            # Convert standard tools to OpenAI format
            openai_tools.append(converted_tool)
```

**Key Point:** `$web_search` is NOT converted - passed through as-is!

#### Tool Execution Handling

**Lines 308-320:**

```python
if tool_name == "$web_search":
    # Kimi builtin web search - pass arguments back unchanged
    # Kimi executes search internally
    logger.info(f"[Kimi Native Web Search] Query: {tool_args.get('query', 'N/A')}")

    # Log token usage
    search_tokens = tool_args.get("usage", {}).get("total_tokens", 0)
    if search_tokens > 0:
        logger.info(f"[Web Search] Will use ~{search_tokens} tokens for results")

    # Pass arguments back unchanged (Kimi handles execution)
    result_content = json.dumps(tool_args)
else:
    # Regular tool - execute it
    result = tool_executor(tool_name, tool_args)
    result_content = str(result)
```

**Key Points:**
- ✅ Detects `$web_search` tool calls
- ✅ Logs query and token usage
- ✅ Returns arguments unchanged (Kimi executes internally)
- ✅ No separate cost (included in token costs)

---

## Layer 3: Web Search Tool (Fallback Only)

**File:** [src/tools/web_search_tool.py](src/tools/web_search_tool.py)

**Responsibility:** Provide schema and minimal fallback for unknown providers

### Current Implementation

```python
class WebSearchTool(Tool):
    """Simple proxy - signals need for web search."""

    def execute(self, query: str, ...) -> Dict[str, Any]:
        """Should NOT be called for Claude/Kimi."""
        logger.warning("Web search tool called directly (should use provider-native)")

        return {
            "status": "provider_native_expected",
            "message": "Claude uses web_search_20250305, Kimi uses $web_search",
            "note": "If seeing this, check provider configuration"
        }
```

**Key Points:**
- ✅ Reduced from 639 lines to 194 lines
- ✅ No actual search implementation (proxy only)
- ✅ Used only for unknown providers
- ✅ Logs warning if called (shouldn't happen in production)

---

## Data Flow: Complete Request Cycle

### Claude Flow

```
1. Agent: Creates web_search_20250305 tool definition
2. Agent: Passes to claude.py provider
3. Claude Provider: Sends to Claude API unchanged
4. Claude API: Executes search internally
5. Claude API: Returns server_tool_use + web_search_tool_result blocks
6. Claude Provider: Parses blocks, tracks search count
7. Claude Provider: Calculates search cost ($10/1K)
8. Agent: Receives results with metadata
```

### Kimi Flow

```
1. Agent: Creates $web_search builtin_function definition
2. Agent: Passes to kimi.py provider
3. Kimi Provider: Passes through unchanged in tool conversion
4. Kimi Provider: Sends to Kimi API
5. Kimi API: Returns tool_call with $web_search
6. Kimi Provider: Detects $web_search, passes args back
7. Kimi Provider: Adds tool response to conversation
8. Kimi API: Executes search, returns results in next response
9. Agent: Receives results (search cost included in tokens)
```

---

## Cost Breakdown

### Claude

| Component | Cost | Where Tracked |
|-----------|------|---------------|
| Input tokens | $3/1M | `claude.py:384` |
| Output tokens | $15/1M | `claude.py:384` |
| **Web searches** | **$10/1K** | `claude.py:384-403` |

**Example:** 30 searches = $0.30 search cost

### Kimi

| Component | Cost | Where Tracked |
|-----------|------|---------------|
| Input tokens | $0.03/1K | `kimi.py` (standard) |
| Output tokens | $0.03/1K | `kimi.py` (standard) |
| **Web search tokens** | **~9K tokens/search** | Included in token costs |

**Example:** 30 searches × 9K tokens × $0.03/1K = $8.10 (token costs only, no search fee)

---

## Why Split Implementation?

### Agent Layer Handles:
- ✅ **Provider detection** - Which provider am I using?
- ✅ **Tool routing** - Which web search format do I need?
- ✅ **Configuration** - Domain filtering, max uses, etc.

### Provider Layer Handles:
- ✅ **Format conversion** - Convert tools to provider API format
- ✅ **Response parsing** - Handle provider-specific response blocks
- ✅ **Cost tracking** - Track usage and calculate costs
- ✅ **Execution logic** - How to handle tool calls

**Benefits:**
1. **Separation of concerns** - Agent doesn't know provider details
2. **Easy to extend** - Add new provider = implement in provider layer
3. **Consistent interface** - Agent uses same pattern for all providers
4. **Provider flexibility** - Each provider handles its quirks

---

## Adding a New Provider (Example: Perplexity)

### Step 1: Agent Layer

**File:** `buffett_agent.py`

```python
elif provider == "perplexity":
    tools.append({
        "type": "perplexity_search",
        "name": "web_search"
    })
```

### Step 2: Provider Layer

**File:** `src/llm/providers/perplexity.py` (new)

```python
class PerplexityProvider:
    def run_react_loop(self, tools, ...):
        # Perplexity has built-in search - no tool conversion needed
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=messages,
            # Perplexity searches automatically, no tools param
        )

        # Parse response (includes search results)
        return parsed_response
```

### Step 3: Done!

No changes needed to:
- ❌ Web search tool
- ❌ Analysis logic
- ❌ Validation logic

---

## Summary

**Question:** How is web search API implemented?

**Answer:** **Both places!**

| Layer | What It Does | Files |
|-------|--------------|-------|
| **Agent** | Tool routing & configuration | `buffett_agent.py`, `sharia_screener.py` |
| **Provider** | Execution & parsing | `claude.py`, `kimi.py` |
| **Tool** | Schema & fallback | `web_search_tool.py` |

**Design Pattern:** **Strategy Pattern**
- Agent selects strategy (which web search)
- Provider implements strategy (how to execute)
- Tool provides interface (what search does)

**Benefits:**
- ✅ Clean separation of concerns
- ✅ Easy to add new providers
- ✅ Consistent agent interface
- ✅ Provider-specific optimizations

---

**Created:** 2025-11-15
**Purpose:** Document web search architecture
**Related:** PHASE_7.6D_FINAL_IMPLEMENTATION.md
