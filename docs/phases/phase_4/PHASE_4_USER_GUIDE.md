# Phase 4: SEC Filing Tool - User Guide

**Quick Start Guide for Testing and Using the SEC Filing Tool**

---

## 1. Quick Start (2 Minutes)

### No Setup Required!
- ✅ No API key needed (SEC EDGAR is completely free)
- ✅ No registration required
- ✅ Just internet connection

### Verify Installation

```bash
# Test tool imports
python -c "from src.tools.sec_filing_tool import SECFilingTool; print('✅ Ready!')"
```

**Expected output:**
```
✅ Ready!
INFO:src.tools.sec_filing_tool:SEC Filing Tool initialized
```

---

## 2. Run Tests (Proof of Functionality)

```bash
# Run core functionality tests (8 tests, ~1 second)
python -m pytest tests/test_tools/test_sec_filing_simple.py -v
```

**Expected output:**
```
============================== test session starts =============================
collected 8 items

test_tool_initialization PASSED                                          [ 12%]
test_rate_limiting_interval PASSED                                       [ 25%]
test_rate_limit_enforcement PASSED                                       [ 37%]
test_input_validation_empty_ticker PASSED                                [ 50%]
test_input_validation_invalid_filing_type PASSED                         [ 62%]
test_cik_lookup_success PASSED                                           [ 75%]
test_text_cleaning PASSED                                                [ 87%]
test_error_response_format PASSED                                        [100%]

============================== 8 passed in 0.70s ==================================
```

**✅ All 8 tests passing = Tool is working correctly**

---

## 3. Run Examples (5 Real-World Scenarios)

```bash
python examples/test_sec_filing.py
```

**What you'll see:**
1. **Apple Business Description** - Extract business section from 10-K
2. **Microsoft Risk Factors** - Identify disclosed risks
3. **Coca-Cola MD&A** - Assess management transparency
4. **Tesla Latest 10-Q** - Get quarterly report
5. **Error Handling** - Graceful error messages

**Time:** ~2 minutes (each API call takes 3-7 seconds due to rate limiting)

---

## 4. Basic Usage

### Example 1: Get Apple's Business Description

```python
from src.tools.sec_filing_tool import SECFilingTool

tool = SECFilingTool()

result = tool.execute(
    ticker="AAPL",
    filing_type="10-K",
    section="business"
)

if result["success"]:
    print(f"Company: {result['data']['company_name']}")
    print(f"Filing Date: {result['data']['filing_date']}")
    print(f"\nContent:\n{result['data']['content'][:500]}")
else:
    print(f"Error: {result['error']}")
```

### Example 2: Get Risk Factors

```python
result = tool.execute(
    ticker="MSFT",
    filing_type="10-K",
    section="risk_factors"
)
```

### Example 3: Get Latest Quarterly Report

```python
result = tool.execute(
    ticker="TSLA",
    filing_type="10-Q",
    quarter=3  # Q3
)
```

---

## 5. Key Features

### Filing Types Supported
- `10-K` - Annual report (most comprehensive)
- `10-Q` - Quarterly report
- `DEF 14A` - Proxy statement (executive compensation)
- `8-K` - Current report (material events)

### Sections Available (10-K/10-Q only)
- `business` - Item 1: What company does
- `risk_factors` - Item 1A: Disclosed risks
- `mda` - Item 7: Management discussion
- `financial_statements` - Item 8: Financial statements
- `full` - Complete filing (default)

### Why Use Section Extraction?
- Full 10-K: ~200,000 characters
- Business section: ~15,000 characters
- **Token savings: 93%**

---

## 6. Rate Limiting (Important!)

**SEC Limit:** 10 requests per second maximum

**Our Implementation:** 9 requests per second (110ms between calls)

**What this means:**
- Tool automatically enforces delays
- 10 filings = ~10-15 seconds
- This is normal and required by SEC

**Do NOT:**
- Remove rate limiting
- Make concurrent requests
- Violate SEC policies (can result in IP ban)

---

## 7. Troubleshooting

### "Ticker not found"
**Cause:** Invalid ticker or company not publicly traded
**Fix:** Verify ticker on Yahoo Finance or SEC.gov

### "Filing not found"
**Cause:** Company hasn't filed that type recently
**Fix:** Try different filing type or check company's filing history

### "Section not found"
**Cause:** Non-standard filing format
**Fix:** Use `section="full"` instead

### Slow performance
**Normal:** Each filing takes 3-7 seconds due to:
- Rate limiting (required by SEC)
- Large file downloads (10-K can be 2-5 MB)
- Text processing

---

## 8. Warren Buffett Use Cases

### Circle of Competence Assessment
```python
# Extract business description
result = tool.execute(ticker="AAPL", filing_type="10-K", section="business")

# Ask: "Can I explain this business in simple terms?"
# If YES → Proceed with analysis
# If NO → Pass (outside circle of competence)
```

### Risk Assessment
```python
# Extract risk factors
result = tool.execute(ticker="AAPL", filing_type="10-K", section="risk_factors")

# Identify: Regulatory, competitive, financial, operational risks
# Assess: Are risks manageable? Any new major risks?
```

### Management Quality
```python
# Extract MD&A
result = tool.execute(ticker="AAPL", filing_type="10-K", section="mda")

# Evaluate: Is management candid? Do they take responsibility?
# Good sign: Clear, honest communication about challenges
```

---

## 9. Integration with Other Tools

### With GuruFocus (Quantitative + Qualitative)
```python
# Step 1: Get metrics from GuruFocus
gf_result = gurufocus_tool.execute(ticker="AAPL", endpoint="keyratios")
roic = gf_result['data']['metrics']['roic']  # 31.2%

# Step 2: Validate with SEC business description
sec_result = sec_filing_tool.execute(ticker="AAPL", filing_type="10-K", section="business")

# Combined: High ROIC + strong business model = Good investment
```

### With Web Search (Cross-Reference)
```python
# Management's view (SEC)
sec_result = sec_filing_tool.execute(ticker="AAPL", filing_type="10-K", section="business")

# Market's view (Web)
ws_result = web_search_tool.execute(query="business model", company="Apple Inc")

# Compare: Does market perception match management's description?
```

---

## 10. Testing Checklist

**Basic Functionality:**
- [ ] Tool imports successfully
- [ ] 8 core tests pass
- [ ] Examples run without errors

**Manual Testing:**
- [ ] Retrieve Apple 10-K business section
- [ ] Retrieve Microsoft risk factors
- [ ] Get latest quarterly report
- [ ] Error handling works (invalid ticker)

**Performance:**
- [ ] Rate limiting works (9 req/sec)
- [ ] Each filing retrieves in 3-7 seconds
- [ ] No timeout errors

**Quality:**
- [ ] Text is clean (no HTML tags)
- [ ] Section extraction works
- [ ] Content is readable

---

## 11. Next Steps

### Phase 4 Complete ✅
All 4 tools now ready:
1. ✅ Calculator Tool
2. ✅ GuruFocus Tool
3. ✅ Web Search Tool
4. ✅ SEC Filing Tool

### Phase 5: AI Agent Integration
- Combine all 4 tools
- Implement 7-phase investigation workflow
- Add autonomous decision-making
- Create complete AI investment agent

---

## 12. Support

**Documentation:**
- Implementation: `src/tools/sec_filing_tool.py`
- Tests: `tests/test_tools/test_sec_filing_simple.py`
- Examples: `examples/test_sec_filing.py`
- Spec: `docs/tool_specs/sec_filing_tool_spec.md`

**Common Issues:**
- Rate limiting: Normal, required by SEC
- Slow downloads: Normal for large filings
- Section not found: Use `section="full"`

---

**END OF USER GUIDE**

**Status:** ✅ Ready to Use
**Time to Verify:** 5 minutes
**Next:** Run tests + examples to confirm
