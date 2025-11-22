# Inline Data Tables Implementation

## Overview

**Date:** 2025-11-20
**Status:** ✅ Complete
**Purpose:** Require inline tables with data + sources + trends wherever calculations are performed

## User Requirement

> "when the agent performs any calculations using data a table of the data with source should be present"

**Key clarifications:**
- NOT a separate "show work" section
- YES inline tables embedded wherever calculations happen
- Tables must show **trends over time**, not just snapshots
- Every table must include **source citations**

---

## Implementation

### 1. Analyst Prompt Updates ([buffett_prompt.py](src/agent/buffett_prompt.py))

#### Owner Earnings Section (Lines 209-218)

**Added:** 10-year Free Cash Flow trend table requirement

```markdown
**REQUIRED: Present Owner Earnings data in table format with trends:**

| Year | Operating Cash Flow | CapEx | Free Cash Flow | YoY Change | Source |
|------|-------------------|--------|----------------|------------|--------|
| 2024 | $XXX.XB | $XX.XB | $XXX.XB | +X.X% | GuruFocus |
| 2023 | $XXX.XB | $XX.XB | $XXX.XB | +X.X% | GuruFocus |
| ... | ... | ... | ... | ... | ... |

**Trend Analysis:** [Growing/Declining/Stable] at X.X% CAGR over 10 years
```

#### ROIC Section (Lines 267-276)

**Added:** 10-year ROIC trend table requirement

```markdown
**REQUIRED: Present ROIC trend data in table format:**

| Year | Operating Income | Invested Capital | ROIC | Trend | Source |
|------|-----------------|------------------|------|-------|--------|
| 2024 | $XX.XB | $XXX.XB | XX.X% | +X.Xpp | GuruFocus |
| ... | ... | ... | ... | ... | ... |

**Trend Analysis:** [Improving/Stable/Declining] - Average ROIC XX.X% over 10 years
```

#### Moat Assessment Section (Lines 92-115)

**Added:** Multiple evidence tables showing trends over time

```markdown
**REQUIRED: Present moat evidence in table format with trends over time:**

**Example - Customer Retention/Switching Costs:**
| Year | Retention Rate | Churn Rate | Industry Avg | Evidence Source |
|------|----------------|------------|--------------|-----------------|
| 2024 | XX% | X.X% | XX% | 10-K FY2024, pg XX |
| 2023 | XX% | X.X% | XX% | 10-K FY2023 |
| 2022 | XX% | X.X% | XX% | 10-K FY2022 |

**Example - Pricing Power:**
| Year | Avg Price Increase | Inflation Rate | Real Pricing Power | Source |
|------|-------------------|----------------|-------------------|--------|
| 2024 | +X.X% | X.X% | +X.X% | MD&A FY2024 |
| ... | ... | ... | ... | ... |

**Example - Market Share:**
| Year | Market Share | Rank | Top 3 Combined | Source |
|------|-------------|------|----------------|--------|
| 2024 | XX% | #X | XX% | Industry report/Web search |
| ... | ... | ... | ... | ... |

**Trend Analysis:** [Strengthening/Stable/Eroding] - narrative explaining trends
```

#### Management Evaluation Section (Lines 153-170)

**Added:** Capital allocation and compensation trend tables

```markdown
**REQUIRED: Present management track record in table format:**

**Capital Allocation Track Record:**
| Year | ROIC | Major M&A | Buyback $ | Dividend $ | Total Shareholder Returns | Source |
|------|------|-----------|-----------|------------|--------------------------|--------|
| 2024 | XX.X% | [Deal name, $XXB] | $X.XB | $X.XB | XX.X% | 10-K, Proxy |
| ... | ... | ... | ... | ... | ... | ... |

**Management Compensation Trend:**
| Year | CEO Total Comp | Median Worker | Ratio | Performance vs Comp | Source |
|------|----------------|---------------|-------|---------------------|--------|
| 2024 | $XX.XM | $XXK | XXX:1 | [Aligned/Excessive] | DEF 14A |
| ... | ... | ... | ... | ... | ... |

**Trend Analysis:** [Improving/Consistent/Declining] capital allocation discipline
```

#### DCF Valuation Section (Lines 201-226)

**Added:** Historical growth analysis, DCF assumptions, and scenario analysis tables

```markdown
**REQUIRED: Present DCF assumptions in table format with justification:**

**Historical Growth Analysis:**
| Metric | 10-Year CAGR | 5-Year CAGR | 3-Year CAGR | Selected Growth Rate | Rationale | Source |
|--------|--------------|-------------|-------------|---------------------|-----------|--------|
| Revenue | X.X% | X.X% | X.X% | X.X% | Conservative: 70% of historical | GuruFocus |
| Owner Earnings | X.X% | X.X% | X.X% | X.X% | Conservative: 70% of historical | GuruFocus |

**DCF Assumption Summary:**
| Parameter | Value | Justification | Source |
|-----------|-------|---------------|--------|
| Base Year Owner Earnings | $XX.XB | 2024 FCF from GuruFocus | GuruFocus |
| Growth Rate (Years 1-10) | X.X% | MAX(0%, MIN(5%, 70% × X.X% historical)) | Calculated |
| Discount Rate | X.X% | [9% world-class / 10% standard / 12% uncertain] | Framework |
| Terminal Growth | X.X% | Long-term GDP growth assumption | Framework |
| **Intrinsic Value** | **$XXX** | **DCF calculation result** | **Calculated** |
| Current Price | $XXX | Market price as of [date] | Market |
| **Margin of Safety** | **XX%** | **(IV - Price) / IV × 100%** | **Calculated** |

**Scenario Analysis:**
| Scenario | Growth Rate | Discount Rate | Terminal Growth | Intrinsic Value | MoS |
|----------|-------------|---------------|-----------------|-----------------|-----|
| Bull | X.X% | X.X% | 3.0% | $XXX | XX% |
| Base | X.X% | X.X% | 2.5% | $XXX | XX% |
| Bear | X.X% | X.X% | 2.0% | $XXX | XX% |
```

#### Financial Analysis Guidelines (Lines 644-648)

**Added:** General requirement emphasizing all data must be in tables

```markdown
**CRITICAL: All financial data and calculations MUST be presented in tables with:**
- Historical trends (not just current year snapshots)
- Source citations (GuruFocus, 10-K, MD&A, etc.)
- Year-over-year changes showing trajectory
- Clear narrative explaining what the trends reveal
```

---

### 2. Validator Prompt Updates ([prompts.py](src/agent/prompts.py))

#### Owner Earnings Validation (Lines 578-582)

**Added:** Checklist for Owner Earnings table requirement

```markdown
**TABLE REQUIREMENT: Owner Earnings Data (NEW):**
□ Does analysis include table showing 10-year FCF trend with YoY changes?
□ Table columns: Year | OCF | CapEx | Free Cash Flow | YoY Change | Source
□ Trend analysis provided (Growing/Declining/Stable with CAGR)?
□ Sources cited for each row (GuruFocus recommended)?
```

#### Required Calculations Validation (Lines 593-602)

**Added:** Checklists for ROIC and DCF tables

```markdown
**TABLE REQUIREMENT: ROIC Trend Data (NEW):**
□ Does analysis include table showing 10-year ROIC trend?
□ Table columns: Year | Operating Income | Invested Capital | ROIC | Trend | Source
□ Trend analysis provided (Improving/Stable/Declining with average)?

**TABLE REQUIREMENT: DCF Assumptions (NEW):**
□ Does analysis include table showing historical growth rates (10-year, 5-year, 3-year CAGR)?
□ Does analysis include DCF assumption summary table with justifications?
□ Table showing: Parameter | Value | Justification | Source
□ Scenario analysis table (Bull/Base/Bear with different assumptions)?
```

#### Data Quality Validation (Lines 622-626)

**Added:** General table presentation checklist

```markdown
**TABLE REQUIREMENT: Data Presentation (NEW):**
□ All financial data presented in tables (not just text)?
□ Tables show trends over time (not just current year snapshots)?
□ Every table row includes source citation?
□ YoY changes shown to demonstrate trajectory?
```

#### Buffett Methodology Validation (Lines 637-646)

**Added:** Moat evidence and management track record table checklists

```markdown
**TABLE REQUIREMENT: Moat Evidence with Trends (NEW):**
□ Does moat assessment include tables showing trends over time?
□ Example tables: Retention rates by year, pricing power trends, market share evolution
□ Each moat source backed by multi-year data (not just current snapshots)?
□ Sources cited for each data point?

**TABLE REQUIREMENT: Management Track Record (NEW):**
□ Capital allocation table showing: Year | ROIC | Major M&A | Buybacks | Dividends | TSR | Source
□ Management compensation trend table showing: Year | CEO Comp | Median Worker | Ratio | Source
□ Multi-year view demonstrating track record (not just current year)?
```

---

## Key Benefits

### 1. Transparency
- Users can see the exact data used in every calculation
- Source citations enable verification
- Trends over time show trajectory (not just snapshots)

### 2. Evidence-Based Analysis
- Moat assessments backed by multi-year trends
- Management evaluation shows track record over time
- DCF assumptions justified with historical data

### 3. Validator Alignment
- Validator now checks for presence of required tables
- Reduces "missing calculation methodology" critiques
- Ensures consistency between analyst requirements and validator expectations

### 4. Better Decisions
- Historical trends reveal patterns (improving vs declining)
- Scenario analysis shows sensitivity to assumptions
- Multi-year view reduces recency bias

---

## Examples of Required Tables

### Example 1: Owner Earnings (GuruFocus FCF - Preferred)

| Year | Operating Cash Flow | CapEx | Free Cash Flow | YoY Change | Source |
|------|-------------------|--------|----------------|------------|--------|
| 2024 | $80.8B | $44.4B | $36.4B | +8.3% | GuruFocus |
| 2023 | $80.5B | $47.0B | $33.5B | +5.2% | GuruFocus |
| 2022 | $91.0B | $59.2B | $31.8B | +12.4% | GuruFocus |
| 2021 | $88.5B | $60.2B | $28.3B | +15.8% | GuruFocus |
| 2020 | $73.4B | $49.0B | $24.4B | -8.1% | GuruFocus |
| ... | ... | ... | ... | ... | ... |

**Trend Analysis:** Growing at 8.2% CAGR over 10 years, with consistent positive FCF generation

### Example 2: ROIC Trend

| Year | Operating Income | Invested Capital | ROIC | Trend | Source |
|------|-----------------|------------------|------|-------|--------|
| 2024 | $25.5B | $115.2B | 22.1% | +0.7pp | GuruFocus |
| 2023 | $24.8B | $116.0B | 21.4% | +0.5pp | GuruFocus |
| 2022 | $23.9B | $114.3B | 20.9% | +1.2pp | GuruFocus |
| ... | ... | ... | ... | ... | ... |

**Trend Analysis:** Improving - Average ROIC 21.5% over 10 years, consistently above 20% threshold for BUY

### Example 3: Pricing Power Evidence

| Year | Avg Price Increase | Inflation Rate | Real Pricing Power | Source |
|------|-------------------|----------------|-------------------|--------|
| 2024 | +4.2% | 3.4% | +0.8% | MD&A FY2024, pg 38 |
| 2023 | +6.1% | 4.0% | +2.1% | MD&A FY2023, pg 35 |
| 2022 | +5.8% | 8.0% | -2.2% | MD&A FY2022, pg 33 |
| 2021 | +3.5% | 4.7% | -1.2% | MD&A FY2021, pg 31 |

**Trend Analysis:** Company has pricing power - able to raise prices above inflation in 2 of past 4 years, maintained margins despite 2022 cost pressures

---

## Impact on Future Analyses

### Analyst Behavior Changes
- Will now include detailed tables for all calculations
- Will cite sources for every data point
- Will show trends over time (not just current year)
- Will provide narrative explaining what trends reveal

### Validator Behavior Changes
- Will check for presence of required tables
- Will verify source citations are included
- Will assess whether trends are shown (not just snapshots)
- Will flag missing tables as "IMPORTANT" issue (not CRITICAL)

### User Benefits
- Can verify calculations by checking source data
- Can see if metrics are improving or declining over time
- Can assess management track record objectively
- Can understand DCF assumption sensitivity

---

## Testing Recommendations

### Test 1: New Deep Dive Analysis
Run a fresh deep dive analysis and verify:
- ✅ Owner Earnings table with 10-year FCF trend appears
- ✅ ROIC table with 10-year trend appears
- ✅ Moat evidence tables show multi-year trends
- ✅ Management track record tables included
- ✅ DCF assumptions presented in table format
- ✅ All tables include source citations

### Test 2: Validator Response
Check that validator:
- ✅ No longer flags "missing calculation methodology" for analyses with tables
- ✅ Flags missing tables as "IMPORTANT" issue if absent
- ✅ Verifies source citations are present in tables
- ✅ Checks that trends are shown (not just snapshots)

---

## Files Modified

### Modified:
1. **[src/agent/buffett_prompt.py](src/agent/buffett_prompt.py)** (5 sections updated)
   - Lines 209-218: Owner Earnings table requirement
   - Lines 267-276: ROIC trend table requirement
   - Lines 92-115: Moat evidence tables requirement
   - Lines 153-170: Management track record tables requirement
   - Lines 201-226: DCF assumptions tables requirement
   - Lines 644-648: General table requirement emphasis

2. **[src/agent/prompts.py](src/agent/prompts.py)** (6 validation checklists added)
   - Lines 578-582: Owner Earnings table validation
   - Lines 593-596: ROIC table validation
   - Lines 598-602: DCF assumptions table validation
   - Lines 622-626: Data presentation table validation
   - Lines 637-641: Moat evidence table validation
   - Lines 643-646: Management track record table validation

### Created:
1. **INLINE_DATA_TABLES_IMPLEMENTATION.md** - This summary document

---

## Status

✅ **Implementation Complete**
⏳ **Pending Production Testing** - Will verify in next deep dive analysis

**Next Step:** Run test deep dive (e.g., NVO, MSFT) to verify tables appear as expected

---

**Implementation Date:** 2025-11-20
**User Request:** "when the agent performs any calculations using data a table of the data with source should be present"
**Solution:** Inline tables with data + sources + trends embedded wherever calculations occur
**Validator Alignment:** ✅ Validator now checks for table presence and quality

---

## Summary

This implementation addresses the user's requirement for **inline data tables** wherever calculations are performed. Instead of a separate "show work" section, tables are now **embedded inline** with:

1. **Historical trends** (not just snapshots)
2. **Source citations** (GuruFocus, 10-K, MD&A, page numbers)
3. **YoY changes** showing trajectory
4. **Narrative analysis** explaining what trends reveal

Both the **analyst prompt** (requires tables) and **validator prompt** (checks for tables) have been updated to ensure alignment and consistency.
