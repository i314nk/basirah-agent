# Warren Buffett Analysis Workflow with Validator

**Complete Deep Dive Analysis Flow**
**Date:** November 18, 2025

---

## Overview

The analysis workflow has **3 main stages**:
1. **Data Collection** (Warren Agent calls tools)
2. **Analysis & Synthesis** (Warren Agent generates thesis)
3. **Validation & Refinement** (Validator Agent reviews and Warren Agent refines)

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                     │
│                   "Analyze LULU deep dive"                              │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 1: DATA COLLECTION                              │
│                      (Warren Agent)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ├─► STEP 1A: GuruFocus Tool
                             │   └─► Get: ROIC, margins, 10-year trends, ratios
                             │        Store in tool_cache
                             │
                             ├─► STEP 1B: SEC Filing Tool
                             │   └─► Get: Full 10-K (current year)
                             │        Store in tool_cache
                             │
                             ├─► STEP 1C: Web Search Tool (optional)
                             │   └─► Get: Recent news, moat validation, management
                             │        Store in tool_cache
                             │
                             ├─► STEP 1D: Calculator Tool
                             │   └─► Calculate: Owner Earnings, ROIC, DCF, MoS
                             │        Store in tool_cache
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               STAGE 2: CURRENT YEAR ANALYSIS                             │
│                      (Warren Agent)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ├─► Warren Agent processes ALL tool outputs
                             │
                             ├─► Phase 7.7.1: Data Extraction
                             │   └─► extract_gurufocus_metrics()
                             │   └─► extract_calculator_metrics()
                             │   └─► merge_metrics() → AnalysisMetrics
                             │        (Pydantic validates AUTOMATICALLY)
                             │
                             ├─► Warren Agent generates analysis text
                             │   └─► Business model
                             │   └─► Economic moat
                             │   └─► Financial strength
                             │   └─► Management quality
                             │   └─► Valuation
                             │
                             ├─► Phase 7.7.3: Insights Extraction
                             │   └─► _extract_insights_from_analysis()
                             │   └─► Creates AnalysisInsights (Pydantic)
                             │
                             ├─► Creates current_year_result:
                             │   {
                             │     "thesis": "...",
                             │     "decision": "BUY/WATCH/AVOID",
                             │     "conviction": "HIGH/MODERATE/LOW",
                             │     "metadata": {
                             │       "structured_metrics": {...},  # Phase 7.7
                             │       "structured_insights": {...}, # Phase 7.7
                             │       "tool_cache": {...}
                             │     }
                             │   }
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               STAGE 3: PRIOR YEARS ANALYSIS (if deep dive)               │
│                      (Warren Agent)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ├─► Determines years to analyze (5-10 years)
                             │
                             ├─► For EACH prior year:
                             │   ├─► STEP 3A: Get 10-K for that year (SEC tool)
                             │   ├─► STEP 3B: Get historical financials (GuruFocus)
                             │   ├─► STEP 3C: Extract metrics (Phase 7.7)
                             │   ├─► STEP 3D: Extract insights (Phase 7.7)
                             │   └─► Store year result
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               STAGE 4: FINAL SYNTHESIS                                   │
│                      (Warren Agent)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ├─► Combines current year + all prior years
                             │
                             ├─► Phase 7.7.4 (NOT IMPLEMENTED):
                             │   └─► Would pre-fetch all data
                             │   └─► Would optimize using structured metrics
                             │
                             ├─► Current behavior:
                             │   └─► Warren Agent synthesizes with all context
                             │   └─► May call tools if needed
                             │
                             ├─► Generates final thesis:
                             │   └─► Multi-year perspective
                             │   └─► Historical context
                             │   └─► Trend analysis
                             │   └─► Final BUY/WATCH/AVOID decision
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│         STAGE 5: VALIDATION (Iteration 0)                                │
│                   (Validator Agent)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ├─► Phase 7.7: Run Automated Checks FIRST
                             │   └─► run_all_validations(analysis_result)
                             │        ├─► validate_quantitative_claims()
                             │        │    └─► Check ROIC (0-200%)
                             │        │    └─► Check margins (net ≤ op ≤ gross)
                             │        │    └─► Check debt/equity (≥0)
                             │        │    └─► Check FCF vs Owner Earnings
                             │        │
                             │        ├─► validate_decision_consistency()
                             │        │    └─► BUY: Need ROIC >15%, MoS >20%, STRONG moat
                             │        │    └─► AVOID: Need clear red flags
                             │        │
                             │        ├─► validate_completeness()
                             │        │    └─► Check required metrics present
                             │        │    └─► Check required insights present
                             │        │
                             │        └─► validate_trend_claims()
                             │             └─► "rapid growth" → verify CAGR
                             │             └─► "expanding margins" → verify trend
                             │
                             ├─► Build Validator Prompt:
                             │   └─► get_validator_prompt(analysis, iteration=0, structured_validation)
                             │        ├─► Include automated check results
                             │        ├─► Include full analysis
                             │        └─► Include validation checklist
                             │
                             ├─► Validator Agent runs (with tools):
                             │   └─► Has web_search_tool (verify claims)
                             │   └─► Has calculator_tool (verify calculations)
                             │   └─► Reviews analysis quality
                             │   └─► Uses automated checks as starting point
                             │
                             ├─► Validator generates critique:
                             │   {
                             │     "approved": false,
                             │     "score": 65,  # /100
                             │     "overall_assessment": "...",
                             │     "strengths": ["...", "..."],
                             │     "issues": [
                             │       {
                             │         "severity": "CRITICAL",
                             │         "category": "methodology",
                             │         "issue": "ROIC calculation error",
                             │         "suggestion": "Recalculate using NOPAT..."
                             │       }
                             │     ],
                             │     "recommendation": "revise"
                             │   }
                             │
                             ▼
                      ┌──────┴──────┐
                      │ Score Check │
                      └──────┬──────┘
                             │
                  ┌──────────┴───────────┐
                  │                      │
          Score ≥ 80?              Score < 80?
                  │                      │
                  ▼                      ▼
         ┌────────────────┐    ┌────────────────────────┐
         │   APPROVED!    │    │  NEEDS REFINEMENT      │
         │   Return       │    │  Go to Stage 6         │
         │   analysis     │    └────────────────────────┘
         └────────────────┘              │
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│         STAGE 6: REFINEMENT (Iteration 1)                                │
│                   (Warren Agent)                                         │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ├─► Warren Agent receives critique
                             │
                             ├─► Filter to fixable issues:
                             │   └─► CRITICAL/MAJOR issues
                             │   └─► Excludes subjective/unfixable
                             │
                             ├─► VALIDATOR-DRIVEN REFINEMENT (NEW):
                             │   └─► Validator identifies issues AND fixes them
                             │   └─► Has access to all tools
                             │   └─► Can call GuruFocus, SEC, Calculator
                             │   └─► Directly updates analysis
                             │
                             ├─► OR ANALYST-DRIVEN REFINEMENT (OLD):
                             │   └─► Warren Agent gets critique
                             │   └─► Warren Agent refines specific issues
                             │   └─► Can call tools to get new data
                             │
                             ├─► Phase 7.7: Update structured data
                             │   └─► Re-extract metrics (Pydantic validates)
                             │   └─► Re-extract insights
                             │
                             ├─► Creates refined_result
                             │
                             ▼
                     Return to STAGE 5
                     (Validation Iteration 1)
                             │
                             ├─► Run automated checks again
                             ├─► Validator reviews again
                             ├─► New score (hopefully higher!)
                             │
                             ▼
                      ┌──────┴──────┐
                      │ Score Check │
                      └──────┬──────┘
                             │
                  ┌──────────┴───────────┐
                  │                      │
          Score ≥ 80?              Score < 80 AND
          OR                       iterations < 3?
          iterations ≥ 3?                 │
                  │                       │
                  ▼                       ▼
         ┌────────────────┐      Return to STAGE 6
         │   COMPLETE!    │      (Refinement Iteration 2)
         │   Return       │
         │   analysis     │
         └────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FINAL RESULT RETURNED                                 │
└─────────────────────────────────────────────────────────────────────────┘
                  │
                  ├─► Contains:
                  │   ├─► Final thesis
                  │   ├─► Decision: BUY/WATCH/AVOID
                  │   ├─► Conviction: HIGH/MODERATE/LOW
                  │   ├─► All validation history
                  │   ├─► Phase 7.7 structured_metrics
                  │   ├─► Phase 7.7 structured_insights
                  │   └─► Tool cache (all tool calls)
                  │
                  ▼
           Displayed to User
```

---

## Detailed Stage Breakdown

### STAGE 1: Data Collection (Warren Agent)

**Tools Available:**
1. **GuruFocus Tool** - Financial data API
2. **SEC Filing Tool** - Read 10-K, 10-Q, Proxy statements
3. **Web Search Tool** - Recent news, management changes
4. **Calculator Tool** - Financial calculations

**Warren Agent Process:**
```
User: "Analyze LULU"
  │
  ├─► Warren Agent thinks: "I need to analyze Lululemon"
  │
  ├─► Calls GuruFocus Tool:
  │    └─► Input: {ticker: "LULU", endpoint: "summary"}
  │    └─► Output: {roic: 0.32, revenue: 8800M, ...}
  │    └─► Stored in: tool_cache["gurufocus"]
  │
  ├─► Calls SEC Filing Tool:
  │    └─► Input: {ticker: "LULU", filing_type: "10-K", section: "full"}
  │    └─► Output: "...full 10-K text..."
  │    └─► Stored in: tool_cache["sec_10k_full"]
  │
  ├─► Calls Calculator Tool:
  │    └─► Input: {calc_type: "owner_earnings", ocf: 1200M, capex: 400M}
  │    └─► Output: {result: 800M, per_share: 6.25}
  │    └─► Stored in: tool_cache["calculator"]["owner_earnings"]
  │
  └─► Phase 7.7: Extracts structured data AUTOMATICALLY
       ├─► extract_gurufocus_metrics() → AnalysisMetrics
       │    └─► Pydantic validates: ROIC 0-500% ✓, margins 0-100% ✓
       └─► extract_calculator_metrics() → AnalysisMetrics
            └─► merge_metrics() combines both sources
```

**Key Phase 7.7 Feature:**
- Data is extracted into **Pydantic models** immediately
- Invalid data is **rejected automatically** (Bug #12 caught here!)
- Structured data stored alongside text analysis

---

### STAGE 2: Analysis (Warren Agent)

**Warren Agent generates text analysis:**
```
Warren Agent has:
  ├─► tool_cache (all tool outputs)
  ├─► structured_metrics (Pydantic validated)
  └─► Buffett personality prompt

Warren Agent writes:
  ├─► Business model analysis
  ├─► Economic moat assessment
  ├─► Financial strength evaluation
  ├─► Management quality review
  ├─► Valuation analysis
  └─► Investment decision

Phase 7.7 Enhancement:
  └─► _extract_insights_from_analysis()
       ├─► Reads Warren's text analysis
       ├─► Extracts decision/conviction/moat/risks
       └─► Creates AnalysisInsights (Pydantic)
            └─► Validates: decision ∈ {BUY,WATCH,AVOID} ✓
```

**Output: current_year_result**
```json
{
  "ticker": "LULU",
  "thesis": "Lululemon has built a powerful brand...",
  "decision": "BUY",
  "conviction": "HIGH",
  "metadata": {
    "structured_metrics": {
      "current_year": {
        "year": 2024,
        "metrics": {
          "roic": 0.32,
          "revenue": 8800.0,
          "operating_margin": 0.18,
          "debt_equity": 0.12,
          ...
        }
      }
    },
    "structured_insights": {
      "current_year": {
        "year": 2024,
        "insights": {
          "decision": "BUY",
          "conviction": "HIGH",
          "moat_rating": "STRONG",
          "risk_rating": "LOW"
        }
      }
    },
    "tool_cache": {
      "gurufocus": {...},
      "sec_10k_full": "...",
      "calculator": {...}
    }
  }
}
```

---

### STAGE 3: Prior Years Analysis (Warren Agent)

**Only for Deep Dive (not Quick Screen):**
```
For each year in [2023, 2022, 2021, 2020, 2019]:
  │
  ├─► Call SEC tool for that year's 10-K
  ├─► Call GuruFocus for historical financials
  ├─► Extract metrics (Phase 7.7)
  ├─► Extract insights (Phase 7.7)
  └─► Store year_result

Result: all_years = [2024, 2023, 2022, 2021, 2020, 2019]
```

---

### STAGE 4: Final Synthesis (Warren Agent)

**Current Behavior (Phase 7.7.4 NOT implemented):**
```
Warren Agent receives:
  ├─► current_year_result
  ├─► prior_years_results [2023, 2022, ...]
  └─► Full context window

Warren Agent synthesizes:
  ├─► Identifies multi-year trends
  ├─► Compares current vs historical
  ├─► Generates final investment thesis
  └─► May call tools if needed (NOT optimized yet)

Output: final_synthesis_result
```

**If Phase 7.7.4 was implemented:**
```
Would do:
  ├─► Pre-fetch ALL required data upfront
  ├─► Use structured_metrics from all years
  ├─► Build synthesis from structured data
  └─► NO tool calls during synthesis (faster!)
```

---

### STAGE 5: Validation (Validator Agent)

**Phase 7.7 NEW: Automated Checks FIRST**
```
STEP 1: Run Automated Checks
  │
  ├─► run_all_validations(final_result)
  │
  ├─► validate_quantitative_claims()
  │    ├─► ROIC: 32% → ✓ Within 0-200%
  │    ├─► Margins: Net 12% < Op 18% < Gross 55% → ✓
  │    └─► Debt/Equity: 0.12 → ✓ Non-negative
  │
  ├─► validate_decision_consistency()
  │    ├─► Decision: BUY
  │    ├─► Moat: STRONG → ✓ (BUY needs STRONG+)
  │    ├─► ROIC: 32% → ✓ (BUY needs >15%)
  │    ├─► MoS: 25% → ✓ (BUY needs >20%)
  │    └─► Conviction: HIGH → ✓ (BUY should have HIGH)
  │
  ├─► validate_completeness()
  │    └─► All required fields present → ✓
  │
  └─► validate_trend_claims()
       └─► Claims "strong revenue growth"
            └─► Check: 5-yr CAGR = 18% → ✓

Result: structured_validation = {
  "total_errors": 0,
  "total_warnings": 0,
  "overall_passed": true
}
```

**STEP 2: Build Validator Prompt**
```
get_validator_prompt(analysis, iteration=0, structured_validation)
  │
  ├─► Includes automated check results:
  │    """
  │    AUTOMATED QUANTITATIVE VALIDATION RESULTS:
  │    ✓ No errors found
  │    ✓ All decision consistency checks passed
  │    """
  │
  ├─► Includes full analysis text
  │
  └─► Includes validation checklist:
       - Business model clarity
       - Moat assessment rigor
       - Financial calculations correct
       - Valuation methodology sound
       - Sources cited
```

**STEP 3: Validator Agent Reviews**
```
Validator Agent:
  ├─► Sees automated validation results (Phase 7.7 NEW!)
  ├─► Reviews full analysis text
  ├─► Can call web_search_tool to verify claims
  ├─► Can call calculator_tool to verify calculations
  │
  └─► Generates critique:
       {
         "score": 85,
         "approved": true,
         "strengths": [
           "Clear moat identification",
           "Thorough financial analysis"
         ],
         "issues": [
           {
             "severity": "MINOR",
             "issue": "Could expand on management succession"
           }
         ]
       }
```

**STEP 4: Decision**
```
If score ≥ 80:
  └─► APPROVED! Return final analysis

If score < 80:
  └─► NEEDS REFINEMENT
       └─► Go to Stage 6
```

---

### STAGE 6: Refinement (Warren Agent)

**NEW: Validator-Driven Refinement**
```
Warren Agent receives critique:
  ├─► Score: 65/100
  ├─► Issues: [
  │     {
  │       "severity": "CRITICAL",
  │       "issue": "ROIC calculation appears incorrect",
  │       "suggestion": "Recalculate using NOPAT / Invested Capital"
  │     }
  │   ]
  │
  ├─► Filter to fixable issues
  │    └─► Only CRITICAL and MAJOR
  │
  └─► Two refinement modes:

MODE 1: Validator-Driven (NEW)
  └─► Validator Agent gets critique + tools
       ├─► Validator identifies: "ROIC needs recalculation"
       ├─► Validator calls calculator_tool:
       │    └─► Input: {calc_type: "roic", nopat: 810M, invested_capital: 2530M}
       │    └─► Output: {result: 0.32} (32% ROIC)
       ├─► Validator updates analysis directly
       └─► Returns refined_result

MODE 2: Analyst-Driven (OLD)
  └─► Warren Agent gets critique
       ├─► Reads issue: "ROIC calculation incorrect"
       ├─► Warren calls calculator_tool to recalculate
       ├─► Warren rewrites affected sections
       └─► Returns refined_result
```

**Phase 7.7: Update Structured Data**
```
After refinement:
  ├─► Re-extract metrics from refined analysis
  │    └─► Pydantic validates new ROIC: 0.32 → ✓
  │
  └─► Re-extract insights
       └─► Pydantic validates decision: "BUY" → ✓

Loop back to STAGE 5 (Validation Iteration 1)
```

---

## Maximum Iterations

**Default: 3 iterations**
```
Iteration 0: Initial validation
  └─► Score < 80 → Refine

Iteration 1: Re-validate after refinement 1
  └─► Score < 80 → Refine again

Iteration 2: Re-validate after refinement 2
  └─► Score < 80 OR ≥80 → STOP (max reached)

Result: Either approved OR max iterations reached
```

---

## Phase 7.7 Integration Points

**Phase 7.7.1 (Data Extraction):**
- Runs during STAGE 1 (Data Collection)
- Extracts GuruFocus data → AnalysisMetrics
- Extracts Calculator results → AnalysisMetrics
- **Pydantic validates immediately** (Bug #12 caught here!)

**Phase 7.7.2 (Multi-year Analysis):**
- Runs during STAGE 3 (Prior Years)
- Creates structured_metrics for each year
- Creates structured_insights for each year

**Phase 7.7.3 (Insights Extraction):**
- Runs during STAGE 2 (Analysis)
- Extracts decision/conviction/moat from text
- Creates AnalysisInsights (Pydantic validates)

**Phase 7.7.4 (Synthesis Optimization):**
- **NOT IMPLEMENTED YET**
- Would run during STAGE 4 (Synthesis)
- Would pre-fetch all data
- Would use structured metrics for synthesis

**Phase 7.7 Validator Enhancement (NEW):**
- Runs during STAGE 5 (Validation)
- Automated checks run BEFORE Validator Agent
- Results included in validator prompt
- Catches quantitative errors automatically

---

## Summary

**The Complete Flow:**
1. **Warren Agent** collects data (GuruFocus, SEC, Calculator)
2. **Phase 7.7** extracts structured data (Pydantic validates)
3. **Warren Agent** analyzes and generates thesis
4. **Phase 7.7** extracts insights from thesis
5. **Phase 7.7 Validator** runs automated checks
6. **Validator Agent** reviews analysis (with automated check results)
7. **If score < 80:** Warren Agent refines (can call tools)
8. **Repeat validation** up to 3 iterations
9. **Return final result** (approved or max iterations reached)

**Key Phase 7.7 Benefits:**
- ✅ Structured data extracted automatically
- ✅ Pydantic validation catches bugs immediately (Bug #12)
- ✅ Validator gets quantitative checks (ROIC, margins, decision consistency)
- ✅ Trend claims verified against historical data
- ❌ Synthesis NOT yet optimized (Phase 7.7.4 pending)

---

**Created:** November 18, 2025
**Status:** Phase 7.7.1-7.7.3 + Validator Enhancement COMPLETE
**Pending:** Phase 7.7.4 (Synthesis Optimization)
