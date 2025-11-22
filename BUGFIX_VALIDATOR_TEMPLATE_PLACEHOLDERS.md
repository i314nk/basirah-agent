# CRITICAL BUG FIX: Validator Receiving Template Placeholders

**Date:** November 18, 2025
**Status:** ✅ FIXED
**Severity:** CRITICAL (Validator scoring 0/100)
**Impact:** Validator was receiving literal template strings instead of actual analysis data

---

## Bug Description

### Symptoms

The validator was receiving template placeholder strings like `{analysis_json}` instead of actual analysis content, causing:

- Validator scoring 0/100 on all analyses
- Error message: "Missing analysis content. The submission contains template placeholders instead of the actual analysis document"
- Validator unable to access ticker symbol, decision, or analysis content
- Complete failure of the validator-driven refinement loop

### User Report

From validator logs:
```
[CRITICAL] data: Missing analysis content. The submission contains template
placeholders instead of the actual analysis document. No ticker symbol,
analysis type, decision, or analysis content was provided in the {analysis_json} field.
```

---

## Root Cause

**File:** [src/agent/prompts.py](src/agent/prompts.py)

### Line 255 (CRITICAL)

```python
# BEFORE (BROKEN):
prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS TO REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticker: {ticker}
Analysis Type: {analysis_type}
Decision: {decision}

Full Analysis:
{analysis_json}
"""
```

**Problem:** The triple-quoted string was **NOT** an f-string, so placeholders like `{ticker}`, `{analysis_type}`, `{decision}`, and `{analysis_json}` were being sent as **literal text** to the validator instead of being replaced with actual values.

### Line 497 (CRITICAL)

```python
# BEFORE (BROKEN):
prompt += """
...
SCORING GUIDE ({analysis_type.upper()}):"""
```

**Problem:** Same issue - `{analysis_type.upper()}` was sent as literal text.

---

## The Fix

### Changes Made

**File:** [src/agent/prompts.py](src/agent/prompts.py)

**Line 255:**
```python
# AFTER (FIXED):
prompt += f"""  # <-- Added 'f' prefix
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS TO REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticker: {ticker}
Analysis Type: {analysis_type}
Decision: {decision}

Full Analysis:
{analysis_json}
"""
```

**Line 497:**
```python
# AFTER (FIXED):
prompt += f"""  # <-- Added 'f' prefix
...
SCORING GUIDE ({analysis_type.upper()}):"""
```

### What Changed

1. **Line 255:** Added `f` prefix to make it an f-string
2. **Line 497:** Added `f` prefix to make it an f-string
3. Now placeholders are correctly replaced with actual values:
   - `{ticker}` → `"AAPL"` (actual ticker)
   - `{analysis_type}` → `"deep_dive"` (actual analysis type)
   - `{decision}` → `"BUY"` (actual decision)
   - `{analysis_json}` → `{...actual JSON...}` (full analysis dict as JSON)

---

## Testing

### Test File

**File:** [test_validator_template_fix.py](test_validator_template_fix.py)

### Test Results

```bash
$ python test_validator_template_fix.py

================================================================================
TEST SUMMARY
================================================================================
[PASS] - Validator Prompt Formatting
[PASS] - Structured Validation Integration

Total: 2/2 tests passed

*** All validator template fix tests PASSED!
[OK] Validator receives actual analysis content
[OK] Template placeholders correctly replaced

CRITICAL BUG FIXED:
  Before: Validator received '{analysis_json}' literal text
  After:  Validator receives actual JSON analysis data
```

### Verification Checks

✅ No `{ticker}` placeholder in validator prompt
✅ No `{analysis_type}` placeholder in validator prompt
✅ No `{decision}` placeholder in validator prompt
✅ No `{analysis_json}` placeholder in validator prompt
✅ Ticker value present: `"Ticker: AAPL"`
✅ Decision value present: `"Decision: BUY"`
✅ Analysis Type present: `"Analysis Type: deep_dive"`
✅ Analysis JSON embedded in prompt

---

## Impact Analysis

### Before Fix

❌ Validator received literal template placeholders
❌ Validator scored 0/100 on all analyses
❌ Validator-driven refinement loop completely broken
❌ No access to analysis content for critique
❌ Critical errors about missing data

### After Fix

✅ Validator receives actual analysis content
✅ Validator can properly score analyses
✅ Validator-driven refinement loop functional
✅ Full access to ticker, decision, and analysis JSON
✅ Automated validation results properly integrated

---

## Related Issues Fixed

This same fix also resolved:

1. **Pydantic Validation Errors** in `_extract_insights_from_analysis()`:
   - `integrity_evidence` type mismatch (string → List[str])
   - `primary_risks` length violation (9 items → max 8)

   **File:** [src/agent/buffett_agent.py](src/agent/buffett_agent.py) lines 2860-2882

---

## Prevention

### Code Review Checklist

When working with Python f-strings:

1. ✅ **Always use `f"""` for strings with placeholders** like `{variable}`
2. ✅ **Never use plain `"""` if the string contains `{...}` placeholders**
3. ✅ **Test template formatting with actual data** before deployment
4. ✅ **Look for literal `{...}` in LLM prompts** as a red flag

### Example

```python
# ❌ WRONG (will output literal {ticker}):
prompt = """
Ticker: {ticker}
"""

# ✅ CORRECT (will output actual ticker value):
prompt = f"""
Ticker: {ticker}
"""
```

---

## Lessons Learned

1. **Python f-string prefix is critical** - Missing the `f` prefix causes silent failures where placeholders are sent as literal text
2. **Test LLM prompts with actual data** - The bug was hidden because the prompt still looked reasonable in code, but was broken at runtime
3. **Validator logs are invaluable** - User's validator logs immediately revealed the issue with template placeholders
4. **Windows Unicode issues** - Remember to use ASCII characters in test output for Windows terminal compatibility

---

## Files Changed

| File | Lines | Change | Status |
|------|-------|--------|--------|
| [src/agent/prompts.py](src/agent/prompts.py#L255) | 255 | Added `f` prefix to format string | ✅ Fixed |
| [src/agent/prompts.py](src/agent/prompts.py#L497) | 497 | Added `f` prefix to format string | ✅ Fixed |
| [src/agent/buffett_agent.py](src/agent/buffett_agent.py#L2860-L2882) | 2860-2882 | Fixed Pydantic validation errors | ✅ Fixed |
| [test_validator_template_fix.py](test_validator_template_fix.py) | New | Test suite for validator template fix | ✅ Created |
| [BUGFIX_VALIDATOR_TEMPLATE_PLACEHOLDERS.md](BUGFIX_VALIDATOR_TEMPLATE_PLACEHOLDERS.md) | New | Documentation | ✅ Created |

---

## Quick Test Command

```bash
# Test the fix
python test_validator_template_fix.py

# Should output:
# [PASS] - Validator Prompt Formatting
# [PASS] - Structured Validation Integration
# Total: 2/2 tests passed
```

---

## Conclusion

**Bug Status:** ✅ FIXED
**Tests Status:** ✅ 2/2 PASSED
**Production Impact:** CRITICAL bug that completely broke validator-driven refinement
**Resolution:** Simple 2-character fix (`f` prefix) with major impact

The validator now receives actual analysis content instead of template placeholders, enabling proper scoring and critique of investment analyses.

---

**Date Fixed:** November 18, 2025
**Fixed By:** Claude Code (AI Assistant)
**Reported By:** User (via validator logs)
**Time to Fix:** ~30 minutes from bug report to fix + tests + documentation
