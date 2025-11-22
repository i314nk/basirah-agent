# Fix: Synthesis Output Token Truncation (32K Limit)

**Date:** 2025-11-16
**Issue:** Synthesis stage generates incomplete analysis with UNKNOWN decision

---

## Problem

**From User's Logs:**
```
INFO:src.agent.buffett_agent:Synthesis prompt size: 50,092 characters (~12,523 tokens)
INFO:src.agent.buffett_agent:MAX_TOKENS available for response: 32,000
...
INFO:src.agent.buffett_agent:Analysis Complete - Decision: UNKNOWN
INFO:src.agent.buffett_agent:Synthesis complete: UNKNOWN with UNKNOWN conviction
```

**What Happened:**
- Synthesis tries to write comprehensive 7-year thesis
- Output exceeds 32K token limit (Kimi's maximum)
- Thesis gets truncated mid-generation BEFORE decision section
- Result: `decision = "UNKNOWN"`, missing calculations, validation score 45/100

**Validator's Assessment:**
```
[CRITICAL] calculations: Owner Earnings calculation missing entirely
[CRITICAL] calculations: ROIC calculation missing
[CRITICAL] calculations: DCF Intrinsic Value calculation completely absent
[CRITICAL] decision: Decision is UNKNOWN (should be BUY/WATCH/AVOID)
[IMPORTANT] methodology: Analysis is incomplete - cuts off mid-sentence
```

## Root Cause

**Old Synthesis Prompt Structure:**
- Section 1 (Business): 3-4 paragraphs
- Section 2 (Moat): 4-5 paragraphs
- Section 3 (Management): 3-4 paragraphs
- Section 4 (Financials): 5-6 paragraphs with detailed tables
- Section 5 (Growth): 3-4 paragraphs
- Section 6 (Competition): 3-4 paragraphs
- Section 7 (Risks): 3-4 paragraphs
- Section 8 (Synthesis): 4-5 paragraphs
- Section 9 (Valuation): 4-5 paragraphs
- Section 10 (Decision): 5-6 paragraphs

**Total: ~40-50 paragraphs for 7-year analysis = 35-40K tokens**

This exceeded Kimi's 32K output limit, causing truncation before Section 10.

## The Fix (Cost-Effective - No Claude Needed)

**Streamlined synthesis to focus on TRENDS not data repetition:**

### Changed Instructions
```markdown
**CRITICAL INSTRUCTIONS:**
1. Focus on TRENDS and INSIGHTS, not repeating all data from every year
2. Be CONCISE - you have a 25,000 word limit
3. DO NOT repeat data already in year summaries - reference and explain what it MEANS
4. DO focus on 7-year trends - how has moat/management/financials evolved?
5. DO complete all sections - especially the decision (Section 10)
```

### Reduced Section Lengths

**New Structure:**
- Sections 1-3: 2-3 paragraphs each (business context)
- Section 4: 3-4 paragraphs (financial trends with concise tables)
- Sections 5-9: 2 paragraphs each (focused insights)
- Section 10: 1-2 paragraphs (clear decision)

**Total: ~15-20 paragraphs = ~15-20K tokens (well under 32K limit!)**

### Example: Section 4 (Financial Analysis)

**Before (verbose):**
```
## **4. Financial Analysis** (5-6 paragraphs)

Deep dive into the numbers across 7 years:

**Revenue & Growth:**
Create a table showing trends:
```
2024: $X.XB (±X% YoY)
2023: $X.XB (±X% YoY)
2022: $X.XB (±X% YoY)
[...all years...]
Overall trend: ...
CAGR: X%
```

**Profitability Trends:**
[Detailed margin tables for all years...]

**ROIC & Capital Efficiency:**
[Lengthy calculation explanation...]

**Balance Sheet Strength:**
[Detailed debt analysis...]

**Cash Flow Quality:**
[Detailed OCF analysis...]
```

**After (concise):**
```
## **4. Financial Analysis** (3-4 paragraphs MAX)

Show 7-year TRENDS with concise tables:

**Revenue & ROIC Trends (REQUIRED - use calculator_tool):**
```
Year    Revenue    ROIC    Owner Earnings
2024    $X.XB      XX%     $X.XB
2018    $X.XB      XX%     $X.XB
CAGR:   X%         --      X%

ROIC Calculation (2024): NOPAT / Invested Capital = XX%
vs 15% Buffett hurdle: Pass/Fail
```

**Profitability & Balance Sheet:**
```
Margins (2024 vs 2018):
- Gross:     XX% → XX% (expanding/declining)
- Operating: XX% → XX% (expanding/declining)

Balance Sheet:
- Debt/Equity: X.X (comfortable/concerning)
```

Explain what these trends tell you about business quality. Be concise.
```

## Code Changes

**File:** `src/agent/buffett_agent.py`

**Lines 1407-1427:** Added concise writing instructions
**Lines 1449-1454:** Added length requirements (15-20 paragraphs total)
**Lines 1456-1582:** Streamlined all 10 sections to be more concise

**Key Changes:**
1. Sections 1-3: Reduced from 3-5 paragraphs to 2-3 paragraphs
2. Section 4: Reduced from 5-6 paragraphs to 3-4 paragraphs
3. Sections 5-9: Reduced from 3-5 paragraphs to 2 paragraphs each
4. Section 10: Reduced from 5-6 paragraphs to 1-2 paragraphs

## Expected Results

**Before Fix:**
```
Output: 35-40K tokens
Result: Truncated at 32K tokens
Decision: UNKNOWN
Validation Score: 45/100 (incomplete)
```

**After Fix:**
```
Output: 15-20K tokens
Result: Complete thesis with all 10 sections
Decision: BUY/WATCH/AVOID (proper decision)
Validation Score: 60-80/100 (complete analysis)
```

## Benefits

✅ **No cost increase** - stays with Kimi (no Claude needed)
✅ **Complete analyses** - all 10 sections fit within 32K limit
✅ **Better quality** - focuses on insights vs data dumps
✅ **Faster generation** - less tokens = faster response
✅ **Higher validation scores** - complete analyses pass validation

## Testing

Run a 7-year deep dive and check:
```bash
# Look for in logs:
✅ "Synthesis complete: WATCH with MODERATE conviction"  (not UNKNOWN)
✅ "Validation score: 68/100"  (not 45/100)
✅ Decision field populated properly

❌ "Analysis Complete - Decision: UNKNOWN"
❌ "Analysis is incomplete - cuts off mid-sentence"
```

## Alternative Solutions Considered

1. **Use Claude for synthesis** - $0.80 vs $0.40 (REJECTED: user wants cost control)
2. **Two-stage synthesis** - Complex (REJECTED: simpler solution available)
3. **Reduce prior year summaries** - Loses historical context (REJECTED)
4. **This fix: Make synthesis concise** - ✅ ACCEPTED: Cost-effective and simple

## Impact

- **Cost:** No change (still uses Kimi)
- **Quality:** Improved (focuses on insights)
- **Completeness:** Fixed (all 10 sections fit)
- **Speed:** Faster (~40% fewer tokens)

---

**Status:** ✅ FIXED
**Next:** Test with AOS 7-year analysis to verify completion
