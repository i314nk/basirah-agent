# Phase 7.7 Implementation Guide

**Purpose:** Step-by-step instructions for implementing hybrid architecture
**Audience:** Developers working on buffett_agent.py
**Status:** 🚧 In Progress

---

## Overview

This guide shows how to implement Phase 7.7 in **4 phases**:

1. **Phase 1: Tool Caching** (Easiest, highest impact)
2. **Phase 2: Structured Metrics Extraction**
3. **Phase 3: Qualitative Insights Structuring**
4. **Phase 4: Synthesis Optimization**

Each phase can be implemented independently and tested before proceeding to the next.

---

## Phase 1: Tool Caching (START HERE)

### Goal
Store all tool outputs to avoid redundant API calls in synthesis stage.

### Expected Impact
- ✅ Eliminate 9 redundant tool calls in Stage 3 (synthesis)
- ✅ 31% reduction in total tool calls (29 → 20)
- ✅ 31% cost reduction
- ✅ 40% faster synthesis

### Implementation Steps

#### Step 1.1: Add tool_cache to agent state

**File:** `src/agent/buffett_agent.py`

**Location:** In `__init__` method (around line 150)

```python
def __init__(self, ...):
    # ... existing code ...

    # Phase 7.7: Tool caching to avoid redundant calls
    self.tool_cache = {
        "gurufocus": {},      # GuruFocus API responses
        "sec": {},            # SEC filing texts
        "web_search": {},     # Web search results
        "calculator": {}      # Calculator outputs
    }
    logger.info("Phase 7.7 tool caching enabled")
```

#### Step 1.2: Update tool execution to cache results

**File:** `src/agent/buffett_agent.py`

**Location:** In `_execute_tool` method (around lines 500-800)

**Current code:**
```python
def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a tool and return result."""
    if tool_name == "gurufocus_tool":
        result = self.gurufocus_tool.fetch_data(...)
        return json.dumps(result, indent=2)
    # ... other tools ...
```

**Updated code:**
```python
def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a tool and return result."""
    # Phase 7.7: Check cache first
    cache_key = self._get_cache_key(tool_name, parameters)
    if cache_key in self._get_tool_cache_for_type(tool_name):
        logger.info(f"[CACHE HIT] Using cached result for {tool_name}")
        cached_result = self._get_tool_cache_for_type(tool_name)[cache_key]
        return json.dumps(cached_result, indent=2)

    # Execute tool
    if tool_name == "gurufocus_tool":
        result = self.gurufocus_tool.fetch_data(...)
        # Cache the result
        self._cache_tool_result(tool_name, cache_key, result)
        return json.dumps(result, indent=2)
    # ... other tools ...
```

#### Step 1.3: Add caching helper methods

**File:** `src/agent/buffett_agent.py`

**Location:** After `_execute_tool` method

```python
def _get_cache_key(self, tool_name: str, parameters: Dict[str, Any]) -> str:
    """
    Generate cache key from tool name and parameters.

    Example: gurufocus_tool(ticker=AOS, endpoint=summary) -> "AOS_summary"
    """
    if tool_name == "gurufocus_tool":
        ticker = parameters.get("ticker", "")
        endpoint = parameters.get("endpoint", "")
        return f"{ticker}_{endpoint}"

    elif tool_name == "sec_filing_tool":
        ticker = parameters.get("ticker", "")
        filing_type = parameters.get("filing_type", "")
        year = parameters.get("year", "")
        section = parameters.get("section", "full")
        return f"{ticker}_{filing_type}_{year}_{section}"

    elif tool_name == "calculator_tool":
        calc_type = parameters.get("calculation", "")
        # Calculator results don't cache well (depend on input data)
        # But we store them for reference
        return f"calc_{calc_type}_{hash(str(parameters))}"

    elif tool_name == "web_search_tool":
        query = parameters.get("query", "")
        # Use first 50 chars of query as key
        return query[:50]

    else:
        # Default: hash of parameters
        return f"{tool_name}_{hash(str(parameters))}"


def _get_tool_cache_for_type(self, tool_name: str) -> Dict[str, Any]:
    """Get the appropriate cache dict for this tool type."""
    if tool_name == "gurufocus_tool":
        return self.tool_cache["gurufocus"]
    elif tool_name == "sec_filing_tool":
        return self.tool_cache["sec"]
    elif tool_name == "web_search_tool":
        return self.tool_cache["web_search"]
    elif tool_name == "calculator_tool":
        return self.tool_cache["calculator"]
    else:
        # Unknown tool - create cache on the fly
        if tool_name not in self.tool_cache:
            self.tool_cache[tool_name] = {}
        return self.tool_cache[tool_name]


def _cache_tool_result(self, tool_name: str, cache_key: str, result: Any):
    """Store tool result in cache."""
    cache = self._get_tool_cache_for_type(tool_name)
    cache[cache_key] = result
    logger.debug(f"[CACHE STORE] Cached {tool_name} result: {cache_key}")
```

#### Step 1.4: Test tool caching

**Run a test analysis:**

```bash
python -c "
from src.agent.buffett_agent import WarrenBuffettAgent

agent = WarrenBuffettAgent(model_key='kimi-k2-thinking')
result = agent.analyze_company('AOS', deep_dive=True, years=5)
"
```

**Look for in logs:**
```
INFO: [CACHE HIT] Using cached result for gurufocus_tool
INFO: [CACHE HIT] Using cached result for sec_filing_tool
```

**Expected behavior:**
- Stage 1 (current year): 8 tool calls → 8 cache stores
- Stage 2 (prior years): 12 tool calls → 12 cache stores
- Stage 3 (synthesis): 0 tool calls (9 cache hits!)

**Success criteria:**
- ✅ Synthesis makes 0 actual API calls
- ✅ Logs show `[CACHE HIT]` messages
- ✅ Final thesis quality unchanged (validation score ≥80)

---

## Phase 2: Structured Metrics Extraction

### Goal
Extract quantitative metrics into `AnalysisMetrics` structure during Stage 1 and Stage 2.

### Expected Impact
- ✅ Synthesis can build trend tables instantly (no text parsing)
- ✅ Better data consistency across stages
- ✅ Easier validation (programmatic checks)

### Implementation Steps

#### Step 2.1: Import data structures

**File:** `src/agent/buffett_agent.py`

**Location:** Top of file (imports section)

```python
from src.agent.data_structures import (
    AnalysisMetrics,
    AnalysisInsights,
    ToolCache,
    YearAnalysis,
    MultiYearAnalysis
)
from src.agent.data_extractor import (
    extract_gurufocus_metrics,
    extract_calculator_metrics,
    merge_metrics,
    create_tool_cache
)
```

#### Step 2.2: Update Stage 1 to extract metrics

**File:** `src/agent/buffett_agent.py`

**Location:** In `_analyze_current_year` method (around lines 1200-1800)

**Current code:**
```python
def _analyze_current_year(self, ticker: str) -> str:
    """Analyze current year and return text analysis."""
    # ... tool calls ...
    # ... LLM analysis ...
    return analysis_text
```

**Updated code:**
```python
def _analyze_current_year(self, ticker: str) -> YearAnalysis:
    """Analyze current year and return structured analysis."""
    from datetime import datetime

    # ... existing tool calls (now cached!) ...

    # Phase 7.7: Extract structured metrics from tool outputs
    gf_metrics = extract_gurufocus_metrics(
        summary=self.tool_cache["gurufocus"].get(f"{ticker}_summary"),
        financials=self.tool_cache["gurufocus"].get(f"{ticker}_financials"),
        keyratios=self.tool_cache["gurufocus"].get(f"{ticker}_keyratios")
    )

    calc_metrics = extract_calculator_metrics(
        self.tool_cache["calculator"]
    )

    # Merge all metrics
    combined_metrics = merge_metrics(gf_metrics, calc_metrics)

    # Create tool cache object
    tool_cache = create_tool_cache(
        gurufocus_summary=self.tool_cache["gurufocus"].get(f"{ticker}_summary"),
        gurufocus_financials=self.tool_cache["gurufocus"].get(f"{ticker}_financials"),
        gurufocus_keyratios=self.tool_cache["gurufocus"].get(f"{ticker}_keyratios"),
        sec_10k_full=self.tool_cache["sec"].get(f"{ticker}_10-K_{datetime.now().year}_full"),
        calculator_outputs=self.tool_cache["calculator"]
    )

    # ... existing LLM analysis (still generate text) ...
    analysis_text = self.llm.provider.run_react_loop(...)

    # Create structured YearAnalysis object
    year_analysis = YearAnalysis(
        year=datetime.now().year,
        ticker=ticker,
        metrics=combined_metrics,
        insights=AnalysisInsights(),  # Will be populated in Phase 3
        tool_cache=tool_cache,
        full_analysis=analysis_text,  # Keep text for backward compatibility
        analysis_date=datetime.now().isoformat(),
        model_used=self.llm.model_key
    )

    logger.info(f"Extracted metrics: ROIC={combined_metrics.roic}, Revenue=${combined_metrics.revenue:,.0f}")

    return year_analysis
```

#### Step 2.3: Update Stage 2 similarly

**File:** `src/agent/buffett_agent.py`

**Location:** In `_analyze_prior_years` method

Follow same pattern as Stage 1 - return `List[YearAnalysis]` instead of text summaries.

#### Step 2.4: Update analyze_company to handle new structure

**File:** `src/agent/buffett_agent.py`

**Location:** Main `analyze_company` method

```python
def analyze_company(self, ticker: str, deep_dive: bool = False, years: int = 5):
    """Analyze company and return investment thesis."""

    # Stage 1: Current year (returns YearAnalysis)
    current_year = self._analyze_current_year(ticker)

    # Stage 2: Prior years (returns List[YearAnalysis])
    prior_years = []
    if deep_dive and years > 1:
        prior_years = self._analyze_prior_years(ticker, years - 1)

    # Stage 3: Synthesis (uses structured data)
    synthesis = self._generate_synthesis(current_year, prior_years, ticker)

    # Create MultiYearAnalysis object
    multi_year_analysis = MultiYearAnalysis(
        ticker=ticker,
        current_year=current_year,
        prior_years=prior_years,
        synthesis=synthesis,
        total_years_analyzed=len(prior_years) + 1,
        analysis_type="deep_dive" if deep_dive else "quick_screen"
    )

    # Validation (if enabled)
    if self.enable_validation:
        # Validator can access multi_year_analysis.current_year.metrics
        # for programmatic validation
        validated = self._validate_analysis(multi_year_analysis)
        return validated

    return multi_year_analysis
```

---

## Phase 3: Qualitative Insights Structuring

### Goal
Organize qualitative insights (moat, management, risks) into `AnalysisInsights` structure.

### Implementation Steps

#### Step 3.1: Update prompts to request structured output

**File:** `src/agent/buffett_prompt.py`

**Location:** In each phase's instructions

**Example for Phase 3 (Moat Assessment):**

```python
## Phase 3: Economic Moat Assessment

After your analysis, provide your assessment in this format:

**Moat Rating:** STRONG | MODERATE | WEAK

**Brand Power:**
[Your narrative assessment of brand strength]

**Moat Sources:**
- brand_power
- switching_costs
[List applicable moat types]

**Moat Durability:**
[Will this moat last 10+ years? Explain.]
```

#### Step 3.2: Parse structured insights from analysis text

**File:** `src/agent/buffett_agent.py`

**Location:** New helper method

```python
def _extract_insights_from_text(self, analysis_text: str, year: int) -> AnalysisInsights:
    """
    Extract structured insights from analysis text.

    Uses regex or simple parsing to find structured sections.
    """
    insights = AnalysisInsights()

    # Parse moat rating
    import re
    moat_match = re.search(r'\*\*Moat Rating:\*\* (STRONG|MODERATE|WEAK)', analysis_text)
    if moat_match:
        insights.moat_rating = moat_match.group(1)

    # Parse decision
    decision_match = re.search(r'\*\*DECISION: (BUY|WATCH|AVOID)\*\*', analysis_text)
    if decision_match:
        insights.decision = decision_match.group(1)

    # Parse conviction
    conviction_match = re.search(r'\*\*CONVICTION: (HIGH|MODERATE|LOW)\*\*', analysis_text)
    if conviction_match:
        insights.conviction = conviction_match.group(1)

    # Extract narrative sections using markers
    # (This is simplified - production version would be more robust)

    # For now, keep full_analysis and extract key fields
    # Future: Could use LLM to extract structured data from unstructured text

    return insights
```

---

## Phase 4: Synthesis Optimization

### Goal
Rewrite synthesis to use cached structured data instead of re-fetching from tools.

### Implementation Steps

#### Step 4.1: Update synthesis prompt

**File:** `src/agent/buffett_agent.py`

**Location:** In `_generate_synthesis` method (around lines 2200-2800)

**Current code:**
```python
def _generate_synthesis(self, current_analysis: str, prior_summaries: List[str], ticker: str):
    """Generate synthesis - currently re-calls tools."""
    # ... makes 9 tool calls ...
    # ... generates synthesis ...
```

**Updated code:**
```python
def _generate_synthesis(
    self,
    current_year: YearAnalysis,
    prior_years: List[YearAnalysis],
    ticker: str
) -> str:
    """
    Generate synthesis using cached structured data.

    Phase 7.7: NO tool calls - all data from cache.
    """

    # Build 7-year metrics tables from structured data
    years_list = [current_year] + prior_years
    revenue_data = [(y.year, y.metrics.revenue) for y in years_list if y.metrics.revenue]
    roic_data = [(y.year, y.metrics.roic) for y in years_list if y.metrics.roic]

    # Calculate trends
    revenue_cagr = self._calculate_cagr([r[1] for r in revenue_data])
    roic_avg = sum(r[1] for r in roic_data) / len(roic_data) if roic_data else None

    # Build synthesis prompt with PRE-CALCULATED data
    synthesis_prompt = f"""
    You've completed a {len(years_list)}-year analysis of {ticker}.

    **PRE-CALCULATED FINANCIAL TRENDS:**

    Revenue Trend (CAGR: {revenue_cagr:.1%}):
    {self._format_metric_table(revenue_data, "Revenue")}

    ROIC Trend (Avg: {roic_avg:.1%}):
    {self._format_metric_table(roic_data, "ROIC")}

    **CURRENT VALUATION (from calculations):**
    - Intrinsic Value: ${current_year.metrics.dcf_intrinsic_value:.2f}
    - Current Price: ${current_year.metrics.current_price:.2f}
    - Margin of Safety: {current_year.metrics.margin_of_safety:.1%}

    **MOAT ASSESSMENT:**
    {current_year.insights.moat_rating}: {current_year.insights.moat_durability}

    **MANAGEMENT QUALITY:**
    {current_year.insights.management_assessment}

    **RISKS:**
    {', '.join(current_year.insights.primary_risks)}

    Now synthesize this into a concise Warren Buffett-style investment thesis.
    Focus on TRENDS and INSIGHTS, not repeating all the data above.

    [... rest of synthesis instructions from buffett_agent.py lines 1407-1582 ...]
    """

    # Generate synthesis - NO tool calls!
    logger.info("Generating synthesis from cached structured data (0 tool calls)")
    synthesis_result = self.llm.provider.run_react_loop(
        system_prompt=get_buffett_personality_prompt(),
        initial_message=synthesis_prompt,
        tools=[],  # NO TOOLS! All data pre-provided
        tool_executor=None,
        max_iterations=1,  # Just one response, no tool calling
        max_tokens=32000
    )

    return synthesis_result["response"]


def _format_metric_table(self, data: List[tuple], metric_name: str) -> str:
    """Format metric data as ASCII table."""
    if not data:
        return "No data available"

    lines = [f"Year    {metric_name}"]
    lines.append("-" * 30)
    for year, value in sorted(data, reverse=True):  # Most recent first
        if metric_name.endswith("%") or "ROIC" in metric_name:
            lines.append(f"{year}    {value:.1%}")
        else:
            lines.append(f"{year}    ${value:,.0f}")

    return "\n".join(lines)


def _calculate_cagr(self, values: List[float]) -> float:
    """Calculate Compound Annual Growth Rate."""
    if len(values) < 2:
        return 0.0

    first = values[-1]  # Oldest
    last = values[0]    # Newest
    years = len(values) - 1

    if first <= 0:
        return 0.0

    cagr = (last / first) ** (1 / years) - 1
    return cagr
```

#### Step 4.2: Verify synthesis makes 0 tool calls

**Test:**
```bash
# Run analysis with verbose logging
export LOG_LEVEL=DEBUG
python test_full_analysis.py
```

**Look for:**
```
INFO: Generating synthesis from cached structured data (0 tool calls)
DEBUG: Synthesis prompt size: 15,234 characters
INFO: Synthesis complete: BUY with HIGH conviction
```

**Should NOT see:**
```
INFO: Calling gurufocus_tool...  # BAD - synthesis shouldn't call tools!
```

---

## Testing Checklist

### Phase 1 Tests (Tool Caching)
- [ ] Stage 1 caches all tool outputs
- [ ] Stage 2 caches all tool outputs
- [ ] Stage 3 makes 0 API calls (9 cache hits)
- [ ] Total tool calls reduced from 29 to 20
- [ ] Final thesis quality unchanged (validation score ≥80)

### Phase 2 Tests (Structured Metrics)
- [ ] `current_year.metrics.roic` populated correctly
- [ ] `current_year.metrics.revenue` populated correctly
- [ ] Trend tables show correct 7-year data
- [ ] Validator can access metrics programmatically

### Phase 3 Tests (Qualitative Insights)
- [ ] `current_year.insights.moat_rating` extracted
- [ ] `current_year.insights.decision` extracted
- [ ] Insights match original text analysis

### Phase 4 Tests (Synthesis Optimization)
- [ ] Synthesis generates complete thesis
- [ ] Synthesis makes 0 tool calls
- [ ] Synthesis completes faster (measure time)
- [ ] Validation score maintained (≥80)

---

## Rollback Plan

If any phase breaks functionality:

1. **Feature flag approach:**
   ```python
   USE_PHASE_7_7 = os.getenv("USE_PHASE_7_7", "false").lower() == "true"

   if USE_PHASE_7_7:
       # New code path
       current_year = self._analyze_current_year_structured(ticker)
   else:
       # Old code path
       current_year = self._analyze_current_year_text(ticker)
   ```

2. **Git revert:**
   ```bash
   git revert <commit-hash>
   ```

3. **Gradual rollout:**
   - Deploy Phase 1 only to production
   - Monitor for 1 week
   - If stable, deploy Phase 2
   - Continue incrementally

---

## Performance Benchmarks

### Before Phase 7.7 (Baseline)
```
Ticker: AOS, Years: 5
Tool calls: 29 (8 + 12 + 9)
Time: 420 seconds
Cost: $1.75
Validation score: 80/100
```

### After Phase 7.7 (Target)
```
Ticker: AOS, Years: 5
Tool calls: 20 (8 + 12 + 0)  ✅ -31%
Time: 320 seconds             ✅ -24%
Cost: $1.25                   ✅ -29%
Validation score: 80+/100     ✅ Maintained
```

---

## Next Steps

1. ✅ Implement Phase 1 (tool caching)
2. Test Phase 1 with AOS analysis
3. If successful, implement Phase 2 (structured metrics)
4. Test Phase 2 with multiple tickers
5. Implement Phase 3 & 4 based on results
6. Deploy to production with feature flag

---

**Status:** 🚧 Implementation guide complete - ready for development
**Risk Level:** LOW (phased approach with rollback options)
**Expected Timeline:** 4 weeks for full implementation
