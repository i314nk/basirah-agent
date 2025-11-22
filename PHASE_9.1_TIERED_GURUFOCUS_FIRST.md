# Phase 9.1: Tiered Analysis with GuruFocus-First Strategy

**Date:** November 20, 2025
**Status:** ✅ Complete
**Previous Phase:** Phase 9 (Framework-Driven Analysis)

---

## Overview

Phase 9.1 refines Phase 9's framework-driven approach with a **tiered analysis strategy** and **GuruFocus-first** methodology. This addresses two key issues:

1. **Calculation errors** - Manual calculations of ROIC, Owner Earnings, etc. prone to errors
2. **Cost efficiency** - Reading 10 full years of 10-Ks is impractical and expensive

---

## The Problem

### Before Phase 9.1:
- Agent calculated ROIC, Owner Earnings, margins manually (error-prone)
- Guidance to read "complete 10-Ks for multiple years" was vague
- No clear distinction between screening vs. deep dive analysis
- Expensive and slow for companies that would be AVOID anyway

### User's Directive:
> "I would like the agent to mostly rely on gurufocus data when it comes to Quantitative analysis = GuruFocus data (verified, 10 years) as to avoid calculation mistakes."

> "Don't do full 10 years of complete 10-Ks. Instead: Latest 10-K (full) + Historical MD&A sections (5 years) for management discussion only."

---

## Solution: Tiered Analysis with GuruFocus-First

### Tier 1: Quick Screen (ALL Companies)

**Purpose:** Filter out AVOID and WATCH candidates quickly

**Quantitative (GuruFocus):**
- 10-year ROIC, margins, revenue growth - **Use GuruFocus data directly**
- Debt levels, interest coverage, financial strength
- Owner Earnings components - **GuruFocus calculated, don't recalculate**

**Qualitative:**
- Latest 10-K (section="full") - Current business description, risks, strategy
- Web search - Major recent events, competitive positioning, moat evidence

**Outcome:**
- **AVOID (40-50%)** - Fails key criteria (low ROIC, no moat, red flags) → STOP
- **WATCH (40-50%)** - Good business, wrong price or missing criteria → STOP
- **BUY candidate** - All 8 criteria look strong → **Proceed to Tier 2**

---

### Tier 2: Deep Dive (BUY Candidates Only)

**Purpose:** Build conviction for rare BUY recommendations

**Quantitative (GuruFocus):**
- Same as Tier 1 - GuruFocus remains source of truth
- No manual recalculation

**Qualitative:**
- Latest 10-K (section="full") - Comprehensive current analysis
- **5 years of MD&A sections** (section="mda", 2020-2024) - Management track record
- Proxy statements (DEF 14A) - Compensation, insider ownership
- Targeted web search - Key strategic decisions, major acquisitions, outcomes

**Why MD&A Only (Not Full Filings):**
- MD&A is 10-20% of full 10-K → 5 years of MD&A < 1 year of full filing
- MD&A reveals management thinking: strategy, challenges, decisions, outlook
- Cost controlled, context window manageable
- Authentic to Buffett - historical perspective without drowning in boilerplate

**Validation:**
- Cross-check management claims with GuruFocus actual results
- Apply Charlie Munger's mental models (single-pass)
- Final framework scoring: Moat (/15), Management (/12), Predictability (/3)

---

## Implementation Changes

### 1. Updated System Prompt ([src/agent/buffett_prompt.py](src/agent/buffett_prompt.py))

**Section 1: TIERED ANALYSIS APPROACH (Lines 568-612)**

```python
## 1. TIERED ANALYSIS APPROACH (Phase 9: Hybrid Quantitative + Qualitative)

**CRITICAL: Use GuruFocus for ALL quantitative data - avoid calculation errors**

### Tier 1: Quick Screen (Most Analyses)

**Quantitative (GuruFocus):**
- 10-year ROIC, margins, revenue growth - GuruFocus calculates these reliably
- Debt levels, interest coverage, financial strength
- Owner Earnings components (use GuruFocus data, don't recalculate)

**Qualitative:**
- Latest 10-K (section="full") - Current business description, risks, strategy
- Web search - Major recent events, competitive positioning, moat evidence

**Use for:** Initial screening, most companies (AVOID or WATCH candidates)

### Tier 2: Deep Dive (BUY Candidates Only)

**Quantitative (GuruFocus):**
- Same as Tier 1 - GuruFocus is your source of truth for all numbers
- 10-year financial history (verified, no manual calculations needed)

**Qualitative:**
- Latest 10-K (section="full") - Comprehensive current analysis
- **5 years of MD&A sections** (NOT full 10-Ks) - Management's discussion over time
- Proxy statements (DEF 14A) - Compensation, insider ownership
- Targeted web search - Key strategic decisions, major acquisitions, competitive responses
```

**Section 2: ANALYSIS APPROACH (Lines 324-379)**

```python
# ANALYSIS APPROACH (Phase 9: Tiered, GuruFocus-First)

## Tier 1: Quick Screen (ALL Companies)

**Step 1: GuruFocus Quantitative Screen (10-year data)**
- Fetch summary, financials, keyratios from GuruFocus
- Check ROIC (need >15%, ideally >20%)
- Check debt levels (Debt/Equity <0.7)
- Check Owner Earnings trend (GuruFocus data, don't calculate manually)
- **Early disqualification:** ROIC <10% → AVOID immediately

**Step 2: Qualitative Screen (Latest 10-K + Web Search)**
- Read latest 10-K (section="full") - Business, risks, competitive position
- Web search for moat evidence, recent news
- Assess Circle of Competence (understandable?)
- Score Moat (/15), Management (/12), Predictability (/3)

**Step 3: Decision Point**
- **AVOID (40-50%):** Fails key criteria (low ROIC, no moat, red flags)
- **WATCH (40-50%):** Good business, wrong price or missing some criteria
- **BUY candidate:** All 8 criteria look strong → **Proceed to Tier 2**

## Tier 2: Deep Dive (BUY Candidates Only)

**Step 4: Historical Qualitative Analysis**
- Read 5 years of MD&A sections (2020-2024, section="mda")
- Read proxy (DEF 14A) - Compensation, insider ownership
- Targeted web search - Key acquisitions, competitive responses

**Step 5: Validation with GuruFocus**
- Cross-check management claims with GuruFocus actual results
- Verify ROIC trends match management's capital allocation narrative

**Step 6: Final Framework Assessment**
- Score Moat (/15), Management (/12), Predictability (/3)
- Calculate Margin of Safety using GuruFocus data (NOT manual DCF)
- Check ALL 8 BUY criteria
```

**Section 3: TOOL USAGE STRATEGY (Lines 652-703)**

```python
## 4. Use Tools Intelligently (Phase 9: GuruFocus-First Strategy)

**CRITICAL: GuruFocus is your PRIMARY source for ALL quantitative data**

### GuruFocus Tool (PRIMARY for Quantitative)
**Use for:** ALL quantitative analysis - ROIC, margins, debt, Owner Earnings
**When:** First tool call for EVERY analysis (avoid calculation errors)
**Trust level:** HIGH - GuruFocus data is verified, audited, reliable

### SEC Filing Tool (Qualitative Analysis)
**Tier 1 (Quick Screen):**
- Latest 10-K (section="full") - Current business state, risks, strategy

**Tier 2 (Deep Dive - BUY candidates):**
- Latest 10-K (section="full") - Comprehensive current analysis
- 5 years of MD&A (section="mda", year=2020-2024) - Management track record
- Proxy (filing_type="DEF 14A") - Compensation, ownership

### Calculator Tool (MINIMAL USE - Prefer GuruFocus)
**Use for:** ONLY when GuruFocus doesn't provide the data
**Avoid:** Manual ROIC, Owner Earnings, margin calculations (use GuruFocus instead)
```

---

### 2. Updated UI ([src/ui/components.py](src/ui/components.py))

**Deep Dive Progress Description (Lines 76-91):**

```python
st.info(
    "📊 **Deep Dive Analysis (Tiered, GuruFocus-First)**\n\n"
    "**Tier 1: Quick Screen (All Companies)**\n"
    "• GuruFocus: 10-year quantitative data (ROIC, debt, Owner Earnings)\n"
    "• Latest 10-K (full): Business description, risks, competitive position\n"
    "• Web search: Moat evidence, recent news\n"
    "• Decision: AVOID (40-50%), WATCH (40-50%), or proceed to Tier 2\n\n"
    "**Tier 2: Deep Dive (BUY Candidates Only)**\n"
    "• 5 years of MD&A sections: Management track record over time\n"
    "• Proxy statement: Compensation, insider ownership\n"
    "• Targeted web search: Strategic decisions, acquisitions, outcomes\n"
    "• Validation: Charlie Munger's mental models (single-pass)\n"
    "• Final scoring: Moat (/15), Management (/12), Predictability (/3)\n\n"
    "Expected time: 3-5 minutes (Tier 1), 5-7 minutes (Tier 2)\n"
    "Expected cost: ~$1-2 (Tier 1), ~$3-5 (Tier 2)"
)
```

---

## Key Benefits

### 1. Accuracy (GuruFocus-First)
- ✅ No manual calculation errors for ROIC, Owner Earnings, margins
- ✅ Verified, audited financial data (10 years)
- ✅ Consistent methodology across all companies

### 2. Cost Efficiency (Tiered Approach)
- ✅ Tier 1 stops AVOID/WATCH candidates early (~$1-2)
- ✅ Tier 2 only for BUY candidates (~$3-5)
- ✅ 5 years of MD&A < 1 year of full 10-K (context window savings)

### 3. Authenticity (Historical MD&A Analysis)
- ✅ Reveals if management delivers on commitments
- ✅ Shows strategic thinking evolution over time
- ✅ Avoids drowning in regulatory boilerplate

### 4. Practical (Manageable Scope)
- ✅ Latest 10-K (full) for current comprehensive analysis
- ✅ 5 years of MD&A for historical perspective
- ✅ GuruFocus for all quantitative validation
- ✅ Targeted web search for key strategic events

---

## Quantitative Analysis: GuruFocus as Source of Truth

**What GuruFocus Provides (Use Directly):**
- ROIC (10 years) - Calculated and verified
- Owner Earnings (10 years) - Calculated from components
- Margins (Gross, Operating, Net) - 10 years
- Debt levels, interest coverage, financial strength
- Revenue growth, earnings growth

**What NOT to Calculate Manually:**
- ❌ ROIC - Use GuruFocus data
- ❌ Owner Earnings - Use GuruFocus data
- ❌ Margins - Use GuruFocus data
- ❌ Growth rates - Use GuruFocus data

**When to Use Calculator Tool:**
- Only when GuruFocus doesn't provide the specific metric
- Rare cases (GuruFocus should cover 95% of quantitative needs)

---

## Qualitative Analysis: MD&A Historical Analysis

### Why MD&A is the Key Section:

**MD&A = Management's Discussion & Analysis**
- Strategy articulation and evolution
- Challenges faced and how management responded
- Capital allocation decisions and reasoning
- Outlook and forward-looking statements

**What You Learn from 5 Years of MD&A:**
1. **Consistency** - Does management deliver on commitments?
2. **Honesty** - Are they candid about challenges?
3. **Rationality** - Do they make evidence-based decisions?
4. **Alignment** - Do they think long-term or short-term?

### Example: Management Quality Assessment

**Year 1 MD&A (2020):**
> "We plan to expand into Asia with 10 new stores, targeting $500M in revenue by 2022."

**GuruFocus Data (2022):**
- Asia revenue: $480M (96% of target - delivered)
- ROIC maintained at 18% (capital allocation disciplined)

**Year 3 MD&A (2022):**
> "Asia expansion successful. Now focusing on margin improvement through operational excellence."

**Conclusion:** Management sets realistic goals, executes well, thinks long-term.

---

## Moat Analysis: Latest 10-K + Web Search

**From Latest 10-K (Item 1: Business):**
- Company's description of competitive advantages
- Market position, customer relationships
- Patents, brands, regulatory licenses

**From Web Search:**
- External validation of moat claims
- Competitive threats and responses
- Market share trends, pricing power evidence

**From GuruFocus:**
- ROIC trends (real moats show up as sustained high ROIC >20%)
- Margin stability (pricing power evident in gross margins)
- Revenue growth consistency

---

## Decision Flow

```
┌─────────────────────────────────────────────────┐
│ START: User requests analysis for ticker       │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│ TIER 1: QUICK SCREEN                            │
│                                                 │
│ Step 1: GuruFocus (10-year quantitative)        │
│   - ROIC >15%? Debt/Equity <0.7?               │
│   - Owner Earnings growing?                    │
│   - Early disqualification: ROIC <10% → AVOID  │
│                                                 │
│ Step 2: Latest 10-K (full) + Web Search        │
│   - Business understandable?                   │
│   - Moat evidence?                             │
│   - Score: Moat (/15), Mgmt (/12), Pred (/3)   │
│                                                 │
│ Step 3: Decision Point                         │
└─────────────────┬───────────────────────────────┘
                  ↓
      ┌───────────┴───────────┐
      ↓                       ↓
┌─────────────┐         ┌─────────────┐
│ AVOID       │         │ WATCH       │
│ (40-50%)    │         │ (40-50%)    │
│             │         │             │
│ Fails key   │         │ Good biz,   │
│ criteria    │         │ wrong price │
└─────────────┘         └─────────────┘
      ↓                       ↓
   [STOP]                  [STOP]

                  ↓
      ┌───────────────────────┐
      │ BUY CANDIDATE         │
      │ All 8 criteria strong │
      └───────────┬───────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│ TIER 2: DEEP DIVE (BUY Candidates Only)         │
│                                                 │
│ Step 4: Historical Qualitative Analysis        │
│   - 5 years of MD&A (2020-2024)                │
│     → Does mgmt deliver on commitments?        │
│   - Proxy (DEF 14A)                            │
│     → Compensation, insider ownership          │
│   - Targeted web search                        │
│     → Acquisitions, strategic decisions        │
│                                                 │
│ Step 5: Validation with GuruFocus              │
│   - Cross-check mgmt claims with results       │
│   - Verify ROIC trends match narrative         │
│                                                 │
│ Step 6: Final Framework Assessment             │
│   - Score: Moat (/15), Mgmt (/12), Pred (/3)   │
│   - Calculate Margin of Safety (GuruFocus DCF) │
│   - Check ALL 8 BUY criteria                   │
└─────────────────┬───────────────────────────────┘
                  ↓
      ┌───────────┴───────────┐
      ↓                       ↓
┌─────────────┐         ┌─────────────┐
│ BUY         │         │ WATCH       │
│ (5-10%)     │         │             │
│             │         │ (Downgrade) │
│ ALL 8       │         │ Missing     │
│ criteria    │         │ some        │
│ pass        │         │ criteria    │
└─────────────┘         └─────────────┘
```

---

## Example: ZTS (Zoetis) Analysis

### Tier 1: Quick Screen

**Step 1: GuruFocus**
```
ROIC (10-year avg): 18.2% ✅ (>15%)
Debt/Equity: 0.52 ✅ (<0.7)
Owner Earnings: $1.8B (2024), growing 8% annually ✅
Margins: Gross 67%, Operating 37% ✅
```

**Step 2: Latest 10-K + Web Search**
```
Business: Animal health pharmaceuticals (understandable) ✅
Moat: Brand (Apoquel, Simparica), switching costs (vet relationships)
Moat Score: 11/15 (Narrow Moat)
Management Score: 9/12 (Good)
Predictability: 3/3 (High - stable animal health industry)
```

**Step 3: Decision → BUY Candidate (all criteria strong) → Proceed to Tier 2**

---

### Tier 2: Deep Dive

**Step 4: 5 Years of MD&A (2020-2024)**
```
2020: "Focus on key growth brands: Apoquel, Simparica Trio"
2021: "Apoquel sales +15%, Simparica Trio sales +45%"
2022: "Launched Librela for osteoarthritis pain"
2023: "Librela adoption exceeding expectations"
2024: "Continue portfolio expansion, margin improvement"

Management Consistency: HIGH ✅
Delivers on commitments: YES ✅
```

**Proxy (DEF 14A):**
```
CEO compensation: 300x median worker (reasonable) ✅
Insider ownership: CEO owns $50M+ stock ✅
Stock-based comp: 60% of total (long-term alignment) ✅
```

**Targeted Web Search:**
```
"ZTS Librela launch" → Strong adoption, positive vet feedback
"ZTS competitive position" → Market leader, 16% global share
"ZTS M&A strategy" → Disciplined, 3 tuck-in acquisitions, all accretive
```

**Step 5: Validation with GuruFocus**
```
Management said: "Margin improvement focus" (2024 MD&A)
GuruFocus shows: Operating margin 35% (2020) → 37% (2024) ✅

Management said: "Key brands growth" (2020-2024 MD&A)
GuruFocus shows: Revenue CAGR 9.2% (2020-2024) ✅
```

**Step 6: Final Framework Assessment**
```
Moat: 11/15 (Narrow but durable)
Management: 10/12 (Exceptional - delivers consistently)
Predictability: 3/3 (High)
ROIC: 18.2% (10-year avg) ✅
Owner Earnings: Growing 8% annually ✅
Margin of Safety: 22% (using GuruFocus DCF)

BUY Criteria Check:
1. Circle of Competence ✅
2. Wide Moat ❌ (11/15 is Narrow, not Wide)
3. Exceptional Management ✅
4. Margin of Safety ≥25% ❌ (22%, close but not quite)
5. High Predictability ✅
6. ROIC >20% ❌ (18.2%, good but not great)
7. Owner Earnings Growing ✅
8. Long-term Conviction ✅

DECISION: WATCH (not BUY)
Rationale: Good business with exceptional management, but:
- Narrow moat (11/15), not wide (12-15 required for BUY)
- Margin of safety 22% (need ≥25%)
- ROIC 18.2% (good, but BUY requires >20%)

Would consider BUY at $140/share (33% margin of safety)
```

---

## Testing and Validation

**Test File:** [test_zts_deep_dive.py](test_zts_deep_dive.py)

```python
"""
Complete Deep Dive Test: ZTS (Zoetis Inc.) - Tiered Analysis

Tests:
1. Tier 1: GuruFocus quantitative screen
2. Tier 1: Latest 10-K qualitative screen
3. Decision point: AVOID/WATCH → Stop, BUY candidate → Tier 2
4. Tier 2: 5 years of MD&A analysis
5. Tier 2: Proxy statement analysis
6. Validation: Single-pass with Munger's mental models
"""
```

**Expected Behavior:**
- Tier 1 completes in 3-5 minutes (~$1-2)
- If AVOID/WATCH → Stop
- If BUY candidate → Tier 2 continues (5-7 minutes total, ~$3-5)
- GuruFocus data used for all quantitative metrics (no manual calculations)
- 5 years of MD&A read (not full 10-Ks)

---

## Files Modified

### 1. Core Prompts
- **[src/agent/buffett_prompt.py](src/agent/buffett_prompt.py)** - Added tiered approach, GuruFocus-first strategy
  - Lines 568-612: TIERED ANALYSIS APPROACH
  - Lines 324-379: ANALYSIS APPROACH (tiered workflow)
  - Lines 652-703: TOOL USAGE STRATEGY (GuruFocus-first)

### 2. UI Components
- **[src/ui/components.py](src/ui/components.py)** - Updated deep dive progress description
  - Lines 76-91: Tiered analysis explanation for users

### 3. Documentation
- **[PHASE_9.1_TIERED_GURUFOCUS_FIRST.md](PHASE_9.1_TIERED_GURUFOCUS_FIRST.md)** - This document

---

## Summary

Phase 9.1 implements a **practical, cost-efficient, and accurate** tiered analysis approach:

### Quantitative Analysis:
- ✅ **GuruFocus-first** - Use verified data, avoid calculation errors
- ✅ **10-year track record** - ROIC, margins, Owner Earnings from GuruFocus

### Qualitative Analysis:
- ✅ **Tier 1:** Latest 10-K (full) + web search
- ✅ **Tier 2:** 5 years of MD&A + proxy + targeted web search
- ✅ **Historical perspective** without reading 10 full 10-Ks

### Decision Efficiency:
- ✅ **Early filtering** - AVOID/WATCH candidates stop at Tier 1
- ✅ **Deep conviction** - BUY candidates get Tier 2 deep dive
- ✅ **Cost controlled** - $1-2 (Tier 1), $3-5 (Tier 2)

**Authentic to Buffett's Actual Process:**
- Uses verified quantitative data (like Buffett relies on audited financials)
- Reads management's own words over time (MD&A reveals thinking)
- Focuses on historical track record (does management deliver?)
- Highly selective (BUY is rare, 5-10%)

---

**Phase 9.1 Complete** ✅

