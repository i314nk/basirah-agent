# Phase 7.6C: Iterative Refinement & Buffett Principles Enforcement

**Date:** 2025-11-13
**Status:** ✅ Complete
**Related:** [PHASE_7.6B.2_IMPROVEMENTS.md](./PHASE_7.6B.2_IMPROVEMENTS.md), [BUFFETT_PRINCIPLES.md](../../BUFFETT_PRINCIPLES.md)

---

## Summary

Phase 7.6C implements two major quality improvements:

1. **Enhanced Synthesis Prompts** - Stricter requirements aligned with Warren Buffett's philosophy
2. **Iterative Refinement System** - Automated fix-and-revalidate loop for quality issues

**Key Innovation:** The agent now "shows its work" like Buffett would - explicit formulas, detailed citations, and the ability to self-correct when validator identifies gaps.

---

## Motivation

### Problem: Validation Issues Persist Despite Requirements

NVO 5-year deep dive test (Phase 7.6B.2.1) showed score of 75/100 with 5 legitimate issues:

1. **ROIC numbers without methodology** (CRITICAL)
2. **Citations lack specificity** (IMPORTANT)
3. **Calculator usage not evident** (IMPORTANT)
4. **Current price too vague** (IMPORTANT)
5. **CEO replacement not researched** (MINOR)

**Root Cause:** Existing requirements were present but not specific or enforced enough.

### Solution: Two-Pronged Approach

**Part 1: Stricter Prompts** (Quick Win)
- Make requirements MORE explicit and detailed
- Add examples showing exactly what's expected
- Align with Buffett principles from [BUFFETT_PRINCIPLES.md](../../BUFFETT_PRINCIPLES.md)

**Part 2: Iterative Refinement** (Systematic Quality)
- If validation score < 80, automatically refine
- Target specific fixable issues
- Re-validate after fixes
- Repeat until score ≥ 80 or max iterations reached

---

## Part 1: Enhanced Synthesis Prompts

### Improvement #1: ROIC Calculation Methodology (CRITICAL)

**Before:**
```markdown
**ROIC & Capital Efficiency:**
ROIC trend:  2024: X%  →  [first year]: X%
Average ROIC: X% over {total_years}-year period
vs 15% hurdle: Passes / Fails
```

**After:**
```markdown
**ROIC & Capital Efficiency (REQUIRED - SHOW CALCULATION):**

CRITICAL: You MUST show ROIC calculation methodology, not just state numbers!

ROIC CALCULATION (use calculator_tool):
Formula: ROIC = NOPAT / Invested Capital

Where:
- NOPAT = Operating Income × (1 - Tax Rate)
  Operating Income (EBIT): $X.XB (Source: 10-K FY2024, Income Statement, page XX)
  Tax Rate: XX% (Source: 10-K FY2024, Income Statement, page XX)
  NOPAT = $X.XB × (1 - 0.XX) = $X.XB

- Invested Capital = Total Equity + Total Debt - Cash
  [Show all inputs with sources and calculate]

ROIC = $X.XB / $X.XB = XX.X%

Calculator Tool Output:
{Paste relevant calculator_tool output that shows ROIC calculation}
```

**Impact:** Enforces Buffett's "show your work" principle (BUFFETT_PRINCIPLES.md lines 524-551)

### Improvement #2: CEO/Management Change Research (IMPORTANT)

**Before:**
```markdown
**Management Quality:**
Evaluate the leadership team...
```

**After:**
```markdown
**Current Leadership (REQUIRED - RESEARCH ANY CHANGES):**
- Current CEO: [Name] (since [Date])
- CRITICAL: If CEO/CFO changed in past 2 years:
  * Research with web_search_tool: "[company] CEO change [name] departure"
  * Document: Who left, when, why, who replaced them
  * New CEO background: Previous role, track record, strategic focus
  * Source: [Link to announcement, press release, SEC filing]
```

**Impact:** Ensures thorough management assessment per Buffett's emphasis on management quality (BUFFETT_PRINCIPLES.md lines 263-397)

### Improvement #3: Exact Current Price (IMPORTANT)

**Before:**
```markdown
**Current Market Price:**
- Trading at: $XXX per share
```

**After:**
```markdown
**Current Market Price (REQUIRED - USE WEB_SEARCH FOR EXACT PRICE):**

CRITICAL: Do NOT use price ranges like "~$70-75". Get EXACT current price!

Use web_search_tool: "[ticker] stock price today current"

Current Price: $XXX.XX per share (as of [exact date])
Source: [Web search result - specify source name]
```

**Impact:** Precision in valuation is critical to margin of safety calculation (BUFFETT_PRINCIPLES.md lines 726-932)

### Improvement #4: Detailed Citation Requirements (IMPORTANT)

**Before:**
```markdown
4. **CITE ALL SOURCES** - Every metric must include:
   - **10-K data**: "Source: 10-K FY20XX, [Section name], page XX"
```

**After:**
```markdown
4. **CITE ALL SOURCES WITH SPECIFICITY** - Detailed citations required:
   - **10-K/20-F data**: "Source: 10-K FY20XX, [Section name], page XX"
     * Examples: "Source: 10-K FY2024, Consolidated Statements of Cash Flows, page 67"
   - **Calculator tool outputs**: Reference tool output explicitly
     * Example: "ROIC calculated using calculator_tool: 17.9% (see calculation above)"
```

**Impact:** Enables verification and demonstrates rigor (Buffett principle of transparency)

---

## Part 2: Iterative Refinement System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Warren Buffett Analysis (Initial)                          │
│  - Deep dive or quick screen                                │
│  - Standard synthesis prompt with enhanced requirements     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Validation (Iteration 0)                                   │
│  - Validator reviews analysis                               │
│  - Returns score + list of issues                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ┌────────┴────────┐
            │  Score >= 80?   │
            └────────┬────────┘
                 YES │         NO
                     │         │
            ┌────────▼────┐   ▼
            │   DONE      │   ┌──────────────────────────────┐
            │  (Quality   │   │ Filter Fixable Issues        │
            │   Met)      │   │ - Remove unfixable issues    │
            └─────────────┘   │ - Prioritize critical/       │
                              │   important issues           │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ Create Refinement Prompt     │
                              │ - Show specific issues       │
                              │ - Provide current analysis   │
                              │ - Instruct surgical fixes    │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ Run Analysis Loop (Refine)   │
                              │ - Agent uses tools to fix    │
                              │ - Shows new calculations     │
                              │ - Adds missing details       │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ Merge Refinements            │
                              │ - Append fixes to original   │
                              │ - Update metadata            │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ Re-Validate (Iteration N)    │
                              │ - Check if issues fixed      │
                              │ - New score                  │
                              └──────────────┬───────────────┘
                                             │
                                  ┌──────────┴──────────┐
                                  │ Score >= 80 OR      │
                                  │ Max iterations?     │
                                  └──────────┬──────────┘
                                         YES │      NO
                                             │      │
                                    ┌────────▼──┐   │
                                    │   DONE    │   │
                                    └───────────┘   │
                                                    │
                                        (Loop back to filter issues)
```

### Implementation Details

#### 1. Entry Point: `_validate_with_refinement()`

**Location:** [buffett_agent.py:2620-2720](../../src/agent/buffett_agent.py#L2620-L2720)

```python
def _validate_with_refinement(
    self,
    result: Dict[str, Any],
    ticker: str,
    max_refinements: int = 2,
    score_threshold: int = 80
) -> Dict[str, Any]:
    """
    Validate analysis and iteratively refine if score below threshold.

    Phase 7.6C: Implements Buffett-style iterative improvement.
    """
```

**Parameters:**
- `max_refinements=2` - Up to 2 refinement attempts
- `score_threshold=80` - Target validation score

**Flow:**
1. Validate initial analysis
2. If score < 80, filter fixable issues
3. Create refinement prompt
4. Run refinement
5. Re-validate
6. Repeat until score ≥ 80 or max iterations

#### 2. Filtering Fixable Issues: `_filter_fixable_issues()`

**Location:** [buffett_agent.py:2722-2774](../../src/agent/buffett_agent.py#L2722-L2774)

**Purpose:** Determine which issues can be fixed through refinement.

**Fixable Issues:**
- Missing calculations (can use calculator_tool)
- Missing citations (can add page numbers)
- Vague prices (can use web_search)
- CEO research gaps (can use web_search)
- Lack of formula display (can show calculations)

**Unfixable Issues (Skip):**
- "Data not available in filings"
- "Company does not disclose"
- "Fundamental business quality" problems
- "Industry in structural decline"

**Prioritization:**
1. Critical issues (always include)
2. Important issues (always include)
3. Minor issues (include if < 3 total issues)

#### 3. Creating Refinement: `_refine_analysis()`

**Location:** [buffett_agent.py:2776-2902](../../src/agent/buffett_agent.py#L2776-L2902)

**Refinement Prompt Structure:**

```markdown
**REFINEMENT TASK - Iteration {N}**

Your previous {ticker} analysis received score {score}/100.

Issues to address:
1. [CRITICAL - calculations]: ROIC shown without methodology...
2. [IMPORTANT - data]: Citations lack page numbers...
3. [IMPORTANT - decision]: Current price too vague...

**CURRENT ANALYSIS (for reference):**
[Shows existing analysis]

**YOUR TASK:**
Fix ONLY the specific issues above.

1. Use tools:
   - calculator_tool for calculations
   - web_search_tool for prices/CEO changes
   - sec_filing_tool for page numbers

2. Show your work:
   - Formulas + inputs + sources
   - Exact prices with dates
   - CEO names and backgrounds

3. Make surgical fixes:
   - Fix ONLY issue-related sections
   - Keep other content the same
   - Maintain Buffett voice

Begin refinement now:
```

**Key Features:**
- **Targeted:** Only addresses specific issues
- **Tool-enabled:** Analyst can use all tools
- **Buffett-aligned:** Emphasizes "show your work"
- **Conservative:** Surgical fixes, not complete rewrites

#### 4. Merging Refinements

**Strategy:** Append refinements to original analysis

```
[Original Analysis]

---

## REFINEMENTS (Iteration 1):

[Fixed sections with explanations]
```

**Why Append Instead of Replace:**
- Preserves original good content
- Shows transparency (what was fixed)
- Allows validator to verify fixes
- Maintains analysis continuity

---

## Expected Impact

### Score Improvements

| Scenario | Initial Score | After 1 Refinement | After 2 Refinements |
|----------|--------------|-------------------|-------------------|
| **NVO (Current)** | 75/100 | 85-90/100 | 90-95/100 |
| **Typical Deep Dive** | 70-80/100 | 80-90/100 | 85-95/100 |
| **Quick Screen** | 65-75/100 | 75-85/100 | 80-90/100 |

### Issues Resolved

From NVO test case, expected fixes:

| Issue | Initial | After Refinement |
|-------|---------|------------------|
| ROIC methodology missing | ❌ CRITICAL | ✅ Shows formula + calculation |
| Citations lack specificity | ❌ IMPORTANT | ✅ Adds page numbers |
| Calculator usage not shown | ❌ IMPORTANT | ✅ References tool outputs |
| Current price vague | ❌ IMPORTANT | ✅ Exact price with date |
| CEO replacement not named | ❌ MINOR | ✅ Names both CEOs |

**Expected final score:** 85-90/100 (vs 75/100 initial)

### Cost & Time Impact

**Without Refinement:**
- Cost: $1-2
- Time: 3-5 minutes
- Score: 70-80/100

**With 1 Refinement (typical):**
- Cost: $2-4 (2× synthesis)
- Time: 5-8 minutes
- Score: 80-90/100

**With 2 Refinements (edge cases):**
- Cost: $3-6 (3× synthesis)
- Time: 7-11 minutes
- Score: 85-95/100

**ROI:** +10-15 points per $1-2 spent on refinement

---

## Files Changed

### Modified (1 file, ~350 lines added)

**[src/agent/buffett_agent.py](../../src/agent/buffett_agent.py)**

#### Synthesis Prompt Enhancements:
1. **Lines 1437-1471** - CEO/management change research requirement
2. **Lines 1481-1510** - ROIC calculation methodology requirement
3. **Lines 1683-1698** - Exact current price requirement
4. **Lines 1792-1803** - Detailed citation requirements with examples

#### Iterative Refinement System:
1. **Lines 274-290** - Modified validation entry point to use refinement
2. **Lines 2620-2720** - `_validate_with_refinement()` main loop
3. **Lines 2722-2774** - `_filter_fixable_issues()` helper
4. **Lines 2776-2902** - `_refine_analysis()` helper
5. **Lines 2904-2931** - `_format_issues_for_refinement()` helper

**Total Lines Added:** ~350
**Total Lines Modified:** ~30

### Created (1 file)

**[docs/phases/phase_7.6/PHASE_7.6C_REFINEMENT.md](./PHASE_7.6C_REFINEMENT.md)** - This file

---

## Testing Plan

### Test 1: NVO Deep Dive with Refinement

```bash
python -c "
from src.agent.buffett_agent import WarrenBuffettAgent

agent = WarrenBuffettAgent(
    model_key='kimi-k2-thinking',
    enable_validation=True  # Refinement enabled by default
)

result = agent.analyze_company('NVO', deep_dive=True, years_to_analyze=5)

print(f\"Final Score: {result['validation']['score']}/100\")
print(f\"Refinements: {result['validation']['refinements']}\")
print(f\"History: {result['validation']['refinement_history']}\")
"
```

**Expected:**
- Initial score: 75-80/100
- After refinement 1: 85-90/100
- Refinements needed: 1
- Issues fixed: 4-5 of 5

### Test 2: Quick Screen (Should Pass Without Refinement)

```bash
python -c "
from src.agent.buffett_agent import WarrenBuffettAgent

agent = WarrenBuffettAgent(
    model_key='kimi-k2-thinking',
    enable_validation=True
)

result = agent.analyze_company('AAPL', deep_dive=False)

print(f\"Score: {result['validation']['score']}/100\")
print(f\"Refinements: {result['validation']['refinements']}\")
"
```

**Expected:**
- Initial score: 80-85/100 (enhanced prompts help)
- Refinements needed: 0
- Passes threshold immediately

---

## Backward Compatibility

✅ **Fully backward compatible**

- Refinement is automatic (no API changes)
- If `enable_validation=False`, refinement is skipped
- Validation metadata structure unchanged (only adds `refinements` and `refinement_history` fields)
- Existing analyses continue to work

**Migration:** None needed - just upgrade and benefit from improvements

---

## Configuration

### Default Settings

```python
# In analyze_company() or buffett_agent.py
max_refinements = 2          # Up to 2 refinement attempts
score_threshold = 80          # Target score for quality
```

### Customization

To adjust refinement behavior:

```python
agent = WarrenBuffettAgent(model_key='kimi-k2-thinking')

# Option 1: Disable refinement (keep validation)
agent.max_validation_iterations = 1  # Only initial validation

# Option 2: More aggressive refinement
# (Would need to modify _validate_with_refinement call)
# max_refinements=3, score_threshold=85

# Option 3: Disable validation entirely
agent = WarrenBuffettAgent(model_key='kimi-k2-thinking', enable_validation=False)
```

---

## Alignment with Buffett Principles

### "Show Your Work" (BUFFETT_PRINCIPLES.md lines 400-551)

**Before:**
> Owner Earnings: $5.2B

**After:**
```
Owner Earnings Calculation:
Operating Cash Flow: $8.5B (Source: 10-K FY2024, Cash Flow Statement, page 67)
- Total CapEx: $3.3B (Source: 10-K FY2024, Cash Flow Statement, page 67)
= Owner Earnings: $5.2B

Calculator Tool Output: owner_earnings=$5.2B
```

### "Rigorous Fact-Checking" (Throughout BUFFETT_PRINCIPLES.md)

**Validator can now verify facts:**
- CEO changes (uses web_search_tool)
- Financial calculations (uses calculator_tool)
- Source citations (checks for specificity)

### "Long-term Focus" (BUFFETT_PRINCIPLES.md lines 1444-1576)

**Quality > Speed:**
- Willing to spend extra time on refinement
- Ensures thorough analysis before decisions
- Values accuracy over quick conclusions

---

## Known Limitations

1. **Refinement Cost**
   - Each refinement = full synthesis call
   - Can be 2-3× cost of initial analysis
   - Mitigated by: Most analyses pass in 0-1 refinements

2. **Context Management**
   - Refinement prompt + original analysis = large context
   - Mitigated by: Truncate original to 15K chars in prompt

3. **Cascading Issues**
   - Fixing one issue might create another
   - Mitigated by: Max 2 refinements prevents endless loops

4. **False Refinements**
   - May refine issues that are actually acceptable
   - Mitigated by: Score threshold of 80 (not 100)

---

## Future Enhancements

### Potential Improvements:

1. **Smarter Refinement Triggers**
   - Only refine critical/important issues
   - Skip refinement for minor issues
   - Weight score by issue severity

2. **Selective Refinement**
   - Fix only worst 1-2 issues per iteration
   - Multiple small fixes instead of one big refinement

3. **Learning from Refinements**
   - Track which issues are most common
   - Improve synthesis prompts based on patterns
   - Build "issue → fix" playbook

4. **User Control**
   - Optional: "Approve refinement before running"
   - User can choose which issues to fix
   - Trade-off cost vs quality interactively

---

## Conclusion

Phase 7.6C delivers systematic quality improvement through two complementary mechanisms:

1. **Enhanced Prompts** - Prevent issues through stricter requirements
2. **Iterative Refinement** - Fix remaining issues automatically

**Key Achievement:** basīrah now operates more like Warren Buffett himself - showing work, citing sources rigorously, and self-correcting when gaps are identified.

**Next Steps:**
- Test with NVO 5-year deep dive
- Verify score improvement (75 → 85-90)
- Monitor refinement frequency and cost
- Collect data on most common fixable issues

---

**Phase 7.6C Version:** 1.0
**Date Completed:** 2025-11-13
**Total Development Time:** ~3 hours
**Lines of Code Added:** ~350
**Expected Quality Improvement:** +10-15 validation score points
**Cost Impact:** +100% (but optional via enable_validation)

---

**END OF DOCUMENT**
