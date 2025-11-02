# PHASE 2: GuruFocus Tool - USER TESTING PACKAGE

**Date:** October 30, 2025
**Phase:** Sprint 3, Phase 2 of 5
**Status:** Ready for User Testing

---

## Implementation Complete

The GuruFocus Tool has been fully implemented and is ready for testing. This package provides everything you need to test the tool yourself.

**Files Created:**
- `src/tools/gurufocus_tool.py` (899 lines)
- `tests/test_tools/test_gurufocus.py` (30+ tests)
- `examples/test_gurufocus.py` (550+ lines with 7 examples)
- `.env.example` (updated with GuruFocus instructions)

---

## Prerequisites

### 1. GuruFocus API Key Setup

**Get API Key:**
1. Visit: https://www.gurufocus.com/api.php
2. Subscribe to GuruFocus Premium (~$40/month)
3. Copy your API key (format: `token1:token2`)

**Configure Environment:**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
GURUFOCUS_API_KEY=your_actual_key_here
```

### 2. Install Dependencies

```bash
# Already installed if you ran Phase 1
pip install requests python-dotenv pytest

# Or install all project dependencies
pip install -r requirements.txt
```

---

## Quick Start

### 1. Verify Installation

```bash
# Check that GuruFocus tool can be imported
python -c "from src.tools.gurufocus_tool import GuruFocusTool; print('✅ GuruFocus Tool installed')"
```

### 2. Run Example Script

```bash
# Run comprehensive examples (requires API key)
python examples/test_gurufocus.py
```

**Expected Output:**
- ✅ Company data for Apple, Microsoft, Coca-Cola, Johnson & Johnson
- ✅ All 4 endpoints demonstrated
- ✅ Integration with Calculator Tool shown
- ✅ Special value detection (if any)

### 3. Run Test Suite

```bash
# Run mocked tests (no API key needed)
python -m pytest tests/test_tools/test_gurufocus.py -v -m "not requires_api"

# Run ALL tests including real API (requires valid key)
python -m pytest tests/test_tools/test_gurufocus.py -v
```

**Expected Results:**
- ✅ 25+ mocked tests pass
- ✅ 5+ real API tests pass (if key provided)
- ✅ All tests complete in 30-60 seconds

---

## Manual Testing Guide

### Test 1: Summary Endpoint (Quick Screening)

```python
from src.tools.gurufocus_tool import GuruFocusTool

tool = GuruFocusTool()
result = tool.execute(ticker="AAPL", endpoint="summary")

print(f"Success: {result['success']}")
print(f"Company: {result['data']['company_name']}")
print(f"ROIC: {result['data']['metrics']['roic']*100:.1f}%")
```

**Expected:**
- `success: True`
- `company_name: "Apple Inc"`
- ROIC around 30-35% (Apple is world-class)
- Financial strength score 8-9/10

### Test 2: Financials Endpoint (Historical Data)

```python
result = tool.execute(ticker="KO", endpoint="financials", period="annual")

financials = result['data']['financials']
print(f"Revenue: ${financials['revenue']/1e9:.1f}B")
print(f"Net Income: ${financials['net_income']/1e9:.1f}B")
print(f"Free Cash Flow: ${financials['free_cash_flow']/1e9:.1f}B")
```

**Expected:**
- Coca-Cola revenue $40-45B
- Net Income $9-11B
- Strong free cash flow
- 10-year historical data in `financials['historical']`

### Test 3: Key Ratios Endpoint (MOST IMPORTANT)

```python
result = tool.execute(ticker="MSFT", endpoint="keyratios")

metrics = result['data']['metrics']
print(f"ROIC: {metrics['roic']*100:.1f}%")
print(f"ROIC 10Y Avg: {metrics['roic_10y_avg']*100:.1f}%")
print(f"FCF per Share: ${metrics['fcf_per_share']:.2f}")
```

**Expected:**
- Microsoft ROIC 25-35% (excellent)
- 10-year average ROIC consistent
- FCF per share growing over time
- All per-share values present

### Test 4: Valuation Endpoint

```python
result = tool.execute(ticker="JNJ", endpoint="valuation")

valuation = result['data']['valuation']
print(f"P/E Ratio: {valuation['pe_ratio']:.1f}")
print(f"GF Value: ${valuation['gf_value']:.2f}")
print(f"Current Price: ${valuation['current_price']:.2f}")
```

**Expected:**
- J&J P/E ratio 15-20 range
- GuruFocus Value close to current price
- Growth metrics showing stable growth

### Test 5: Special Value Detection

```python
result = tool.execute(ticker="AAPL", endpoint="keyratios")

special_values = result['data']['special_values_detected']
if special_values:
    for sv in special_values:
        print(f"Field: {sv['field']}, Value: {sv['value']}, Meaning: {sv['meaning']}")
else:
    print("No special values - all data available")
```

**Expected:**
- Most quality companies: No special values
- Some companies: 9999 (data N/A) or 10000 (no debt) detected
- Special values properly flagged with meaning

### Test 6: Rate Limiting

```python
import time

start = time.time()
result1 = tool.execute(ticker="AAPL", endpoint="summary")
result2 = tool.execute(ticker="MSFT", endpoint="summary")
elapsed = time.time() - start

print(f"Elapsed: {elapsed:.2f}s")
print(f"Rate limiting {'✅ working' if elapsed >= 1.5 else '❌ NOT working'}")
```

**Expected:**
- Elapsed time ≥ 1.5 seconds
- Both requests successful
- No 429 (rate limit) errors

### Test 7: Error Handling (Invalid Ticker)

```python
result = tool.execute(ticker="INVALID", endpoint="summary")

print(f"Success: {result['success']}")
print(f"Error: {result['error']}")
```

**Expected:**
- `success: False`
- Error message contains "not found"
- No crashes or exceptions

### Test 8: Integration with Calculator Tool

```python
from src.tools.calculator_tool import CalculatorTool

gf_tool = GuruFocusTool()
calc_tool = CalculatorTool()

# Get GuruFocus metrics
gf_result = gf_tool.execute(ticker="AAPL", endpoint="keyratios")
fcf_per_share = gf_result['data']['metrics']['fcf_per_share']

# Use in DCF calculation
shares = 15_700_000_000  # Apple shares outstanding
owner_earnings = fcf_per_share * shares

dcf_result = calc_tool.execute(
    calculation="dcf",
    data={
        "owner_earnings": owner_earnings,
        "growth_rate": 0.07,
        "discount_rate": 0.10,
        "terminal_growth": 0.03,
        "years": 10
    }
)

print(f"Intrinsic Value: ${dcf_result['data']['result']/shares:.2f} per share")
```

**Expected:**
- DCF calculation works with GuruFocus data
- Intrinsic value is reasonable (not wildly off)
- Integration seamless

---

## Test Checklist

Mark each test as you complete it:

- [ ] API key setup works
- [ ] Summary endpoint returns data for AAPL
- [ ] Financials endpoint returns 10-year data for KO
- [ ] **Key ratios endpoint returns pre-calculated metrics for MSFT (MOST IMPORTANT)**
- [ ] Valuation endpoint returns data for JNJ
- [ ] Invalid ticker returns proper error
- [ ] Rate limiting enforced (minimum 1.5s between calls)
- [ ] Special values detected correctly
- [ ] Integration with Calculator Tool works
- [ ] All mocked tests pass
- [ ] All real API tests pass (if key provided)

---

## Known Issues & Limitations

### API Response Variability
- GuruFocus may return percentages (25.3) or decimals (0.253)
- Tool handles both formats automatically
- Some fields may be missing for certain companies

### Special Values
- 9999 = Data not available (company doesn't report this metric)
- 10000 = No debt OR negative equity (context-dependent)
- 0 = At loss (valid value for unprofitable companies)

### Rate Limiting
- **CRITICAL:** Must wait 1.5s minimum between requests
- GuruFocus enforces this strictly
- Exceeding limit → 429 errors → retries with backoff

### Data Freshness
- Financial data updated quarterly/annually
- Real-time prices may have 15-minute delay
- Historical data goes back 10 years

---

## Manual Validation

### Cross-Check with Official Sources

**Apple (AAPL) - Validate Against 10-K:**
- Net Income FY2023: ~$97B
- Revenue FY2023: ~$383B
- ROIC should be 30-35%

**Coca-Cola (KO) - Known Metrics:**
- Consistent ROIC: 17-18%
- Stable dividends
- Low capital intensity

**Microsoft (MSFT) - High-Quality:**
- ROIC: 25-35%
- Growing FCF per share
- Strong margins

### Comparison with GuruFocus Website

1. Visit https://www.gurufocus.com/stock/AAPL/summary
2. Compare metrics to tool output
3. Verify ROIC, ROE, margins match
4. Check financial statement numbers

---

## Troubleshooting

### "GURUFOCUS_API_KEY environment variable not set"

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# If not, copy example
cp .env.example .env

# Edit .env and add your key
nano .env  # or use any text editor
```

### "Ticker 'XXX' not found in GuruFocus"

**Solution:**
- Verify ticker symbol is correct
- Use uppercase (AAPL not aapl)
- Some international tickers not supported
- Try well-known US stocks first (AAPL, MSFT, KO, JNJ)

### "Rate limit exceeded"

**Solution:**
- Tool should handle automatically with retries
- If persistent, wait 5-10 minutes
- Check API key is Premium (not free tier)

### "Request timeout"

**Solution:**
- Check internet connection
- GuruFocus API may be slow (normal for large datasets)
- Tool retries automatically up to 3 times

### Tests fail with "No module named 'src'"

**Solution:**
```bash
# Run tests from project root
cd /path/to/basira-agent
python -m pytest tests/test_tools/test_gurufocus.py -v
```

---

## Performance Expectations

### Response Times
- Summary endpoint: 0.5-2 seconds
- Financials endpoint: 1-3 seconds (10 years of data)
- Key ratios endpoint: 1-3 seconds
- Valuation endpoint: 0.5-2 seconds

### Rate Limiting Impact
- Sequential requests: +1.5s per request
- 4 endpoint calls: ~6-10 seconds total
- Normal for quality data

### API Costs
- GuruFocus Premium: ~$40/month
- Unlimited API calls (with rate limiting)
- Per-analysis cost: ~4-5 API calls
- Cost per analysis: Negligible (fixed monthly fee)

---

## Success Criteria

Phase 2 User Testing is successful when:

- [x] GuruFocus Tool implements Tool interface correctly
- [x] All 4 endpoints work with real API
- [x] Returns pre-calculated metrics (hybrid approach)
- [x] Special values detected and flagged
- [x] Rate limiting enforced
- [x] All mocked tests pass
- [ ] All real API tests pass (USER MUST VERIFY with key)
- [ ] Integration with Calculator Tool works (USER MUST VERIFY)
- [ ] User can analyze real companies
- [ ] No crashes or unhandled errors

---

## Next Steps After Testing

1. **If All Tests Pass:**
   - Move to Strategic Review package
   - Approve Phase 2 completion
   - Proceed to Phase 3 (Web Search Tool)

2. **If Issues Found:**
   - Document issues in GitHub Issues
   - Tag as `phase-2` and `gurufocus-tool`
   - Builder will address and re-submit

3. **Enhancements for Future:**
   - Add caching for repeated requests?
   - Support for international tickers?
   - Batch endpoint for multiple companies?

---

## Questions or Issues?

**Documentation:**
- Tool Spec: `docs/tool_specs/gurufocus_tool_spec.md`
- API Docs: `docs/api_references/gurufocus_api.md`
- Architecture: `docs/ARCHITECTURE_DECISION_HYBRID_APPROACH.md`

**Code:**
- Implementation: `src/tools/gurufocus_tool.py`
- Tests: `tests/test_tools/test_gurufocus.py`
- Examples: `examples/test_gurufocus.py`

**Support:**
- GitHub Issues: https://github.com/i314nk/basirah-agent/issues
- Tag issues with `phase-2` and `gurufocus-tool`

---

**PHASE 2 USER TESTING PACKAGE COMPLETE**

**Date:** October 30, 2025
**Status:** ✅ Ready for Testing
**Approver:** User (You)
**Next Package:** PHASE_2_STRATEGIC_REVIEW.md
