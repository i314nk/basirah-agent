# Prompt Alignment Fix: Owner Earnings Formula

## Issue Discovered

**Date:** 2025-11-20
**Severity:** HIGH - Causes false positive validation errors
**Reported By:** User observation of validator critique

### The Problem

The **analyst prompt** and **validator prompt** had **different Owner Earnings formulas**, causing the validator to incorrectly flag properly calculated Owner Earnings as errors.

**Analyst Prompt** (buffett_prompt.py):
```
Owner Earnings = Net Income + D&A - Maintenance CapEx - ΔWorking Capital
```

**Validator Prompt** (prompts.py):
```
Owner Earnings = Net Income + D&A - CapEx - Change in Working Capital
```

**Key Difference:** "Maintenance CapEx" vs "CapEx" (total)

### Why This is Problematic

1. **False Positives:** Validator flags correct calculations as errors
2. **User Confusion:** User gets critique saying their calculation is wrong when following instructions
3. **Trust Erosion:** Undermines confidence in validation system
4. **Inconsistent Framework:** Analyst and validator use different definitions

### Example from NVO Analysis

**Validator Critique (INCORRECT):**
```
**Critical Issues:**
1. **Calculations**: Owner Earnings calculation uses incorrect formula
   (Net Income + D&A - CapEx instead of Operating Cash Flow - CapEx).
   - *Recommended fix*: Use Operating Cash Flow - CapEx
```

**Reality:** The analyst was following its prompt instructions exactly. The validator was applying a different standard.

## Root Cause Analysis

### Buffett's Owner Earnings - Multiple Valid Formulations

Warren Buffett has described Owner Earnings in different ways over time:

**1. Original Formula (1986 Berkshire Letter):**
```
Owner Earnings = Net Income + D&A + Amortization - Maintenance CapEx ± ΔWorking Capital
```

**2. Practical Approximation:**
```
Owner Earnings ≈ Operating Cash Flow - Maintenance CapEx
```

**3. Conservative Variant (Most Common in Practice):**
```
Owner Earnings ≈ Operating Cash Flow - Total CapEx  (i.e., Free Cash Flow)
```

### The Challenge: "Maintenance" vs "Growth" CapEx

The **theoretical** formula uses "Maintenance CapEx" (capital needed to maintain current operations), but:

- ❌ Not reported separately in financial statements
- ❌ Requires subjective judgment to estimate
- ❌ Different analysts will disagree on the split
- ❌ Management may not disclose their breakdown

The **practical** solution:

- ✅ Use **Total CapEx** (conservative assumption: all CapEx is necessary)
- ✅ If business is mature, most CapEx IS maintenance
- ✅ If business is growing, being conservative is prudent
- ✅ Easier to calculate, verify, and reproduce

## Solution Implemented

### Tiered Owner Earnings Approach (Smart, Adaptive)

Instead of forcing one formula, we now use a **tiered hierarchy** that prioritizes the best available data:

**Tier 1 (PREFERRED): GuruFocus Free Cash Flow**
```
Owner Earnings = GuruFocus FCF
```
- GuruFocus calculates FCF = OCF - CapEx
- Pre-verified, consistent across all companies
- 10 years of historical data available
- **Use this if available** - most reliable source

**Tier 2 (IF MAINTENANCE CAPEX IDENTIFIABLE): Original Buffett Formula**
```
Owner Earnings = Net Income + D&A - Maintenance CapEx ± ΔWorking Capital
```
- Only use if Maintenance CapEx clearly disclosed in MD&A
- Analyst must document source (e.g., "Per 2023 MD&A: $200M of $500M CapEx is maintenance")
- This is Buffett's original 1986 formula
- Honors Buffett's intent when data is available

**Tier 3 (CONSERVATIVE FALLBACK): Total CapEx**
```
Owner Earnings = Operating Cash Flow - Total CapEx
```
- Use when Maintenance CapEx cannot be identified
- Conservative: Assumes all CapEx is necessary
- Same as Free Cash Flow (common proxy)

**All three approaches are now accepted by the validator.**

### Why This Tiered Approach is Better

1. **Prioritizes Verified Data:** GuruFocus FCF is pre-calculated and verified - most reliable
2. **Honors Buffett's Intent:** If Maintenance CapEx is disclosed, use the original formula
3. **Practical Fallback:** When Maintenance CapEx unclear, use conservative Total CapEx
4. **Reduces False Positives:** Validator accepts all three valid approaches
5. **Adaptive:** Uses best available data for each company
6. **Aligned:** Analyst and validator agree on the hierarchy

### Changes Made

#### 1. Analyst Prompt ([buffett_prompt.py:198-218](../../src/agent/buffett_prompt.py#L198-L218))

**Before:**
```
Owner Earnings = Net Income + D&A - Maintenance CapEx - ΔWorking Capital
```

**After:**
```
Owner Earnings = Operating Cash Flow - Total CapEx

Alternative (if OCF not available):
Owner Earnings = Net Income + D&A - Total CapEx ± ΔWorking Capital
```

Added rationale explaining why we use Total CapEx instead of "Maintenance" CapEx.

#### 2. Validator Prompt ([prompts.py:247-251](../../src/agent/prompts.py#L247-L251))

**Before:**
```
Owner Earnings = Net Income + D&A - CapEx - Change in Working Capital
```

**After:**
```
Accept EITHER of these Buffett-approved formulas:
- Preferred: Owner Earnings = Operating Cash Flow - Total CapEx
- Alternative: Owner Earnings = Net Income + D&A - Total CapEx ± ΔWorking Capital

Both are valid. OCF - CapEx is Free Cash Flow, a widely-used proxy.
```

Added example showing both formulas are acceptable.

## Impact

### Before Fix
- ❌ Validator flags correct Owner Earnings calculations as errors
- ❌ Confusing critique: "Use OCF - CapEx" when analyst did use correct formula
- ❌ User loses trust in validation system
- ❌ Analyst and validator disagree on fundamentals

### After Fix
- ✅ Validator accepts both valid Owner Earnings formulas
- ✅ No false positives on correctly calculated Owner Earnings
- ✅ Clear documentation of why we use Total CapEx
- ✅ Analyst and validator aligned on framework

## Testing

### Manual Verification

1. **Read analyst prompt:** Confirmed new formula present
2. **Read validator prompt:** Confirmed acceptance of both formulas
3. **Check examples:** Updated to show both approaches valid

### Expected Behavior (Future Analyses)

**Scenario 1: Analyst uses OCF - CapEx**
```
Owner Earnings = $80.8B - $44.4B = $36.4B
```
✅ Validator accepts (preferred formula)

**Scenario 2: Analyst uses NI + D&A - CapEx**
```
Owner Earnings = $97.4B + $13.9B - $44.4B = $66.9B
```
✅ Validator accepts (alternative formula)

**Scenario 3: Analyst uses wrong formula (e.g., ignores CapEx)**
```
Owner Earnings = Net Income = $97.4B  (WRONG - no CapEx deduction)
```
❌ Validator correctly flags as error

## Lessons Learned

### 1. **Prompt Alignment is Critical**

When multiple agents (analyst + validator) work together, they MUST agree on:
- Definitions of key metrics
- Acceptable calculation methods
- Standards for "correctness"

### 2. **Practical > Theoretical**

The "theoretically correct" formula (using Maintenance CapEx) is impractical because:
- Not reported in financial statements
- Requires subjective estimates
- Causes analyst-validator disagreements

The "practically correct" formula (using Total CapEx) is better because:
- Easy to calculate from public data
- Conservative and defensible
- No subjective judgments needed

### 3. **Test Validator Against Analyst Instructions**

Future validation tests should include:
- Does validator accept outputs that follow analyst instructions?
- Are there any false positives (correct work flagged as incorrect)?
- Do validator critiques make sense to users?

### 4. **Document Formula Choices**

Any metric with multiple valid calculation methods should:
- Document which formula(s) are acceptable
- Explain WHY that formula was chosen
- Show example calculations
- Ensure all agents use same definition

## Related Issues

This type of prompt misalignment could affect other metrics:

### Potentially At Risk:
- **ROIC:** Multiple definitions (NOPAT / Invested Capital vs Operating Income / Invested Capital)
- **Free Cash Flow:** OCF - CapEx vs OCF - CapEx - Dividends
- **Working Capital:** Current Assets - Current Liabilities vs more complex definitions
- **Debt/Equity:** Total Debt vs Long-Term Debt only

### Action Item:
Audit all key metric definitions in both analyst and validator prompts to ensure alignment.

## References

### Warren Buffett on Owner Earnings

**1986 Berkshire Hathaway Letter:**
> "If we think through these questions, we can gain some insights about what may be called 'owner earnings.' These represent (a) reported earnings plus (b) depreciation, depletion, amortization, and certain other non-cash charges less (c) the average annual amount of capitalized expenditures for plant and equipment, etc. that the business requires to fully maintain its long-term competitive position and its unit volume."

**Key Insight:** Buffett emphasizes "maintain its long-term competitive position" → Maintenance CapEx

**Practical Reality:** Most analysts use Free Cash Flow (OCF - Total CapEx) as Owner Earnings proxy because:
1. Total CapEx is observable
2. Maintenance CapEx requires estimate
3. Conservative approach (assumes all CapEx is necessary)

## Status

✅ **Fixed** - Prompts now aligned
✅ **Documented** - This file explains the issue and solution
⏳ **Pending Verification** - Will verify in next production analysis

---

**Implementation Date:** 2025-11-20
**Files Changed:**
- `src/agent/buffett_prompt.py` (lines 198-242) - Tiered approach with decision tree
- `src/agent/prompts.py` (lines 247-292) - Validator accepts all three approaches

---

## Update: Tiered Approach (User-Suggested Improvement)

**Suggested By:** User
**Date:** 2025-11-20

The initial fix used a single "OCF - Total CapEx" formula. The user correctly pointed out a smarter approach:

> "If Warren Buffett agent is able to find maintenance capex from MD&A in 10k filings it should use original formula. If not, it can simply use OCF - Capex. Even better, GuruFocus should have Owner Earnings available or Owner Earnings per share, if not then simply use FCF from GuruFocus."

This led to the **tiered hierarchy** implementation:
1. **Tier 1:** GuruFocus FCF (preferred - most reliable)
2. **Tier 2:** NI + D&A - Maintenance CapEx (if identifiable from MD&A)
3. **Tier 3:** OCF - Total CapEx (conservative fallback)

### Benefits of Tiered Approach

- ✅ **Adaptive:** Uses best available data for each company
- ✅ **Honors Buffett's Original Intent:** Uses Maintenance CapEx when disclosed
- ✅ **Prioritizes Verified Data:** GuruFocus FCF is pre-calculated and consistent
- ✅ **Conservative Fallback:** Total CapEx when Maintenance CapEx unclear
- ✅ **Eliminates False Positives:** Validator accepts all three valid approaches
- ✅ **Encourages Best Practices:** Analyst prefers GuruFocus FCF (most reliable)

This is a **significantly better** approach than forcing a single formula, and it better reflects how professional investors actually analyze Owner Earnings in practice.
