# Phase 7.6B.1: Context-Aware Validation

**Date:** 2025-11-11
**Status:** ✅ Complete
**Related:** [PHASE_7.6B_IMPLEMENTATION.md](./PHASE_7.6B_IMPLEMENTATION.md)

---

## Summary

Updated the Phase 7.6B Validator Agent to provide **context-aware validation** based on analysis type:
- **Quick Screen** - Relaxed requirements (no Owner Earnings/DCF required)
- **Deep Dive** - Full Buffett methodology required (all 4 calculations)
- **Sharia Screen** - Islamic compliance focus

---

## Problem Identified

User testing revealed the validator was applying **deep dive criteria** to **quick screen** analyses, resulting in inappropriately low scores.

**Example from ZTS Quick Screen:**
```
Validation Score: 45/100 ❌

Critical Issues:
- Owner Earnings not calculated ❌ (NOT required for quick screens!)
- DCF Intrinsic Value not calculated ❌ (NOT required for quick screens!)
- Margin of Safety not calculated ❌ (NOT required for quick screens!)
- No sources cited ✅ (VALID issue - sources should be cited)
- ROIC calculation not shown ✅ (VALID issue - should show calc)
```

**3 out of 5 critical issues were invalid** for quick screens.

---

## Solution Implemented

### Updated Validator Prompt Logic

**File Modified:** [`src/agent/prompts.py`](../../src/agent/prompts.py)

**Changes:**
1. Added analysis type detection:
   ```python
   is_quick_screen = "quick" in analysis_type.lower()
   is_sharia_screen = "sharia" in analysis_type.lower()
   is_deep_dive = not is_quick_screen and not is_sharia_screen
   ```

2. Created **three separate validation checklists**:
   - Quick Screen checklist (lines 105-144)
   - Sharia Screen checklist (lines 67-101)
   - Deep Dive checklist (lines 148-197)

3. Added **type-specific scoring guidance** (lines 277-324)

---

## Validation Criteria by Analysis Type

### 1. Quick Screen Validation

**REQUIRED (CRITICAL/IMPORTANT):**
- ✅ ROIC calculated or provided (with source)
- ✅ Basic valuation metric (P/E, P/B, or relative valuation)
- ✅ Financial data sourced properly
- ✅ No hallucinations
- ✅ Professional tone
- ✅ Clear screening recommendation

**NOT REQUIRED:**
- ❌ Owner Earnings calculation
- ❌ DCF Intrinsic Value calculation
- ❌ Detailed Margin of Safety
- ❌ Deep moat analysis (high-level sufficient)
- ❌ Comprehensive management evaluation

**Scoring for Quick Screens:**
```
90-100: Excellent quick screen, well-sourced, clear recommendation
80-89: Good quick screen, minor source or clarity issues
70-79: Adequate quick screen, some data quality or analysis issues
60-69: Weak quick screen, missing sources or shallow analysis
50-59: Poor quick screen, data quality problems
0-49: Unacceptable, hallucinated data or fundamental errors

NOTE: Owner Earnings, DCF, and detailed MoS calculations NOT required.
      Focus on data quality, basic metrics (ROIC, valuation), clear logic.
      Efficiency valued - don't penalize for lack of deep analysis.
```

### 2. Sharia Screen Validation

**REQUIRED (CRITICAL):**
- ✅ Business activities screened (no alcohol, gambling, pork, interest-based finance)
- ✅ Revenue breakdown analyzed (non-compliant revenue < 5%)
- ✅ Financial ratios checked:
  - Debt/Market Cap < 33%
  - Cash + Interest-bearing securities/Market Cap < 33%
  - Accounts receivable/Total assets < 45%
- ✅ Interest income/expense analyzed (< 5% of revenue)
- ✅ Sources cited for all compliance checks
- ✅ Clear pass/fail determination

**Scoring for Sharia Screens:**
```
90-100: Excellent screening, all criteria checked properly, well-sourced
80-89: Good screening, minor source or explanation issues
70-79: Adequate screening, some criteria need better verification
60-69: Weak screening, multiple criteria not properly checked
50-59: Poor screening, critical compliance checks missing
0-49: Unacceptable, fundamental screening errors or hallucinated data

CRITICAL issues include:
- Missing business activity screening
- Financial ratios not checked or hallucinated
- No sources for compliance data
- Incorrect pass/fail determination
```

### 3. Deep Dive Validation

**REQUIRED (CRITICAL):**
- ✅ Owner Earnings calculated (OCF - CapEx, NOT Net Income)
- ✅ ROIC calculated (NOPAT / Invested Capital)
- ✅ DCF Intrinsic Value calculated (with assumptions, cash flows, terminal value)
- ✅ Margin of Safety calculated
- ✅ All 4 calculations present
- ✅ calculator_tool used (not estimated)
- ✅ Financial data sourced from reliable APIs
- ✅ SEC filing data from official EDGAR
- ✅ Specific sources cited (URLs, page numbers)
- ✅ No hallucinations

**REQUIRED (IMPORTANT):**
- ✅ Competitive moat analyzed in depth
- ✅ Moat width assessed with evidence
- ✅ Management quality evaluated thoroughly
- ✅ Capital allocation track record with examples
- ✅ Financial strength analyzed (debt, coverage, FCF)
- ✅ Business predictability over multiple years
- ✅ Comprehensive investment thesis

**Scoring for Deep Dives:**
```
90-100: Excellent deep dive, all 4 calculations present, thorough analysis
80-89: Good deep dive, some important analysis gaps
70-79: Adequate deep dive, several important issues
60-69: Weak deep dive, critical calculations missing or methodology errors
50-59: Poor deep dive, multiple critical issues
0-49: Unacceptable, fundamental methodology errors or hallucinated valuations

CRITICAL issues include:
- Owner Earnings not calculated or wrong formula
- Missing any of the 4 calculations
- No sources cited for financial data
- Hallucinated valuations or financial data
```

---

## Impact on ZTS Quick Screen

**Before Update:**
```
Score: 45/100 ❌
Issues: 9 (5 critical, 3 important, 1 minor)

Critical Issues (Invalid for Quick Screen):
❌ Owner Earnings not calculated
❌ DCF not calculated
❌ Margin of Safety not calculated

Critical Issues (Valid):
✅ No sources cited
✅ ROIC calculation not shown
```

**After Update (Expected):**
```
Score: 70-75/100 ⚠️
Issues: 5 (2 critical, 3 important)

Critical Issues (Valid):
✅ No sources cited
✅ ROIC calculation not shown

Important Issues (Valid):
✅ Moat analysis needs evidence
✅ Management quality not evaluated
✅ Decision consistency (UNKNOWN vs INVESTIGATE)
```

**Note:** Still not approved (need 85+), but more accurate assessment focused on actual quick screen requirements.

---

## Testing

### Test Script Created

**File:** [`test_deep_dive_validation.py`](../../test_deep_dive_validation.py)

**Purpose:** Test deep dive analysis with full validation expectations

**Usage:**
```bash
python test_deep_dive_validation.py
```

**What it does:**
1. Runs deep dive analysis on ZTS (3 years)
2. Displays validation results
3. Shows all issues with severity and fixes
4. Returns exit code 0 if approved, 1 if not

**Expected Result:**
- Deep dive should trigger full validation requirements
- Should check for all 4 calculations
- Should require sources, thorough moat analysis, etc.

### Recommended Testing Sequence

**1. Re-run Quick Screen (Streamlit UI):**
```
Ticker: ZTS
Analysis Type: Quick Screen
Expected: Higher score (~70-80), fewer invalid critical issues
```

**2. Run Deep Dive (Test Script):**
```bash
python test_deep_dive_validation.py
```
Expected: Lower initial score if calculations missing, full Buffett methodology required

**3. Run Sharia Screen (If Available):**
```
Ticker: Any compliant stock
Analysis Type: Sharia Screen
Expected: Compliance-focused validation, different criteria
```

---

## Files Changed

### Modified Files (1)

**src/agent/prompts.py** (+~250 lines, restructured)
- Lines 35-38: Added analysis type detection
- Lines 65-144: Added quick screen and sharia screen checklists
- Lines 148-197: Preserved deep dive checklist (made explicit)
- Lines 277-329: Added type-specific scoring guidance

### Created Files (1)

**test_deep_dive_validation.py** (165 lines)
- Comprehensive deep dive test script
- Displays validation results in detail
- Color-coded issue severity
- Summary and recommendations

### Documentation (1)

**docs/phases/phase_7.6/VALIDATOR_UPDATE_7.6B.1.md** (this file)

---

## Backward Compatibility

✅ **Fully backward compatible**

- Existing code unchanged
- Validation still enabled by default
- Analysis structure unchanged
- Deep dive analyses use same criteria as before
- Only difference: Quick/Sharia screens now validated appropriately

---

## Known Limitations

1. **Still Single-Pass Validation**
   - Validator reviews once, no iterative refinement
   - Analysis returned even if not approved
   - User must manually re-run if improvements needed

2. **Analysis Type Detection**
   - Relies on `analysis_type` field in analysis dict
   - If field missing, defaults to deep dive criteria
   - Sharia screen detection looks for "sharia" in type string

3. **Scoring Adjustments**
   - Quick screens may still score lower than expected
   - Validator is still "tough" on data quality and sources
   - Even quick screens need proper citations

---

## Next Steps

### Immediate (User Testing)

1. **Re-run ZTS Quick Screen** via Streamlit UI
   - Check if validation score improves (~70-80 expected)
   - Verify only valid issues flagged (sources, ROIC calc, moat evidence)
   - Confirm no Owner Earnings/DCF/MoS complaints

2. **Run ZTS Deep Dive** via test script
   ```bash
   python test_deep_dive_validation.py
   ```
   - Check if all 4 calculations validated
   - Verify deep methodology requirements enforced
   - Assess if thorough analysis gets good score

3. **Test Sharia Screen** (if available)
   - Verify compliance-focused validation
   - Check that financial ratios validated properly
   - Confirm business activity screening checked

### Future Enhancements (Phase 7.6B.2)

1. **Iterative Refinement**
   - Re-run analysis with validator feedback
   - Multiple improvement iterations
   - Higher quality through iteration

2. **Validator Tool Calling**
   - Validator can verify calculations directly
   - Can check sources by fetching URLs
   - More accurate validation

3. **Confidence Scores**
   - Validator expresses confidence in critique
   - Low confidence triggers human review
   - Helps catch edge cases

---

## Conclusion

Phase 7.6B.1 successfully implements **context-aware validation** that adjusts expectations based on analysis type. This fixes the issue where quick screens were inappropriately penalized for not having deep dive calculations.

**Key Achievement:** Validator now correctly differentiates between:
- Quick screens (basic metrics, screening logic)
- Deep dives (full Buffett methodology, all 4 calculations)
- Sharia screens (Islamic compliance focus)

**Status:** ✅ Phase 7.6B.1 COMPLETE

**Recommendation:** Test with ZTS quick screen and deep dive to verify improvements.

---

**Implementation Date:** 2025-11-11
**Version:** 7.6B.1 (Context-aware validation)
**Files Changed:** 1 modified, 1 created
**Backward Compatible:** Yes
