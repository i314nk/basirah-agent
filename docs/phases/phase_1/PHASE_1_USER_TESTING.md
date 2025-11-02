# PHASE 1: Calculator Tool - USER TESTING PACKAGE

**Sprint:** Sprint 3, Phase 1
**Status:** COMPLETE
**Date:** 2025-10-29
**Component:** Calculator Tool

---

## Quick Start

### Installation

No external dependencies needed - the Calculator Tool is pure Python computation!

```bash
cd c:\Projects\basira-agent
```

### Run Tests

```bash
# Run all Calculator Tool tests
python -m pytest tests/test_tools/test_calculator.py -v

# Expected: All 36 tests pass
```

### Try Examples

```bash
# Run examples with real company data (Apple, Coca-Cola)
python examples/test_calculator.py

# Expected: See all 5 calculation examples with results
```

---

## What to Test

### Test 1: Basic Owner Earnings

```python
from src.tools.calculator_tool import CalculatorTool

tool = CalculatorTool()
result = tool.execute(
    calculation="owner_earnings",
    data={
        "net_income": 100_000_000,
        "depreciation_amortization": 10_000_000,
        "capex": 15_000_000,
        "working_capital_change": 5_000_000
    }
)
print(result)
```

**Expected Result:**
- `success`: True
- `result`: 90,000,000
- `result_formatted`: "$90.00M"
- `breakdown`: Step-by-step calculation with 6 steps
- `interpretation`: Quality assessment (e.g., "EXCELLENT", "GOOD", etc.)
- `warnings`: List (may be empty)

**Validation:**
- Formula: Net Income ($100M) + D&A ($10M) - CapEx ($15M) - ΔWC ($5M) = $90M ✓

### Test 2: ROIC Calculation

```python
result = tool.execute(
    calculation="roic",
    data={
        "operating_income": 50_000_000,
        "total_assets": 400_000_000,
        "current_liabilities": 50_000_000,
        "cash_equivalents": 75_000_000
    }
)
print(f"ROIC: {result['data']['result_formatted']}")
print(f"Interpretation: {result['data']['interpretation']}")
```

**Expected Result:**
- `result`: 0.1818 (18.18%)
- `result_formatted`: "18.2%"
- Invested Capital: $275M
- Interpretation: "GOOD" (meets Buffett's 15% threshold)

**Validation:**
- Invested Capital: $400M - $50M - $75M = $275M ✓
- ROIC: $50M / $275M = 18.18% ✓

### Test 3: DCF Valuation

```python
result = tool.execute(
    calculation="dcf",
    data={
        "owner_earnings": 100_000_000,
        "growth_rate": 0.07,  # 7%
        "discount_rate": 0.10,  # 10%
        "terminal_growth": 0.03,  # 3%
        "years": 10
    }
)
print(f"Intrinsic Value: {result['data']['result_formatted']}")
```

**Expected Result:**
- `result`: Should be between $1.0B and $2.5B (reasonable DCF range)
- `breakdown`: Shows DCF period value + terminal value
- `warnings`: May warn if assumptions are aggressive

**Validation:**
- Result should be a positive value ✓
- Terminal value should be present ✓
- Interpretation should mention growth rate and discount rate ✓

### Test 4: Margin of Safety

```python
result = tool.execute(
    calculation="margin_of_safety",
    data={
        "intrinsic_value": 150.00,
        "current_price": 100.00
    }
)
print(f"Margin: {result['data']['result_formatted']}")
print(f"Signal: {result['data']['interpretation']}")
```

**Expected Result:**
- `result`: 0.3333 (33.33%)
- `result_formatted`: "33.3%"
- Interpretation: "GOOD" (25-40% range for quality companies)

**Validation:**
- Formula: ($150 - $100) / $150 = 0.3333 ✓
- Should recommend BUY signal ✓

### Test 5: Sharia Compliance

```python
result = tool.execute(
    calculation="sharia_compliance_check",
    data={
        "total_debt": 50_000_000_000,
        "total_assets": 200_000_000_000,
        "cash_and_liquid_assets": 30_000_000_000,
        "market_cap": 2_000_000_000_000,
        "accounts_receivable": 60_000_000_000,
        "business_activities": ["consumer_electronics", "software"]
    }
)
print(f"Compliance: {result['data']['result_formatted']}")
```

**Expected Result:**
- `result`: 1 (compliant)
- `result_formatted`: "COMPLIANT"
- All individual checks in `breakdown` should show "PASS"

**Validation:**
- Debt/Assets: 50B / 200B = 25% < 33% ✓
- Liquid/Market Cap: 30B / 2000B = 1.5% < 33% ✓
- Receivables/Market Cap: 60B / 2000B = 3% < 50% ✓
- No prohibited activities ✓

### Test 6: Error Handling

```python
# Test missing field
result = tool.execute(
    calculation="owner_earnings",
    data={"net_income": 100_000_000}  # Missing other required fields
)
print(f"Success: {result['success']}")  # Should be False
print(f"Error: {result['error']}")      # Should mention missing field
```

**Expected Result:**
- `success`: False
- `error`: "Missing required field: 'depreciation_amortization'"

### Test 7: Unrealistic Assumptions

```python
# Test with aggressive growth rate
result = tool.execute(
    calculation="dcf",
    data={
        "owner_earnings": 100_000_000,
        "growth_rate": 0.25,  # 25% - very aggressive!
        "discount_rate": 0.10,
        "terminal_growth": 0.03,
        "years": 10
    }
)
print(f"Warnings: {result['data']['warnings']}")  # Should have warning about growth rate
```

**Expected Result:**
- `success`: True (calculation completes)
- `warnings`: Should include warning about aggressive 25% growth rate

---

## Test Checklist

Run through this checklist to verify the Calculator Tool:

- [ ] **All pytest tests pass** (36/36)
- [ ] **Example script runs without errors**
- [ ] **Owner Earnings calculates correctly** (Test 1)
- [ ] **ROIC calculates correctly** (Test 2)
- [ ] **DCF calculates correctly** (Test 3)
- [ ] **Margin of Safety calculates correctly** (Test 4)
- [ ] **Sharia Compliance checks correctly** (Test 5)
- [ ] **Error messages are clear and helpful** (Test 6)
- [ ] **Warnings appear for unrealistic inputs** (Test 7)
- [ ] **Breakdown shows step-by-step calculation**
- [ ] **Interpretation provides actionable insight**

---

## Known Issues

**None** - All tests pass and functionality is complete.

**Note on Unicode:** On Windows, you may see encoding warnings if your console doesn't support UTF-8. The calculations still work correctly, only display may be affected.

---

## Manual Validation with Real Company Data

### Apple Inc. (Buffett's Largest Holding)

**Owner Earnings (FY2022 approximation):**
```python
result = tool.execute(
    calculation="owner_earnings",
    data={
        "net_income": 99_800_000_000,
        "depreciation_amortization": 11_100_000_000,
        "capex": 10_700_000_000,
        "working_capital_change": 3_000_000_000
    }
)
# Expected Owner Earnings: $97.2B
```

**ROIC (using Apple data):**
- Expected ROIC: ~27-30% (world-class)
- Should show "WORLD-CLASS" or "EXCELLENT" interpretation

**Sharia Compliance (Apple):**
- Debt/Assets: ~31% (PASS, under 33% threshold)
- Should return COMPLIANT

### Coca-Cola (Buffett's Classic Investment)

**ROIC (approximate data):**
```python
result = tool.execute(
    calculation="roic",
    data={
        "operating_income": 10_300_000_000,
        "total_assets": 92_000_000_000,
        "current_liabilities": 23_000_000_000,
        "cash_equivalents": 9_000_000_000
    }
)
# Expected ROIC: ~17% (GOOD, meets Buffett's 15% threshold)
```

---

## Performance Verification

The Calculator Tool should be fast (pure computation, no API calls):

```python
import time

tool = CalculatorTool()
start = time.time()

for _ in range(1000):
    tool.execute(
        calculation="owner_earnings",
        data={
            "net_income": 100_000_000,
            "depreciation_amortization": 10_000_000,
            "capex": 15_000_000,
            "working_capital_change": 5_000_000
        }
    )

elapsed = time.time() - start
print(f"1000 calculations in {elapsed:.3f} seconds")
print(f"Average: {elapsed/1000*1000:.2f} milliseconds per calculation")
```

**Expected Performance:**
- 1000 calculations should complete in < 1 second
- Each calculation should take < 1 millisecond

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Make sure you're running from the project root:
```bash
cd c:\Projects\basira-agent
python -m pytest tests/test_tools/test_calculator.py
```

### Test Failures

**Problem:** Some tests fail

**Solution:** Ensure you have the latest code:
```bash
git pull  # if using git
# Or verify calculator_tool.py matches implementation
```

### Example Script Errors

**Problem:** Unicode encoding errors on Windows

**Solution:** The script includes UTF-8 handling. If issues persist, run with:
```bash
python -X utf8 examples/test_calculator.py
```

---

## Success Criteria

✅ **Phase 1 is successful if:**

1. All 36 pytest tests pass
2. Examples run without errors
3. All 5 calculation types produce correct results
4. Formulas match Buffett Principles documentation
5. Error handling catches invalid inputs
6. Warnings appear for unrealistic assumptions
7. Real company data (Apple, Coca-Cola) validates correctly
8. Performance is fast (< 1ms per calculation)

---

## Next Steps

After you've completed testing:

1. **Report any issues** you find (bugs, unclear error messages, etc.)
2. **Verify results** match your expectations for real companies
3. **Review Strategic Package** (PHASE_1_STRATEGIC_REVIEW.md) for technical details
4. **Approve Phase 1** to proceed to Phase 2 (Data adapters)

---

**USER TESTING PACKAGE COMPLETE**

Ready for user acceptance testing!
